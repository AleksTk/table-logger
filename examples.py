# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
import random
import math
from datetime import datetime

from table_logger import TableLogger


def print_simple():
    tpl = TableLogger(columns=['a', 'b', 'c', 'd'])
    tpl(1, 'Row1', datetime.now(), math.pi)
    tpl(2, 'Row2', datetime.now(), 1/3)
    tpl(3, 'Row3', datetime.now(), random.random())


def print_time_delta():
    tpl = TableLogger(columns=['data'], rownum=True, time_delta=True, 
                       timestamp=True)
    for e in 'abcde':
        time.sleep(random.randint(0, 3))
        tpl(e)


def print_file_info():
    """Prints file details in the current directory"""
    tpl = TableLogger(columns=['file', 'created', 'modified', 'size'])
    for f in os.listdir('.'):
        size = os.stat(f).st_size
        date_created = datetime.fromtimestamp(os.path.getctime(f))
        date_modified = datetime.fromtimestamp(os.path.getmtime(f))
        tpl(f, date_created, date_modified, size)


if __name__ == "__main__":
    print_simple()
    print_file_info()
    print_time_delta()
    