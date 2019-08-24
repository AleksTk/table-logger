# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function

"""
TableLogger is a handy Python utility for logging tabular data into a console or a file.

Examples:
    
    Minimalistic example:
    
    >>> tbl = TableLogger()
    >>> tbl(1, 'Row1', datetime.now(), math.pi)
    >>> tbl(2, 'Row2', datetime.now(), 1/3)
    +----------------------+---------------------+----------------------+
    | Row1                 | 2015-12-29 13:04:47 |    3.141592653589793 |
    | Row2                 | 2015-12-29 13:04:47 |    0.333333333333333 |
    
    
    Print table header:
    
    >>> tbl = TableLogger(columns='name,age')
    >>> tbl('John Smith',  33)
    >>> tbl('Tommy Cash', 25)
    +----------------------+----------------------+
    | name                 |                  age |
    |----------------------+----------------------|
    | John Smith           |                   33 |
    | Tommy Cache          |                   25 |
    
    
    Include time-delta and timestamp columns:
    
    >>> tbl = TableLogger(columns='data', rownum=True, time_delta=True, timestamp=True)
    >>> for e in 'abcde':
    >>>     time.sleep(random.randint(0, 3))
    >>>     tbl(e)
    +-----------+----------------------------+-----------------+--------------+
    |       row | timestamp                  |      time delta | data         |
    |-----------+----------------------------+-----------------+--------------|
    |         1 | 2016-01-01 21:40:35.956815 |     0.000000000 | a            |
    |         2 | 2016-01-01 21:40:35.957315 |     0.000000000 | b            |
    |         3 | 2016-01-01 21:40:37.957569 |     2.000253916 | c            |
    |         4 | 2016-01-01 21:40:37.957569 |     0.000500202 | d            |
    |         5 | 2016-01-01 21:40:39.958323 |     2.000253916 | e            |
    
    
    Specify custom column widths and formatters:
    
    >>> tbl = TableLogger(columns='name,salary',
    >>>                   formatters={'salary': '{:,.2f}'.format},
    >>>                   colwidth={'name':12, 'salary':15})
    >>> tbl('John Smith',  1200000.890)
    >>> tbl('Tommy Cache',   70000.125)
    +--------------+-----------------+
    | name         |          salary |
    |--------------+-----------------|
    | John Smith   |    1,200,000.89 |
    | Tommy Cache  |       70,000.12 |

"""
import sys
import datetime
import csv
import io

import numpy as np

from . import fmt

PY2 = sys.version_info[0] == 2

try:
    basestring
except NameError:
    basestring = str

type2fmt = {
    # floats
    float: fmt.FloatFormatter,
    np.float: fmt.FloatFormatter,
    np.float32: fmt.FloatFormatter,
    np.float64: fmt.FloatFormatter,

    # int
    int: fmt.IntegerFormatter,
    np.int: fmt.IntegerFormatter,
    np.int16: fmt.IntegerFormatter,
    np.int32: fmt.IntegerFormatter,
    np.int64: fmt.IntegerFormatter,

    datetime.datetime: fmt.DatetimeFormatter,
    datetime.date: fmt.DateFormatter,
}


