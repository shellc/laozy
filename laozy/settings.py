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
        if os.path.exists(f):
            self.settings = Config(f)
        else:
            self.settings = Config()

    def get(self, key: str, default=None):
        return self.settings(key=key, default=default)


instance = Settings()


def get(key: str, default=None):
    return instance.get(key, default)


def home():
    return instance.home


def get_bool(key: str, default=None) -> bool:
    v = get(key, default)
    return v is not None and v.lower() == 'true'
