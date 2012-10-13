from unittest import TestCase
from cStringIO import StringIO

from event import Event, serialize, unserialize


class EventTest(TestCase):
    def test_serialize(self):
        evt = Event()
        evt.channel = 'toto'
        evt.payload = "{'popo': 42}"
        buff = StringIO()
        serialize(evt, buff)
        print buff.read()
        buff.seek(0)
        buff.read(4)  # total size
        evt2 = unserialize(buff)
        print evt2.channel, evt2.payload
