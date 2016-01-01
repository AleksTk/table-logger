============
TableLogger
============

TableLogger is a handy Python utility for logging tabular data into a console or a text file.


Usage
-----
::

    from table_logger import TableLogger
    tpl = TableLogger(columns=['a', 'b', 'c', 'd'])
    
    tpl(1, 'Row1', datetime.now(), math.pi)
    tpl(2, 'Row2', datetime.now(), 1/3)
    tpl(3, 'Row3', datetime.now(), random.random())

Output::

    +----------------------+----------------------+---------------------+----------------------+
    |                    a | b                    | c                   |                    d |
    |----------------------+----------------------+---------------------+----------------------|
    |                    1 | Row1                 | 2015-12-28 21:13:46 |    3.141592653589793 |
    |                    2 | Row2                 | 2015-12-28 21:13:46 |    0.333333333333333 |
    |                    3 | Row3                 | 2015-12-28 21:13:46 |    0.854212894923849 |


Features
--------

* sane default formatting for basic python types: int, float, date and datetime
* row number, timestamp and time delta columns
* allows to adjust column width and format
* python 2.7 and 3.4 support


Installation
------------

PyPI::

    $ pip install table-logger

GitHub::
    
    $ git clone https://github.com/AleksTk/table-logger
    $ cd table-logger
    $ python setup.py install


More Examples
-------------

Include row number, time-delta and timestamp columns::

    tpl = TableLogger(columns=['data'], rownum=True, time_delta=True, timestamp=True)
    for e in 'abcde':
        time.sleep(random.randint(0, 3))
        tpl(e)

Output::

    +-----------+----------------------------+-----------------+----------------------+
    |       row | timestamp                  |      time delta | data                 |
    |-----------+----------------------------+-----------------+----------------------|
    |         1 | 2016-01-01 21:40:35.956815 |     0.000000000 | a                    |
    |         2 | 2016-01-01 21:40:35.957315 |     0.000000000 | b                    |
    |         3 | 2016-01-01 21:40:37.957569 |     2.000253916 | c                    |
    |         4 | 2016-01-01 21:40:37.957569 |     0.000500202 | d                    |
    |         5 | 2016-01-01 21:40:39.958323 |     2.000253916 | e                    |



Specify custom column widths and formatters::

    tpl = TableLogger(columns=['name', 'salary'],
                      column_formatters={1: '{:,.2f}'.format},
                      column_widths={0:12, 1:15})
    tpl('John Smith',  1200000.890)
    tpl('Tommy Cache',   70000.125)

Output::

    +--------------+-----------------+
    | name         |          salary |
    |--------------+-----------------|
    | John Smith   |    1,200,000.89 |
    | Tommy Cache  |       70,000.12 |
