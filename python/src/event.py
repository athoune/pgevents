import struct


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
    csize, psize = struct.unpack('ii', reader.read(8))
    evt = Event()
    evt.channel = reader.read(csize)
    evt.payload = reader.read(psize)
    return evt
