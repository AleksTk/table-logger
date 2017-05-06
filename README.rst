============
TableLogger
============

TableLogger is a handy Python utility for logging tabular data into a console 
or a text file with little overhead.


Usage
-----
.. code-block:: python

    from table_logger import TableLogger
    tbl = TableLogger(columns='a,b,c,d'])
    
    tbl(1, 'Row1', datetime.now(), math.pi)
    tbl(2, 'Row2', datetime.now(), 1/3)
    tbl(3, 'Row3', datetime.now(), random.random())

Output::

    +----------------------+----------------------+---------------------+----------------------+
    |                    a | b                    | c                   |                    d |
    |----------------------+----------------------+---------------------+----------------------|
    |                    1 | Row1                 | 2015-12-28 21:13:46 |    3.141592653589793 |
    |                    2 | Row2                 | 2015-12-28 21:13:46 |    0.333333333333333 |
    |                    3 | Row3                 | 2015-12-28 21:13:46 |    0.854212894923849 |


Features
--------

* sane default formatting for basic python types
* row number, timestamp and time delta columns
* csv output
* allows to adjust column width and format
* python 2.7 and 3 support


Installation
------------

PyPI::

    $ pip install table-logger

GitHub::
    
    $ git clone https://github.com/AleksTk/table-logger
    $ cd table-logger
    $ python setup.py install


Examples
--------

Include row number, time-delta and timestamp columns

.. code-block:: python

    tbl = TableLogger(columns='data', rownum=True, time_delta=True, timestamp=True)
    for e in 'abcde':
        time.sleep(random.randint(0, 3))
        tbl(e)

Output::

    +-----------+----------------------------+-----------------+----------------------+
    |       row | timestamp                  |      time delta | data                 |
    |-----------+----------------------------+-----------------+----------------------|
    |         1 | 2016-01-01 21:40:35.956815 |     0.000000000 | a                    |
    |         2 | 2016-01-01 21:40:35.957315 |     0.000000000 | b                    |
    |         3 | 2016-01-01 21:40:37.957569 |     2.000253916 | c                    |
    |         4 | 2016-01-01 21:40:37.957569 |     0.000500202 | d                    |
    |         5 | 2016-01-01 21:40:39.958323 |     2.000253916 | e                    |



Write to csv file

.. code-block:: python

     with open('log.csv', 'w') as csvfile:
        tbl = TableLogger(file=csvfile, csv=True, columns='a,b'])
        tbl('John "Smith"',  1200000.890)
        tbl('Tommy,Cache',   70000.125)

Output::

    a,b
    "John ""Smith""",1200000.890000
    "Tommy,Cache",70000.125000



Specify custom column widths and formatters

.. code-block:: python

    tbl = TableLogger(columns='name,salary',
                      formatters={'salary': '{:,.2f}'.format},
                      colwidth={'name':12, 'salary':15})
    tbl('John Smith',  1200000.890)
    tbl('Tommy Cache',   70000.125)

Output::

    +--------------+-----------------+
    | name         |          salary |
    |--------------+-----------------|
    | John Smith   |    1,200,000.89 |
    | Tommy Cache  |       70,000.12 |
