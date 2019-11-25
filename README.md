# Stella

## About

Stella is a console program which monitors availability and performance of websites

## Setup

### Requirements

- Linux, MacOS or Windows.
- Python 3.7

This program uses the included _curses_ library. As the regular Windows Python distribution does not include the _curses_ library  used for the console dashboard, the _windows-curses_ library is required.

### Installation and running

To install from source in a virtualenv:

- python setup.py install
- Run `stella`

If you do not want to install the program, you can also call it by using `python main.py`

## Configuration

Modify the websites you would like to monitor in the `websites.conf` file.
Each line represents a website and check interval, separated by a space.

## Improvements

- Errors in parsing the `websites.conf` conf files are not handled. They would need to be improved to help the user identify where the error is in the file.
