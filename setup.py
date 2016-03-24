from setuptools import setup
import os
from fsdb import __version__


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as buf:
        return buf.read()

setup(
    name="Fsdb",
    version=__version__,
    packages=['fsdb'],

    author="Ael",
    author_email="tommy.ael@gmail.com",
    long_description=read('README.rst'),
    description=("File system database. Easily manage file storing"),
    keywords="database file storing db",
    url="https://github.com/ael-code/pyFsdb",
    license="LGPLv3",
    tests_require='nose',
    test_suite='nose.collector',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Topic :: Database",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ]
)
