# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import io
import datetime
import time

from table_logger import TableLogger
from table_logger.fmt import GenericFormatter, FloatFormatter


class Test(unittest.TestCase):
    
    
    def test_generic_formatter(self):
        gf = GenericFormatter.setup(value=1, col_width=5, just='r')
        self.assertEqual('    1', gf(1))
        self.assertEqual('12345', gf(12345))
        self.assertEqual('12...', gf(123456))
        
        gf = GenericFormatter.setup(value=1, col_width=5, just='l')
        self.assertEqual('1    ', gf(1))
        
        gf = GenericFormatter.setup(value=1, fmt='{:,d}'.format, col_width=9)
        self.assertEqual('1,234,567', gf(1234567))
    
    
    def test_float_formatter(self):
        ff = FloatFormatter.setup(123456789, col_width=10)
        self.assertEqual(' 123456789', ff(123456789))
        self.assertEqual('-123456789', ff(-123456789))
        self.assertEqual('-123456789', ff(-123456789.12))
        self.assertEqual('-123456...', ff(-1234567899))
        self.assertEqual('1234561...', ff(123456.123456e+120))
        
        ff = FloatFormatter.setup(123456.123456e+120, col_width=10)
        self.assertEqual(' 1.23e+125', ff(123456.123456e+120))
        self.assertEqual('-1.23e+125', ff(-123456.123456e+120))
        self.assertEqual('  1.23e+02', ff(123))
    
    
    def test_print_to_file(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, colwidth={0:2, 1:5})
        tbl('12', '12345')
        tbl('ab', 'cdefg')
        self.assertEqual('+----+-------+\n| 12 | 12345 |\n| ab | cdefg |\n',
                         f.getvalue())
    
    
    def test_border(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, colwidth={0:1, 1:1})
        tbl(1, 1)
        self.assertEqual('+---+---+\n| 1 | 1 |\n', f.getvalue())
        
        f = io.StringIO()
        tbl = TableLogger(file=f, colwidth={0:1, 1:1}, border=False)
        tbl(1, 1)
        self.assertEqual('1 1\n', f.getvalue())
        
        f = io.StringIO()
        tbl = TableLogger(file=f, colwidth={0:1, 1:1}, 
                           columns=['a', 'b'], border=False)
        tbl(1, 1)
        self.assertEqual('a b\n1 1\n', f.getvalue())
        
    
    def test_custom_formatters(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, border=False,
                          formatters={0: '{:,.2f}'.format,
                                      1: '{:%Y-%m-%d}'.format}
                          )
        tbl(12345.1234, datetime.date(2013, 12, 25))
        self.assertEqual('12,345.12 2013-12-25', f.getvalue().strip())
        
        f = io.StringIO()
        tbl = TableLogger(file=f, 
                          border=False,
                          columns=['number', 'datetime'],
                          formatters={'number':   '{:,.2f}'.format,
                                      'datetime': '{:%Y-%m-%d}'.format}
                          )
        tbl(12345.1234, datetime.date(2013, 12, 25))
        self.assertEqual('12,345.12 2013-12-25', f.getvalue().split('\n')[1].strip())
    
    
    def test_colwidth(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, border=False, colwidth={0: 30})
        tbl('col1')
        self.assertEqual(len(f.getvalue()) - 1, 30)
        
        f = io.StringIO()
        tbl = TableLogger(file=f, border=False, colwidth={0: 30, 1: 20})
        tbl('col1', 345)
        self.assertEqual(len(f.getvalue()) - 2, 30 + 20)
        
        f = io.StringIO()
        tbl = TableLogger(file=f, border=False, columns=['col1'], 
                          colwidth={'col1': 30})
        tbl('value')
        self.assertEqual(len(f.getvalue().split('\n')[1]), 30)
        
        f = io.StringIO()
        tbl = TableLogger(file=f, border=False, columns=['c1', 'c2'], 
                          colwidth={'c1': 30, 'c2': 20})
        tbl('col1', 345)
        self.assertEqual(len(f.getvalue().split('\n')[1]) - 1, 30 + 20)
        
    
    def test_invalid_column_number(self):
        tbl = TableLogger(file=io.StringIO())
        tbl(1, 2)
        self.assertRaises(ValueError, lambda: tbl(1,2,3))
    
    
    def test_timestamp_column(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, timestamp=True, border=False)
        tbl()
        val = datetime.datetime.strptime(' '.join(f.getvalue().split()[-2:]), 
                                         '%Y-%m-%d %H:%M:%S.%f')
        self.assertTrue((datetime.datetime.now() - val).total_seconds() < 1)
    
    
    def test_time_delta_column(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, time_delta=True, border=False)
        tbl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(0, val, places=2)
        
        time.sleep(1)
        tbl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(1, val, places=2)
        
        time.sleep(3)
        tbl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(3, val, places=2)
    
    
    def test_rownum_column(self):
        f = io.StringIO()
        tbl = TableLogger(file=f, rownum=True, border=False)
        
        for i in range(1, 10):
            tbl()
            val = int(f.getvalue().split()[-1])
            self.assertEqual(i, val)
    
        
if __name__ == "__main__":
    unittest.main()
    