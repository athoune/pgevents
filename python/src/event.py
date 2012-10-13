import struct


class Event(object):
    payload = ""
    channel = ""
    timestamp = 0


def serialize(event, writer):
    csize = len(event.channel)
    psize = len(event.payload)
    tsize = psize + csize
    writer.write(struct.pack('ii', tsize, csize))
    writer.write(event.channel)
    writer.write(event.payload)


def unserialize(reader):
    csize = struct.unpack('i', reader.read(4))[0]
    evt = Event()
    evt.channel = reader.read(csize)
    evt.payload = reader.read()
    return evt
