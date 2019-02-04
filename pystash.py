from json import dumps
from time import sleep

from kivy.app import App
from kivy.clock import Clock
from kivy.config import ConfigParser
from kivy.uix.gridlayout import GridLayout
from kivy.uix.settings import SettingsWithSidebar

settings_config = {
    'auth': dumps([
        {
            "type": "bool",
            "section": "auth",
            "key": "uses_session_token",
            "title": "Use the Session Token instead?"
        }
    ])
}


class Root(GridLayout):

    def test(self):
        sleep(5)
        Clock.schedule_once(lambda dt: setattr(self.b_test, 'text', 'done'))
        sleep(1)
        Clock.schedule_once(lambda dt: setattr(self.b_test, 'text', 'test'))


class Pystash(App):

    def build(self):
        self.use_kivy_settings = False
        self.settings_cls = SettingsWithSidebar
        return Root()

    def build_settings(self, settings):
        self.config = ConfigParser()
        self.config.read(self.get_application_config())
        for sec in self.config.sections():
            settings.add_json_panel(sec, self.config, data=settings_config[sec])


if __name__ == '__main__':
    Pystash().run()
