from os import path

from kivy.uix.filechooser import FileChooserListView

from popups import ProgressPopup
from netcat import Sender, SendingException, Receiver


class RecvFileChooser(FileChooserListView):
    # implement using only directories
    def recv_file(self, src_port, fname):
        popup = ProgressPopup(
            title='Receiving...',
            content='Sending {0}, {1}'.format(src_port, fname),
            size_hint=(0.3, 0.3,))

        dirpath = self.selection[0]
        fpath = path.join(dirpath, fname)
        receiver = Receiver(src_port, popup)
        try:
            receiver.receiveFile(fpath)
        except Exception as e:
            print 'receiver exception'
            print e


class SendFileChooser(FileChooserListView):
    # break out into own module
    def send_file(self, dest_ip, dest_port):
        progress_popup = ProgressPopup(
            title='Sending...',
            content='Preparing to send',
            size_hint=(0.5, 0.3))
        sender = Sender(dest_ip, dest_port, progress_popup)
        try:
            sender.sendFile(self.selection[0])
        except SendingException as e:
            pass
