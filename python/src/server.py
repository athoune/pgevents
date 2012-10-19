import select
import socket
import time
import os

from pistil.arbiter import Arbiter
from pistil.worker import Worker
from pistil.tcp.sync_worker import TcpSyncWorker
from pistil.tcp.arbiter import TcpArbiter
from pistil.util import parse_address, close

import psycopg2
import psycopg2.extensions

from event import Event, serialize, unserialize, SocketRW


class EventArbiter(TcpArbiter):
    def on_init(self, conf):
        TcpArbiter.on_init(self, conf)
        # we return a spec
        return (conf['event_worker'], 30, "worker", {}, "worker",)


class PgEventListener(Worker):
    def on_init(self, conf):
        self.conn = psycopg2.connect(conf['dsn'])
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        self.curs = self.conn.cursor()
        self.curs.execute("LISTEN test;")
        self.lastseen = 'epoch'
        self.address = parse_address(conf['address'])
        self.channel = conf['channel']
        self.fetch_events()  # Fetch old events.

    def fetch_events(self):
        self.curs.callproc('on_event', [self.channel, self.lastseen])
        for record in self.curs:
            self.lastseen = record[0]
            evt = Event()
            evt.channel = 'test'
            evt.payload = record[1]
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(self.address)
            serialize(evt, SocketRW(sock))
            close(sock)

    def handle(self):
        if select.select([self.conn], [], [], 5) == ([], [], []):
            # Timeout
            pass
        else:
            self.conn.poll()
            # It's for postgres < 9, without payload, so noftifies are just ONE
            # trigger
            self.fetch_events()
            while self.conn.notifies:
                self.conn.notifies.pop()


class EventWorker(TcpSyncWorker):
    def handle(self, sock, addr):
        #FIXME implement timeout
        evt = unserialize(SocketRW(sock))
        self.do_event(evt)
        close(sock)

    def do_event(self, event):
        raise NotImplementedError()

if __name__ == '__main__':
    af = "/tmp/pgevents.sock"
    try:
        os.remove(af)
    except Exception:
        pass

    class TestWorker(EventWorker):
        def do_event(self, evt):
            print "###### Event", self.pid, evt.channel, evt.payload
            time.sleep(1)

    conf = {"num_workers": 5,
            "address": "unix:%s" % af,
            "dsn": "dbname=pubsub",
            "channel": "test",
            "event_worker": TestWorker}

    specs = [
        (EventArbiter, 30, "supervisor", {}, "tcp_pool"),
        (PgEventListener, 30, "worker", {}, "listener"),
    ]

    arbiter = Arbiter(conf, specs)
    arbiter.run()
