from io import open
from sys import platform

from setuptools import setup

requirements = []

if platform == "win32":
    requirements.append('windows-curses')


setup(
    name="stella",
    version="1.0",
    install_requires=requirements,
    tests_require=["pytest", "mock"],
    packages=['stella'],
    author="James Barrios",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author_email="james@barrios.me",
    description="Console program which monitors availability and performance of websites",
    py_modules=['main', 'app', 'config'],
    entry_points={
        'console_scripts': [
            'stella = main:main',
        ],
    },
    project_urls={
        "Source Code": "https://github.com/Japillow/Stella",
    },
    test_suite="tests",
)
