import os.path
from time import sleep
import socket

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import protocol, reactor, defer

CHUNKSIZE = 1024


def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


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
    def __init__(self, ip, port):
        self.transport = None
        self.dest_ip = ip
        self.dest_port = int(port)
        self.filepath = None
        self.send = defer.Deferred()
        self.send.addCallback(self.on_connection)

    def on_connection(self, transport):
        self.transport = transport

        # pull out method
        if os.path.exists(self.filepath) and os.path.isfile(self.filepath):
            with open(self.filepath, 'rb') as f:
                while True:
                    chunk = f.read(CHUNKSIZE)
                    if chunk:
                        self.transport.write(chunk)
                    else:
                        break
        else:
            raise SendingException(
                'File does not exist at {}'.format(self.filepath))

        self.transport.loseConnection()

    def sendFile(self, filepath):
        self.filepath = filepath
        reactor.connectTCP(self.dest_ip, self.dest_port, SendFactory(self.send))


class Receiver(object):
    def __init__(self, port):
        self.transport = None
        self.src_port = int(port)
        self.filepath = None
        self.listener = None
        self.created = False
        self.data = []

        self.received = defer.Deferred()
        self.received.addCallback(self.transfer_done)

    def transfer_done(self, reason):
        # dont work with big files
        print reason
        self.listener.stopListening()
        print 'all done'
        # handle errors/bad connections

    def receiveFile(self, filepath):
        self.filepath = filepath

        def data_writer(data):
            # if not os.path.exists(self.filepath) or self.created:
            with open(self.filepath, 'ab') as f:
                f.write(data)

        self.listener = reactor.listenTCP(self.src_port, ReceiveFactory(data_writer, self.received))
