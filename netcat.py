import os.path
import os
import socket
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
        self.factory.on_connection(self.transport)


class SendFactory(protocol.ClientFactory):
    protocol = SendProto

    def __init__(self, on_connection, on_termination):
        self.on_connection = on_connection
        self.on_termination = on_termination

    def clientConnectionLost(self, conn, reason):
        self.on_termination(reason)
        print 'lost'

    def clientConnectionFailed(self, conn, failure):
        self.on_termination(failure)
        print 'failed'


class Sender(object):
    implements(interfaces.IPushProducer)

    def __init__(self, ip, port, progress_popup=None):
        self.dest_ip = ip
        self.dest_port = int(port)

        self._transport = None
        self._produced = 0
        self._paused = False

        self._progress = progress_popup

    def _onTermination(self, reason):
        # discern lost from failed
        print reason
        print dir(reason)
        self._finput.close()

        # all these ugly if statements
        if self._progress:
            self._progress.show_msg('failed or terminated (success?)')
            self._progress.show_exit()

    def _onConnection(self, transport):
        self._transport = transport
        self._transport.registerProducer(self, True)
        self.resumeProducing()

    def prepareFileForSending(self, filepath):
        self._finput = open(filepath, 'rb')
        self._count = os.fstat(self._finput.fileno()).st_size

    def sendFile(self, filepath):
        if self._progress:
            self._progress.open()
            self._progress.set_cancel(self.terminateProduction)
        try:
            self.prepareFileForSending(filepath)
        except IOError:
            self._produced.show_msg('Cannot open file', title='Error')

        reactor.connectTCP(
            self.dest_ip, self.dest_port,
            SendFactory(self._onConnection, self._onTermination))

    def pauseProducing(self):
        self._paused = True

    def resumeProducing(self):
        self._paused = False

        while not self._paused and self._produced < self._count:
            if self._progress:
                self._progress.update_msg(self._produced, self._count)
            self._transport.write(self._finput.read(CHUNKSIZE))
            self._produced += CHUNKSIZE

        if self._produced >= self._count:
            self.terminateProduction()

    def stopProducing(self):
        self._produced = self._count

    def terminateProduction(self, instance=None):
        self._transport.unregisterProducer()
        self._transport.loseConnection()


class ReceiveProto(protocol.Protocol):
    def dataReceived(self, data):
        self.factory.dataWriter(data)

    def connectionLost(self, reason):
        print 'losing connection'
        print reason
        self.factory.onDone('no reason')


class ReceiveFactory(protocol.Factory):
    protocol = ReceiveProto

    def __init__(self, dataWriter, onDone):
        print 'ready to recv'
        self.dataWriter = dataWriter
        self.onDone = onDone


class Receiver(object):
    def __init__(self, port, progress=None):
        self.srcPort = int(port)
        self.filepath = None
        self.receiver = None
        self._progress = progress
        self.bytes_received = 1.0

    def transferFinished(self, reason):
        if self._progress:
            self._progress.show_msg('Transfer finished')
            self._progress.show_exit()
        print reason
        self.receiver.stopListening()
        print 'all done'

    def receiveFile(self, filepath):
        self.filepath = filepath
        if self._progress:
            self._progress.open()

        def dataWriter(data):
            with open(self.filepath, 'ab') as f:
                self.bytes_received += len(data)
                if self._progress:
                    self._progress.update_msg(self.bytes_received)
                f.write(data)

        self.receiver = reactor.listenTCP(self.srcPort, ReceiveFactory(
            dataWriter, self.transferFinished))
