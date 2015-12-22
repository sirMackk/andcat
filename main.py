from kivy import require
require('1.9.0')

__version__ = '0.0.3'

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout

from netcat import get_network_ip


kv_files = ('andcat', 'send_file', 'recv_file', 'about', )


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


class AndCatApp(App):
    def build(self):
        return ScreenMan()


if __name__ == '__main__':
    AndCatApp().run()
