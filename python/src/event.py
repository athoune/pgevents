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


class SocketRW(SocketReader):

    def write(self, stuff):
        print "Writing", stuff
        self._sock.sendall(stuff)
