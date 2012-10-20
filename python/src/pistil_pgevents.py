import select

from pistil.arbiter import Arbiter
from pistil.worker import Worker

import psycopg2
import psycopg2.extensions

from event import Event


class PgEventWorker(Worker):
    def on_init(self, conf):
        self.conn = psycopg2.connect(conf['dsn'])
        self.conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

        self.curs = self.conn.cursor()
        self.curs.execute("LISTEN test;")
        self.lastseen = 'epoch'
        self.channel = conf['channel']
        self.fetch_events()  # Fetch old events.

    def fetch_events(self):
        self.curs.callproc('on_event', [self.channel, self.lastseen])
        for record in self.curs:
            self.lastseen = record[0]
            evt = Event()
            evt.channel = 'test'
            evt.payload = record[1]
            self.on_event(evt)

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

    def on_event(self, evt):
        raise NotImplementedError()


if __name__ == '__main__':

    class TestWorker(PgEventWorker):
        def on_event(self, evt):
            print "###### Event", self.pid, evt.channel, evt.payload

    conf = {"dsn": "dbname=pubsub",
            "channel": "test",
            }

    specs = [
        (TestWorker, 30, "worker", {}, "listener"),
    ]

    arbiter = Arbiter(conf, specs)
    arbiter.run()
