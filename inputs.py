import re

from kivy.uix.textinput import TextInput


IPSUB = re.compile(r'[^0-9.]')
PORTSUB = re.compile(r'[^0-9]')


class AndCatTextInput(TextInput):
    pass


class AndCatIPInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = IPSUB.sub('', substring)
        return super(AndCatIPInput, self).insert_text(s, from_undo=from_undo)


class AndCatPortInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = PORTSUB.sub('', substring)
        return super(AndCatPortInput, self).insert_text(s, from_undo=from_undo)