class TableLogger(object):
    """The main class for printing tabular data.
    
    Example:
        >>> tbl = TableLogger()
        >>> tbl(1, 'Row1', datetime.now(), math.pi)
        >>> tbl(2, 'Row2', datetime.now(),    1/3.)
    
    Args:
        time_delta (boolean): include a time delta column. Defaults to False.
        timestamp (boolean): include a timestamp column. Defaults to False.
        rownum (boolean): include a column with row numbers
        columns (list or str): a list of column names or a string of coma-delimited columns.
            If specified, a table header will be printed. Defaults to None.
        border (boolean): draw table borders. Defaults to True.
        csv (boolean): print output in csv format
        formatters (dict): (column-name -> string-format) custom column formatters. Defaults to None.
        float_format (callable): formatting function to apply to all float columns by default.
        colwidth (dict): (column-name -> width) custom column widths. Defaults to None.
        default_colwidth (int): default width for all columns.
        file (file object or str): File to open. Expects file object to be opened in binary writing mode 'wb'. Defaults to sys.stdout.
        encoding (unicode): Output encoding
    """

    def __init__(self,
                 time_delta=False,
                 timestamp=False,
                 rownum=False,
                 columns=None,
                 border=True,
                 csv=False,
                 formatters=None,
                 float_format=None,
                 colwidth=None,
                 default_colwidth=None,
                 file=None,
                 encoding='utf-8'
                 ):
        self.time_diff = time_delta
        self.timestamp = timestamp
        self.rownum = rownum
        self.border = border
        self.csv = csv
        self.column_formatters = formatters or {}
        self.float_format = float_format
        self.column_widths = colwidth or {}
        self.default_colwidth = default_colwidth
        self.encoding = encoding

        # set output file
        if file is None:
            if PY2:
                self.file = sys.stdout
            else:
                if hasattr(sys.stdout, 'buffer'):
                    self.file = sys.stdout.buffer
                else:
                    self.file = sys.stdout
        elif isinstance(file, basestring):
            self.file = open(file, 'wb')
        else:
            self.file = file

        # set column names
        if columns is None:
            self.columns = []
        elif isinstance(columns, list):
            self.columns = columns
        elif isinstance(columns, basestring):
            if len(columns) == 0:
                raise ValueError('Invalid "columns" argument')
            self.columns = columns.split(',')

        self.col_sep = ' '
        self.formatters = []

        if time_delta:
            self.columns.insert(0, 'time delta')
        if timestamp:
            self.columns.insert(0, 'timestamp')
        if rownum:
            self.columns.insert(0, 'row')

    def __call__(self, *args):
        """Prints a formatted row
        
        Args:
            args: row cells
        """
        if len(self.formatters) == 0:
            self.setup(*args)

        row_cells = []

        if self.rownum:
            row_cells.append(0)
        if self.timestamp:
            row_cells.append(datetime.datetime.now())
        if self.time_diff:
            row_cells.append(0)

        row_cells.extend(args)

        if len(row_cells) != len(self.formatters):
            raise ValueError('Expected number of columns is {}. Got {}.'.format(
                len(self.formatters), len(row_cells)))

        line = self.format_row(*row_cells)
        self.print_line(line)

    def format_row(self, *args):
        vals = [self.format_column(value, col) for col, value in enumerate(args)]
        row = self.join_row_items(*vals)
        return row

    def format_column(self, value, col):
        return self.formatters[col](value)

    def setup_formatters(self, *args):
        """Setup formatters by observing the first row.
        
        Args:
            *args: row cells
        """
        formatters = []
        col_offset = 0
        # initialize formatters for row-id, timestamp and time-diff columns
        if self.rownum:
            formatters.append(fmt.RowNumberFormatter.setup(0))
            col_offset += 1
        if self.timestamp:
            formatters.append(fmt.DatetimeFormatter.setup(
                datetime.datetime.now(),
                fmt='{:%Y-%m-%d %H:%M:%S.%f}'.format,
                col_width=26))
            col_offset += 1
        if self.time_diff:
            formatters.append(fmt.TimeDeltaFormatter.setup(0))
            col_offset += 1

        # initialize formatters for user-defined columns
        for coli, value in enumerate(args):
            fmt_class = type2fmt.get(type(value), fmt.GenericFormatter)
            kwargs = {}

            # set column width
            if self.default_colwidth is not None:
                kwargs['col_width'] = self.default_colwidth
            if coli in self.column_widths:
                kwargs['col_width'] = self.column_widths[coli]
            elif self.columns and self.columns[coli + col_offset] in self.column_widths:
                kwargs['col_width'] = self.column_widths[self.columns[coli + col_offset]]

            # set formatter function
            if fmt_class == fmt.FloatFormatter and self.float_format is not None:
                kwargs['fmt'] = self.float_format
            if coli in self.column_formatters:
                kwargs['fmt'] = self.column_formatters[coli]
            elif self.columns and self.columns[coli + col_offset] in self.column_formatters:
                kwargs['fmt'] = self.column_formatters[self.columns[coli + col_offset]]

            formatter = fmt_class.setup(value, **kwargs)
            formatters.append(formatter)

        self.formatters = formatters

    def setup(self, *args):
        """Do preparations before printing the first row
        
        Args:
            *args: first row cells 
        """
        self.setup_formatters(*args)
        if self.columns:
            self.print_header()
        elif self.border and not self.csv:
            self.print_line(self.make_horizontal_border())

    def print_header(self):
        col_names = []
        for coli, col_name in enumerate(self.columns):
            col_width = self.formatters[coli].col_width
            if len(col_name) > col_width:
                col_name = col_name[:col_width - 3] + '...'
            col_name = self.formatters[coli].just(col_name, col_width)
            col_names.append(col_name)

        header = self.join_row_items(*col_names)

        if self.csv:
            self.print_line(header)
        elif self.border:
            self.print_line(self.make_horizontal_border())
            self.print_line(header)
            self.print_line(self.make_horizontal_border('|'))
        else:
            self.print_line(header)

    def make_horizontal_border(self, corner='+'):
        border = '-+-'.join('-' * fmr.col_width for fmr in self.formatters)
        return u'{0}-{1}-{0}'.format(corner, border)

    def join_row_items(self, *args):
        if self.csv:
            row = self.csv_format(args)
        elif self.border:
            row = '| {} |'.format(' | '.join(args))
        else:
            row = '{}'.format(self.col_sep).join(args)
        return row

    def print_line(self, text):
        self.file.write(text.encode(self.encoding))
        self.file.write(b'\n')
        self.file.flush()

    def csv_format(self, row):
        """Converts row values into a csv line
        
        Args:
            row: a list of row cells as unicode
        Returns:
            csv_line (unicode)
        """
        if PY2:
            buf = io.BytesIO()
            csvwriter = csv.writer(buf)
            csvwriter.writerow([c.strip().encode(self.encoding) for c in row])
            csv_line = buf.getvalue().decode(self.encoding).rstrip()
        else:
            buf = io.StringIO()
            csvwriter = csv.writer(buf)
            csvwriter.writerow([c.strip() for c in row])
            csv_line = buf.getvalue().rstrip()
        return csv_line

    def close(self):
        """Closes underlying output file"""
        if self.file is not None:
            self.file.close()
