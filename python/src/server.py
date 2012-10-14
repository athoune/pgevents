import select
import socket
import time

from pistil.arbiter import Arbiter
from pistil.worker import Worker
from pistil.tcp.sync_worker import TcpSyncWorker
from pistil.tcp.arbiter import TcpArbiter
from pistil.util import parse_address

import psycopg2
import psycopg2.extensions

from event import Event, serialize, unserialize


class EventArbiter(TcpArbiter):
    def on_init(self, conf):
        TcpArbiter.on_init(self, conf)
        # we return a spec
        print "Ready to listen"
        return (EventWorker, 30, "worker", {}, "event_handler",)


class PgEventListener(Worker):
    def on_init(self, conf):
        DSN = "dbname=pubsub"
        self.conn = psycopg2.connect(DSN)
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        self.curs = self.conn.cursor()
        self.curs.execute("LISTEN test;")
        self.lastseen = 'epoch'
        address = parse_address(conf['address'])
        time.sleep(1)
        print "Try to connect"
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(address)

    def handle(self):
        if select.select([self.conn], [], [], 5) == ([], [], []):
            print "Timeout"
        else:
            self.conn.poll()
            while self.conn.notifies:
                notify = self.conn.notifies.pop()
                print "Got NOTIFY:", notify.pid, notify.channel, notify.payload
                self.curs.callproc('on_event', ['test', self.lastseen])
                for record in self.curs:
                    self.lastseen = record[0]
                    evt = Event()
                    evt.channel = 'test'
                    evt.payload = record[1]
                    serialize(evt, SocketWrapper(self.socket))


class SocketWrapper(object):
    def __init__(self, socket):
        self.socket = socket

    def write(self, stuff):
        self.socket.sendall(stuff)

    def read(self, size):
        return self.socket.recv(size)


class EventWorker(TcpSyncWorker):
    def handle(self, sock, addr):
        evt = unserialize(SocketWrapper(sock))
        print evt.channel, evt.payload

if __name__ == '__main__':
    conf = {"num_workers": 3, "address": "unix:/tmp/pgevents.sock"}

    specs = [
        (EventArbiter, 30, "supervisor", {}, "tcp_pool"),
        (PgEventListener, 30, "worker", {}, "listener"),
    ]

    arbiter = Arbiter(conf, specs)
    arbiter.run()
