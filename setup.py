# -*- coding: utf-8 -*-
import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "table-logger",
    version = "0.3",
    author = "Alexander Tkachenko",
    author_email = "alex.tk.fb@gmail.com",
    description = ("TableLogger is a handy Python utility for logging tabular"
                   " data into a console or a file."),
    license = "GNU GPL 2.0",
    keywords = ["tabular", "structured", "data", "console", "log"],
    url = "https://github.com/AleksTk/table-logger",
    download_url = 'https://github.com/AleksTk/table-logger/archive/v0.3.tar.gz',
    packages=['table_logger'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Logging",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
)
