from stella.app import App
from stella import config
from stella.helpers import read_websites


def main():
    websites = read_websites(config.WEBSITES_FILE)
    app = App(websites)
    app.start()


if __name__ == '__main__':
    main()
