from argparse import ArgumentParser

HOST = 'news.ycombinator.com/'
NEWS_COUNT = 30


def main():
    args = parse_args()
    pass


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-l', help='Log file')
    return parser.parse_args()


if __name__ == '__main__':
    main()

