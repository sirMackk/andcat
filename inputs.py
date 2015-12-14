import re

from kivy.uix.textinput import TextInput


IPSUB = re.compile(r'[^0-9.]')
PORTSUB = re.compile(r'[^0-9]')


class AndCatTextInput(TextInput):
    def __init__(self, *args, **kwargs):
        self.edited = False
        super(AndCatTextInput, self).__init__(*args, **kwargs)

    def on_focus(self, instance, value):
        if value and not self.edited:
            self.edited = True
            self.placeholder = self.text
            self.text = ''
        elif value and self.text == self.placeholder:
            self.text = ''
        elif not value and self.text == '':
            self.text = self.placeholder


class AndCatIPInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = IPSUB.sub('', substring)
        return super(AndCatIPInput, self).insert_text(s, from_undo=from_undo)


class AndCatPortInput(AndCatTextInput):
    def insert_text(self, substring, from_undo=False):
        s = PORTSUB.sub('', substring)
        return super(AndCatPortInput, self).insert_text(s, from_undo=from_undo)
