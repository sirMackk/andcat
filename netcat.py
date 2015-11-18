import os.path
from time import sleep
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import protocol, reactor, defer

CHUNKSIZE = 1024


class SendingException(Exception):
    pass


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
