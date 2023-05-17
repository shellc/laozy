import os
from pathlib import Path
from starlette.config import Config


class Settings(object):
    def __init__(self):
        self.home = os.getenv('LAOZY_HOME')

        if not self.home:
            self.home = os.path.join(Path.home(), '.laozy')

        if not os.path.exists(self.home):
            os.mkdir(self.home)

        f = os.path.join(self.home, 'settings.ini')
        self.settings = Config(f)

    def get(self, key: str, default=None):
        return self.settings(key=key, default=default)


instance = Settings()


def get(key: str, default=None):
    return instance.get(key, default)


def home():
    return instance.home
