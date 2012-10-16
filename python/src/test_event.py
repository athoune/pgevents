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
        buff.seek(0)
        evt2 = unserialize(buff)
        print evt2.channel, evt2.payload
        self.assertEqual('', buff.read())
        self.assertEqual(evt.channel, evt2.channel)
        self.assertEqual(evt.payload, evt2.payload)
