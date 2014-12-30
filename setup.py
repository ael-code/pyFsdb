from setuptools import setup, find_packages

setup(
    name = "Fsdb",
    version = "0.2.4",
    packages=['fsdb'],

    author = "Ael",
    author_email = "tommy.ael@gmail.com",
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

