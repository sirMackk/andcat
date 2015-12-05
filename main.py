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
from kivy.uix.popup import Popup

from netcat import get_network_ip


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


#xtract into own modules
class AndCatIPInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = IPSUB.sub('', substring)
        return super(AndCatIPInput, self).insert_text(s, from_undo=from_undo)


class AndCatPortInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = PORTSUB.sub('', substring)
        return super(AndCatPortInput, self).insert_text(s, from_undo=from_undo)


class AndCatApp(App):
    def build(self):
        return ScreenMan()


if __name__ == '__main__':
    AndCatApp().run()
