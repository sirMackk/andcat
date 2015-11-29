from os import path
import re

from kivy import require
require('1.9.0')

__version__ = '0.0.1'

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

from netcat import Sender, SendingException, Receiver, get_network_ip

kv_files = ('andcat', 'send_file', 'recv_file', 'http_server', 'about', )

IPSUB = re.compile(r'[^0-9.]')
PORTSUB = re.compile(r'[^0-9]')

for kv_file in kv_files:
    Builder.load_file(kv_file + '.kv')


class ScreenMan(ScreenManager):
    version = __version__


class AndCatBtn(Button):
    pass


class AndCatLabel(Label):
    pass


class AndCatIPLabel(Label):
    def get_own_ip(self):
        return get_network_ip()


class AndCatGrid(GridLayout):
    pass


class AndCatTextInput(TextInput):
    pass


class AndCatIPInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = IPSUB.sub('', substring)
        return super(AndCatIPInput, self).insert_text(s, from_undo=from_undo)

    def validate(self, text_input):
        print text_input


class AndCatPortInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = PORTSUB.sub('', substring)
        return super(AndCatPortInput, self).insert_text(s, from_undo=from_undo)



class SendFileChooser(FileChooserListView):
    # break out into own module
    def send_file(self, dest_ip, dest_port):
        popup = Popup(
            title='Sending...',
            content=Label(text='Sending {0}, {1}'.format(dest_ip, dest_port)),
            size_hint=(0.3, 0.3,))
        sender = Sender(dest_ip, dest_port, popup)
        try:
            sender.sendFile(self.selection[0])
        except SendingException as e:
            pass #popup!


class RecvFileChooser(FileChooserListView):
    # implement using only directories
    def recv_file(self, src_port, fname):
        popup = Popup(
            title='Receiving...',
            content=Label(text='Sending {0}, {1}'.format(src_port, fname)),
            size_hint=(0.3, 0.3,))

        dirpath = self.selection[0]
        fpath = path.join(dirpath, fname)
        receiver = Receiver(src_port, popup)
        try:
            receiver.receiveFile(fpath)
        except Exception as e:
            print 'receiver exception'
            print e


class AndCatApp(App):
    def build(self):
        return ScreenMan()


if __name__ == '__main__':
    AndCatApp().run()
