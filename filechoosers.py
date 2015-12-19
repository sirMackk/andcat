from os import path

from kivy.uix.filechooser import FileChooserListView

from popups import ProgressPopup
from netcat import Sender, Receiver, SendingException, ValidationError


class RecvFileChooser(FileChooserListView):
    # implement using only directories
    def recv_file(self, src_port, fname):
        popup = ProgressPopup(
            title='Receiving...',
            content='Receiving {0}, {1}'.format(src_port, fname),
            size_hint=(0.5, 0.3,))
        popup.open()

        dirpath = self.selection[0]
        fpath = path.join(dirpath, fname)
        try:
            receiver = Receiver(src_port, popup)
        except ValidationError as e:
            popup.show_err(e)
            return
        try:
            receiver.receiveFile(fpath)
        except Exception as e:
            print 'receiver exception'
            print e


class SendFileChooser(FileChooserListView):
    def send_file(self, dest_ip, dest_port):
        progress_popup = ProgressPopup(
            title='Sending...',
            content='Preparing to send',
            size_hint=(0.5, 0.3))
        progress_popup.open()

        try:
            sender = Sender(dest_ip, dest_port, progress_popup)
        except ValidationError as e:
            progress_popup.show_err(e)
            return

        try:
            sender.sendFile(self.selection[0])
        except SendingException as e:
            progress_popup.show_err(e)