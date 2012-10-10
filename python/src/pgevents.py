import select
import psycopg2
import psycopg2.extensions


def dispatcher(conn, cb):
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()
    curs.execute("LISTEN test;")

    print "Waiting for notifications on channel 'test'"
    lastseen = 'epoch'
    while 1:
        if select.select([conn], [], [], 5) == ([], [], []):
            print "Timeout"
        else:
            conn.poll()
            while conn.notifies:
                notify = conn.notifies.pop()
                print "Got NOTIFY:", notify.pid, notify.channel, notify.payload
                curs.callproc('on_event', ['test', lastseen])
                for record in curs:
                    lastseen = record[0]
                    cb(0, record)

if __name__ == '__main__':
    def _notify(ts, payload):
        print payload

    DSN = "dbname=pubsub"
    conn = psycopg2.connect(DSN)
    dispatcher(conn, _notify)
