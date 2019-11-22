from app import App
import config
from helpers import read_websites


def main():
    websites = read_websites(config.WEBSITES_FILE)
    app = App(websites)
    app.start()


if __name__ == '__main__':
    main()
