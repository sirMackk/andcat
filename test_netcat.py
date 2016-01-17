from StringIO import StringIO

import mock
from twisted.test import proto_helpers
from twisted.trial import unittest

from netcat import ReceiveFactory, Receiver


class ReceiverTest(unittest.TestCase):
    def setUp(self):
        self.buff = StringIO()
        self.msg = StringIO()

        def dataWriter(data):
            self.buff.write(data)

        def transferFinished(msg):
            self.msg.write(msg)

        self.factory = ReceiveFactory(dataWriter, transferFinished)
        self.proto = self.factory.buildProtocol(('localhost', 0,))
        self.transport = proto_helpers.StringTransportWithDisconnection()
        self.transport.protocol = self.proto
        self.proto.makeConnection(self.transport)

    def test_successful_transfer(self):
        self.proto.dataReceived('SomeData\r\n')
        self.assertEqual(self.buff.getvalue(), 'SomeData\r\n')

    def test_connectionLost(self):
        self.proto.dataReceived('SomeData\r\n')
        self.transport.loseConnection()
        self.assertTrue(self.msg.getvalue(), 'Transfer finished successfully!')
