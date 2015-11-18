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

from netcat import Sender, SendingException

kv_files = ('send_file', 'recv_file', 'http_server', 'about',)

for kv_file in kv_files:
    Builder.load_file(kv_file + '.kv')


class ScreenMan(ScreenManager):
    version = __version__


class AndCatBtn(Button):
    pass


class AndCatLabel(Label):
    pass


class AndCatGrid(GridLayout):
    pass


class AndCatTextInput(TextInput):
    pass


class SendFileChooser(FileChooserListView):
    # break out into own module
    def send_file(self, dest_ip, dest_port):
        # this should create another object that encompasses sending logic (ie. reactor, protocol, etc)
        print dest_ip
        print dest_port
        print self.selection[0]
        sender = Sender(dest_ip, dest_port)
        try:
            sender.sendFile(self.selection[0])
        except SendingException as e:
            pass #popup!

class RecvFileChooser(FileChooserListView):
    # implement using only directories
    pass


class AndCatApp(App):
    def build(self):
        return ScreenMan()


if __name__ == '__main__':
    AndCatApp().run()
