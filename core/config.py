import types


class Config(dict):

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or {})

    def from_file(self, filename):
        config = types.ModuleType('config')
        config.__file__ = filename
        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), config.__dict__)
        except IOError as e:
            e.strerror = 'Не удается загрузить файл конфигурации {}'.format(e.strerror)
            raise
        self.set_config(config)

    def set_config(self, config):
        for key in dir(config):
            if key.isupper():
                self[key] = getattr(config, key)