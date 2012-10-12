from pistil.arbiter import Arbiter
from pistil.worker import Worker
from pistil.tcp.sync_worker import TcpSyncWorker
from pistil.tcp.arbiter import TcpArbiter


class EventArbiter(TcpArbiter):
    def on_init(self, conf):
        TcpArbiter.on_init(self, conf)
        # we return a spec
        return (EventWorker, 30, "worker", {}, "event_handler",)


class EventListener(Worker):
    def handle(self):
        pass


class EventWorker(TcpSyncWorker):
    def handle(self, sock, addr):
        pass


if __name__ == '__main__':
    conf = {"num_workers": 3, "address": "unix:/tmp/pgevents.sock"}

    specs = [
        (EventArbiter, 30, "supervisor", {}, "tcp_pool"),
        (EventListener, 30, "worker", {}, "listener")
    ]

    arbiter = Arbiter(conf, specs)
    arbiter.run()
