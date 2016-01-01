# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
TableLogger is a handy Python utility for logging tabular data into a console or a file.

Examples:
    
    Minimalistic example:
    
    >>> tpr = TableLogger()
    >>> tpr(1, 'Row1', datetime.now(), math.pi)
    >>> tpr(2, 'Row2', datetime.now(), 1/3)
    +----------------------+---------------------+----------------------+
    | Row1                 | 2015-12-29 13:04:47 |    3.141592653589793 |
    | Row2                 | 2015-12-29 13:04:47 |    0.333333333333333 |
    
    
    Print table header:
    
    >>> tpr = TableLogger(columns=['name', 'age'])
    >>> tpr('John Smith',  33)
    >>> tpr('Tommy Cash', 25)
    +----------------------+----------------------+
    | name                 |                  age |
    |----------------------+----------------------|
    | John Smith           |                   33 |
    | Tommy Cache          |                   25 |
    
    
    Include time-delta and timestamp columns:
    
    >>> tpr = TableLogger(columns=['data'], rownum=True, time_delta=True, timestamp=True)
    >>> for e in 'abcde':
    >>>     time.sleep(random.randint(0, 3))
    >>>     tpr(e)
    +-----------+----------------------------+-----------------+--------------+
    |       row | timestamp                  |      time delta | data         |
    |-----------+----------------------------+-----------------+--------------|
    |         1 | 2016-01-01 21:40:35.956815 |     0.000000000 | a            |
    |         2 | 2016-01-01 21:40:35.957315 |     0.000000000 | b            |
    |         3 | 2016-01-01 21:40:37.957569 |     2.000253916 | c            |
    |         4 | 2016-01-01 21:40:37.957569 |     0.000500202 | d            |
    |         5 | 2016-01-01 21:40:39.958323 |     2.000253916 | e            |
    
    
    Specify custom column widths and formatters:
    
    >>> tpr = TableLogger(columns=['name', 'salary'],
    >>>                    column_formatters={1: '{:,.2f}'.format},
    >>>                    column_widths={0:12, 1:15})
    >>> tpr('John Smith',  1200000.890)
    >>> tpr('Tommy Cache',   70000.125)
    +--------------+-----------------+
    | name         |          salary |
    |--------------+-----------------|
    | John Smith   |    1,200,000.89 |
    | Tommy Cache  |       70,000.12 |

"""
import sys
import datetime

from . import fmt


type2fmt = {
    float:             fmt.FloatFormatter,
    int:               fmt.IntegerForamtter,
    datetime.datetime: fmt.DatetimeFormatter,
    datetime.date:     fmt.DateFormatter,
    }


class TableLogger(object):
    """
    The main class for printing tabular data.
    
    Example:
        >>> tpr = TableLogger()
        >>> tpr(1, 'Row1', datetime.now(), math.pi)
        >>> tpr(2, 'Row2', datetime.now(),    1/3.)
    
    Args:
        time_delta (boolean): include a time delta column. Defaults to False.
        timestamp (boolean): include a timestamp column. Defaults to False.
        rownum (boolean): include a column with row numbers
        columns (list): column names. If specified, a table header will be
            printed. Defaults to None.
        border (boolean): draw table borders. Defaults to True.
        column_formatters (dict): custom column formatters. Defaults to None.
        column_widths (dict): custom column widths. Defaults to None.
        file (file object): Defaults to sys.stdout
    """
    
    
    def __init__(self,
                 time_delta=False,
                 timestamp=False,
                 rownum=False,
                 columns=None,
                 border=True,
                 column_formatters=None,
                 column_widths=None,
                 file=sys.stdout,
                 ):
        self.time_diff = time_delta
        self.timestamp = timestamp
        self.rownum = rownum
        self.columns = columns if columns is not None else []
        self.border = border
        self.column_formatters = column_formatters or {}
        self.column_widths = column_widths or {}
        self.file = file
        
        self.col_sep = ' '
        self.formatters = []
        
        if time_delta:
            self.columns.insert(0, 'time delta')
        if timestamp:
            self.columns.insert(0, 'timestamp')
        if rownum:
            self.columns.insert(0, 'row')
        
        
    
    def setup_formatters(self, *args):
        """ Setup formatters by observing the first row.  
        
        Args:
            *args: row cells
        """
        formatters = []
        if self.time_diff:
            formatters.insert(0, fmt.TimeDeltaFormatter.setup(0))
        if self.timestamp:
            formatters.insert(0, fmt.DatetimeFormatter.setup(
                                        datetime.datetime.now(),
                                        fmt='{:%Y-%m-%d %H:%M:%S.%f}'.format,
                                        col_width=26))
        if self.rownum:
            formatters.insert(0, fmt.RowNumberFormatter.setup(0))
        
        for col, value in enumerate(args):
            if type(value) in type2fmt:
                fmt_class = type2fmt[type(value)]
            else:
                fmt_class = fmt.GenericFormatter
            
            kwargs = {}
            if col in self.column_widths:
                kwargs['col_width'] = self.column_widths[col] 
            if col in self.column_formatters:
                kwargs['fmt'] = self.column_formatters[col]
            
            formatter = fmt_class.setup(value, **kwargs)
            formatters.append(formatter)
        self.formatters = formatters
    
    
    def __call__(self, *args):
        """Prints a formatted row
        
        Args:
            *args: row cells
        """
        if len(self.formatters) == 0:
            self.setup_formatters(*args)
            if self.columns:
                self.print_header()
            elif self.border:
                self.print_line(self.make_horizontal_border())
        
        args = list(args)
        
        if self.time_diff:
            args.insert(0, 0)
        if self.timestamp:
            args.insert(0, datetime.datetime.now())
        if self.rownum:
            args.insert(0, 1000)
        
        if len(args) != len(self.formatters):
            raise ValueError('Expected number of columns - {}. Got {}.'.format(
                                len(self.formatters), len(args)))
        
        line = self.format_row(*args)
        self.print_line(line)
        
    
    def format_row(self, *args):
        vals = [self.format_column(value, col) for col, value in enumerate(args)]
        row = self.join_row_items(*vals)
        return row
    
    
    def format_column(self, value, col):
        return self.formatters[col](value)
    
    
    def print_header(self):
        col_names = []
        for col_idx, col_name in enumerate(self.columns):
            col_width = self.formatters[col_idx].col_width
            if len(col_name ) > col_width:
                col_name  = col_name[:col_width-3] + '...'
            col_name = self.formatters[col_idx].just(col_name, col_width)
            col_names.append(col_name)
        
        header = self.join_row_items(*col_names)
        
        if self.border == True:
            self.print_line(self.make_horizontal_border())
            self.print_line(header)
            self.print_line(self.make_horizontal_border('|'))
        else:
            self.print_line(header)
        
    
    def make_horizontal_border(self, corner='+'):
        border = '-+-'.join('-' * fmr.col_width for fmr in self.formatters)
        return u'{0}-{1}-{0}'.format(corner, border)
    
    
    def join_row_items(self, *args):
        if self.border == True:
            return '| {} |'.format(' | '.join(args))
        else:
            return '{}'.format(self.col_sep).join(args)
        
    
    def print_line(self, text):
        self.file.write(text)
        self.file.write('\n')
        self.file.flush()

