import struct
from http_parser.reader import SocketReader


class Event(object):
    payload = ""
    channel = ""
    timestamp = 0


def serialize(event, writer):
    csize = len(event.channel)
    psize = len(event.payload)
    writer.write(struct.pack('ii', csize, psize))
    writer.write(event.channel)
    writer.write(event.payload)


def unserialize(reader):
    buff = reader.read(8)
    print "Buff", len(buff), buff
    csize, psize = struct.unpack('ii', buff)
    print "csize, psize", csize, psize
    evt = Event()
    evt.channel = reader.read(csize)
    evt.payload = reader.read(psize)
    return evt


WAITING_FOR_SIZE = 1
WAITING_FOR_CHANNEL = 2
WAITING_FOR_PAYLOAD = 3


class SocketReader(object):

    def __init__(self, socket):
        self.socket = socket
        self.es = EventStream()

    def __iter__(self):
        tmp = self.socket.recv(self.es.size_needed())
        self.es.feed(tmp)
        if self.es.payload is not None:
            yield self.es
            self.es = EventStream()


class EventStream(object):

    def __init__(self):
        self._buff = ""
        self._state = WAITING_FOR_SIZE
        self.required_size = 8
        self.channel = None
        self.payload = None

    def size_needed(self):
        return self.required_size - len(self._buff)

    def feed(self, chunk):
        self._buff += chunk
        if len(self._buff) < self.required_size:
            return
        buff = self._buff[:self.required_size]
        self._buff = self._buff[self.required_size:]
        if self._state == WAITING_FOR_SIZE:
            self.csize, self.psize = struct.unpack('ii', buff)
            self.required_size = self.csize
        elif self._state == WAITING_FOR_CHANNEL:
            self.channel = buff
            self.required_size = self.psize
        elif self._state == WAITING_FOR_PAYLOAD:
            self.payload = buff
        else:
            raise Exception('Wrong state.')


class SocketRW(object):

    def __init__(self, socket):
        self.socket = socket

    def read(self, size):
        buff = []
        total = size
        while total:
            try:
                tmp = self.socket.recv(total)
                buff.append(tmp)
                total -= len(tmp)
            except Exception as e:
                print "AAAAAAAAAAAAAAHHHHHHHHH", e
        resp = ''.join(buff)
        return resp

    def write(self, stuff):
        self.socket.sendall(stuff)

    def close(self):
        pass
