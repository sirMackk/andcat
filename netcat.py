import os.path
import os
from time import sleep
import socket
from datetime import datetime
from zope.interface import implements

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import protocol, reactor, defer, interfaces

CHUNKSIZE = 1024


def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


class SendProducer(object):
    implements(interfaces.IPushProducer)

    def __init__(self, transport, finput, popup=None):
        self._transport = transport
        self._popup = popup
        self._finput = finput
        self._count = os.fstat(finput.fileno()).st_size
        self._produced = 0
        self._started = datetime.now()
        self._paused = False

        self._popup.open()

    def pauseProducing(self):
        self._paused = True

    def resumeProducing(self):
        self._paused = False

        while not self._paused and self._produced < self._count:
            percent_done = (self._produced / float(self._count)) * 100
            avg_speed = (self._produced / (datetime.now() - self._started
                                           ).total_seconds()) / 1024 / 1024
            self._popup.content.text = 'Sent: {0:.2f}% - {1:.2f} MB/s'.format(
                percent_done, avg_speed)
            self._transport.write(self._finput.read(CHUNKSIZE))
            self._produced += CHUNKSIZE

        if self._produced >= self._count:
            self._transport.unregisterProducer()
            self._transport.loseConnection()
            # this should be in a 'finally' 
            self._finput.close()
            self._popup.dismiss()

    def stopProducing(self):
        self._produced = self._count


class SendingException(Exception):
    pass


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


class SendProto(protocol.Protocol):
    def connectionMade(self):
        print 'connectionMade!'
        # self.factory.sender.on_connection(self.transport)
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
    # make into context manager?
    # all this is done with call backs
    # how about switched to deferreds?
    def __init__(self, ip, port, progress_popup=None):
        self.transport = None
        self.dest_ip = ip
        self.dest_port = int(port)
        self.filepath = None
        self.popup = progress_popup
        self.send = defer.Deferred()
        self.send.addCallback(self.on_connection)

    def on_connection(self, transport):
        self.transport = transport

        f = open(self.filepath, 'rb')
        producer = SendProducer(transport, f, self.popup)
        transport.registerProducer(producer, True)
        producer.resumeProducing()

    def sendFile(self, filepath):
        self.filepath = filepath
        reactor.connectTCP(self.dest_ip, self.dest_port, SendFactory(self.send))


class Receiver(object):
    def __init__(self, port, popup=None):
        self.transport = None
        self.src_port = int(port)
        self.filepath = None
        self.listener = None
        self.created = False
        self.popup = popup
        self.data = []
        self.bytes_recved = 1.0
        self.started = datetime.now()

        self.received = defer.Deferred()
        self.received.addCallback(self.transfer_done)

        self.popup.open()

    def transfer_done(self, reason):
        print reason
        self.listener.stopListening()
        self.popup.dismiss()
        print 'all done'
        # handle errors/bad connections

    def receiveFile(self, filepath):
        self.filepath = filepath

        def data_writer(data):
            # if not os.path.exists(self.filepath) or self.created:
            with open(self.filepath, 'ab') as f:
                self.bytes_recved += len(data)
                megab = self.bytes_recved / 1024 / 1024
                speed = megab / (datetime.now() - self.started
                         ).total_seconds()
                self.popup.content.text = '{0:.2f}MB - {1:.2f} MB/s'.format(megab,
                                                                     speed)
                f.write(data)

        self.listener = reactor.listenTCP(self.src_port, ReceiveFactory(data_writer, self.received))
