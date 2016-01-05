from kivy import require
require('1.9.0')

__version__ = '0.0.5'

from kivy.lang import Builder
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.image import Image

from netcat import get_network_ip


ABOUT = """
AndCat - netcat for Android
Version: {version}
Author: Matt / github.com/sirmackk
Logo credits: Iconka - https://www.iconfinder.com/icons/182515/cat_tied_yarn_icon

License: GPLv2
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
"""
kv_files = ('andcat', 'send_file', 'recv_file', 'about',)



for kv_file in kv_files:
    Builder.load_file(kv_file + '.kv')


class ScreenMan(ScreenManager):
    version = __version__
    about = ABOUT


class AndCatBtn(Button):
    pass


class AndCatLabel(Label):
    pass


class AndCatLogo(GridLayout):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('cols', 2)
        kwargs.setdefault('rows', 1)
        self.size_hint = (1, None,)
        self.height = 50

        super(self.__class__, self).__init__(*args, **kwargs)
        self.create_and_add_widgets(kwargs.get('screen', ''))

    def create_and_add_widgets(self, screen_label=''):
        main_label = AndCatLabel(text='AndCat',
                                 size_hint=(1.0, None,),
                                 height=50)
        logo_container = AnchorLayout(anchor_x='right')
        logo_img = Image(source='logo.png', size_hint=(None, None,), width=50, height=50)

        logo_container.add_widget(logo_img)
        self.add_widget(main_label)
        self.add_widget(logo_container)


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
