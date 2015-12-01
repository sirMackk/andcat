import os.path
import os
import socket
from datetime import datetime
from zope.interface import implements

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import protocol, reactor, defer, interfaces

CHUNKSIZE = 1024


class SendingException(Exception):
    pass


def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


class SendProto(protocol.Protocol):
    def connectionMade(self):
        print 'connectionMade!'
        self.factory.sender.callback(self.transport)


class SendFactory(protocol.ClientFactory):
    protocol = SendProto

    def __init__(self, sender):
        self.sender = sender

    def clientConnectionLost(self, conn, reason):
        print 'lost'
        # reactor.stop()

    def clientConnectionFailed(self, conn, failure):
        print 'failed'
        pass
        # reactor.stop()


class Sender(object):
    implements(interfaces.IPushProducer)
    # open file
    # send file w/ rate limiting (producer)
    # update progress widget

    def __init__(self, ip, port, progress_popup=None):
        self.dest_ip = ip
        self.dest_port = int(port)

        self._transport = None
        self._produced = 0
        self._paused = False

        self._progress = progress_popup

        self.send = defer.Deferred()
        self.send.addCallback(self.on_connection)

    def on_connection(self, transport):
        self.transport = transport
        self.transport.registerProducer(self, True)
        self.resumeProducing()

    def sendFile(self, filepath):
        self._progress.open()

        # try catch or move to _init_ or own func
        self._finput = open(filepath, 'rb')
        self._count = os.fstat(self._finput.fileno()).st_size

        reactor.connectTCP(self.dest_ip, self.dest_port, SendFactory(self.send))

    def pauseProducing(self):
        self._paused = True

    def resumeProducing(self):
        self._paused = False

        while not self._paused and self._produced < self._count:
            self._progress.update(self._produced, self._count)
            self._transport.write(self._finput.read(CHUNKSIZE))
            self._produced += CHUNKSIZE

        if self._produced >= self._count:
            self._transport.unregisterProducer()
            self._transport.loseConnection()
            # this should be in a 'finally' or deferred?
            self._finput.close()
            self._progress.dismiss()

    def stopProducing(self):
        self._produced = self._count


class ReceiveProto(protocol.Protocol):
    def dataReceived(self, data):
        self.factory.data_writer(data)

    def connectionLost(self, reason):
        print 'losing connection'
        print self.factory.received
        print reason
        # self.factory.received.callback(reason)
        self.factory.received.callback('no reason')


class ReceiveFactory(protocol.Factory):
    protocol = ReceiveProto

    def __init__(self, data_writer, received):
        print 'ready to recv'
        self.data_writer = data_writer
        self.received = received


class Receiver(object):
    def __init__(self, port, progress=None):
        self.transport = None
        self.src_port = int(port)
        self.filepath = None
        self.listener = None
        self.created = False
        self._progress = progress
        self.data = []
        self.bytes_recved = 1.0

        self.received = defer.Deferred()
        self.received.addCallback(self.transfer_done)

        self._progress.open()

    def transfer_done(self, reason):
        print reason
        self.listener.stopListening()
        self._progress.dismiss()
        print 'all done'
        # handle errors/bad connections

    def receiveFile(self, filepath):
        self.filepath = filepath

        def data_writer(data):
            # if not os.path.exists(self.filepath) or self.created:
            with open(self.filepath, 'ab') as f:
                self.bytes_recved += len(data)
                self._progress.update(self.bytes_recved)
                f.write(data)

        self.listener = reactor.listenTCP(self.src_port, ReceiveFactory(data_writer, self.received))
