from setuptools import setup, find_packages
import os

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()

setup(
    name = "Fsdb",
    version = "0.3.1",
    packages=['fsdb'],

    author = "Ael",
    author_email = "tommy.ael@gmail.com",
    long_description=read('README.rst'),
    description = ("File system database. Easily manage file storing"),
    keywords = "database file storing db",
    url = "https://github.com/ael-code/pyFsdb",
    license = "LGPLv3",
    test_suite='tests',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Topic :: Database",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only"
    ]
)

