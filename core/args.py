from argparse import ArgumentParser


class Args:

    def __init__(self):
        parser = ArgumentParser()
        parser.add_argument('-c', '--config')

        self.args = parser.parse_args()

    def __getattr__(self, item):
        return getattr(self.args, item)