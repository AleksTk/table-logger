# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function

"""The module contains column formatters for basic python types."""

import time


class GenericFormatter(object):
    """Base class for column formatters. Typically is initialized using a class 
    method 'setup'.
    
    Example:
    
    >>> f = GenericFormatter.setup(example_value=1.45e+12)
    >>> f(7.34e+22)
    7.34e+22
    
    Args:
        fmt (function):  formatting functions
        col_width (int): column width
        just (str): column alignment: "l" for left,  "r" for right.
    """

    def __init__(self, fmt, col_width, just):
        self.fmt = fmt
        self.col_width = col_width
        self.just = ljust if just == 'l' else rjust

    def __call__(self, value):
        """
        Formats a given value
        
        Args:
            value: value to format
        
        Returns:
            str: formatted value
        """
        fmt = self.fmt(value)
        if len(fmt) > self.col_width:
            fmt = fmt[:self.col_width - 3] + '...'
        fmt = self.just(fmt, self.col_width)
        return fmt

    @classmethod
    def setup(cls, value, fmt='{}'.format, col_width=20, just='l'):
        return cls(fmt, col_width, just)


class DateFormatter(GenericFormatter):
    @classmethod
    def setup(cls, value, fmt=None, col_width=10, just='l'):
        fmt = fmt or '{:%Y-%m-%d}'.format
        return cls(fmt, col_width, just)


class DatetimeFormatter(GenericFormatter):
    @classmethod
    def setup(cls, value, fmt=None, col_width=19, just='l'):
        fmt = fmt or '{:%Y-%m-%d %H:%M:%S}'.format
        return cls(fmt, col_width, just)


class RowNumberFormatter(GenericFormatter):
    def __call__(self, value):
        if not hasattr(self, 'n'):
            self.n = 1
        fmt = super(RowNumberFormatter, self).__call__(self.n)
        self.n += 1
        return fmt

    @classmethod
    def setup(cls, value, fmt='{:d}'.format, col_width=9, just='r'):
        return cls(fmt, col_width, just)


class TimeDeltaFormatter(GenericFormatter):
    def __call__(self, value):
        if not hasattr(self, 'time'):
            self.time = time.time()
        diff = time.time() - self.time if hasattr(self, 'time') else 0
        self.time = time.time()
        fmt = super(TimeDeltaFormatter, self).__call__(diff)
        return fmt

    @classmethod
    def setup(cls, value, fmt='{:.9f}'.format, col_width=15, just='r'):
        return cls(fmt, col_width, just)


class IntegerFormatter(GenericFormatter):
    @classmethod
    def setup(cls, value, fmt=None, col_width=20, just='r'):
        if fmt is None:
            if len(str(value)) > col_width:
                fmt = '{{:.{}e}}'.format(col_width - 8)
            else:
                fmt = '{}'
            fmt = fmt.format
        return cls(fmt, col_width, just)


class FloatFormatter(GenericFormatter):
    @classmethod
    def setup(cls, value, fmt=None, col_width=20, just='r'):
        if fmt is None:
            value_str = str(value)
            if 'e' in value_str:
                fmt = '{{:.{}e}}'.format(max(0, min(6, col_width - 8)))
            else:
                if '.' in value_str:
                    head, tail = [len(e) for e in value_str.split('.')]
                else:
                    head, tail = len(value_str), 0
                if head >= col_width:
                    fmt = '{{:.{}e}}'.format(max(0, col_width - 8))
                elif len(value_str) > col_width:
                    fmt = '{{:.{}f}}'.format(col_width - head - 1)
                else:
                    precision = min(6, col_width - head - 1)
                    fmt = '{{:.{}f}}'.format(precision)
            fmt = fmt.format
        return cls(fmt, col_width, just)


def ljust(text, n):
    return text.ljust(n)


def rjust(text, n):
    return text.rjust(n)
