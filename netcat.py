import os.path
import os
import socket
import re
from zope.interface import implements

from kivy.support import install_twisted_reactor
install_twisted_reactor()

from twisted.internet import protocol, reactor, defer, interfaces, error

CHUNKSIZE = 1024
IP_VALIDATOR = re.compile(
                (r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25'
                 '[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4]'
                 '[0-9]|25[0-5])$'))


class SendingException(Exception):
    pass


class ValidationError(Exception):
    pass


def validate_ip(ip):
    """
    Uses regex to validate ip address. Raises ValidationError.
    :ip: string representing a valid IP address.
    :return: None
    """
    if not IP_VALIDATOR.match(ip):
        raise ValidationError('Please provide a valid IP address')


def validate_port(port):
    """
    Validates if a port is between 1024 and 65535. Raises Validation Error.
    :port: String or int representing a port.
    :return: None
    """
    try:
        port = int(port)
    except ValueError:
        raise ValidationError('A port can only be composed of numbers')

    if port < 1024 or port > 65535:
        raise ValidationError('Must specify a port between 1024 and 65535')
    


def get_network_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('<broadcast>', 0))
    return s.getsockname()[0]


class SendProto(protocol.Protocol):
    def connectionMade(self):
        self.factory.on_connection(self.transport)


class SendFactory(protocol.ClientFactory):
    protocol = SendProto

    def __init__(self, on_connection, on_termination):
        self.on_connection = on_connection
        self.on_termination = on_termination

    def clientConnectionLost(self, conn, reason):
        self.on_termination(reason)

    def clientConnectionFailed(self, conn, failure):
        self.on_termination(failure)


class Sender(object):
    implements(interfaces.IPushProducer)

    def __init__(self, ip, port, progress_popup=None):
        validate_ip(ip)
        validate_port(port)

        self.dest_ip = ip
        self.dest_port = int(port)

        self._transport = None
        self._produced = 0
        self._paused = False

        self._progress = progress_popup

    def _onTermination(self, reason):
        self._finput.close()

        if self._progress:
            if reason.check(error.ConnectionDone):
                msg = "Transfer finished!"
            else:
                msg = "Possible problem with the transfer".format(reason.value)
            self._progress.show_msg(msg)
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
            self._progress.set_cancel(self.terminateProduction)
        try:
            self.prepareFileForSending(filepath)
        except IOError:
            self._produced.show_err('Cannot open file')

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
        if reason.check(error.ConnectionDone):
            msg = 'Transfer finished sucessfully!'
        else:
            msg = 'Error while receiving file: {}'.format(reason.value)

        self.factory.onDone(msg)


class ReceiveFactory(protocol.Factory):
    protocol = ReceiveProto

    def __init__(self, dataWriter, onDone):
        self.dataWriter = dataWriter
        self.onDone = onDone


class Receiver(object):
    def __init__(self, port, progress=None):
        validate_port(port)
        # validate directory, filename
        self.srcPort = int(port)
        self.filepath = None
        self.receiver = None
        self._progress = progress
        self.bytes_received = 1.0

    def transferFinished(self, msg):
        if self._progress:
            self._progress.show_msg(msg)
            self._progress.show_exit()
        self.receiver.stopListening()

    def receiveFile(self, filepath):
        self.filepath = filepath

        def dataWriter(data):
            with open(self.filepath, 'ab') as f:
                self.bytes_received += len(data)
                if self._progress:
                    self._progress.update_msg(self.bytes_received)
                f.write(data)

        self.receiver = reactor.listenTCP(self.srcPort, ReceiveFactory(
            dataWriter, self.transferFinished))
