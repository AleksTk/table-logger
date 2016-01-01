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
        tpl = TableLogger(file=f, column_widths={0:2, 1:5})
        tpl('12', '12345')
        tpl('ab', 'cdefg')
        self.assertEqual('+----+-------+\n| 12 | 12345 |\n| ab | cdefg |\n',
                         f.getvalue())
    
    
    def test_border(self):
        f = io.StringIO()
        tpl = TableLogger(file=f, column_widths={0:1, 1:1})
        tpl(1, 1)
        self.assertEqual('+---+---+\n| 1 | 1 |\n', f.getvalue())
        
        f = io.StringIO()
        tpl = TableLogger(file=f, column_widths={0:1, 1:1}, border=False)
        tpl(1, 1)
        self.assertEqual('1 1\n', f.getvalue())
        
        f = io.StringIO()
        tpl = TableLogger(file=f, column_widths={0:1, 1:1}, 
                           columns=['a', 'b'], border=False)
        tpl(1, 1)
        self.assertEqual('a b\n1 1\n', f.getvalue())
        
    
    def test_custom_formatters(self):
        f = io.StringIO()
        tpl = TableLogger(file=f, border=False,
                           column_formatters={0: '{:,.2f}'.format,
                                              1: '{:%Y-%m-%d}'.format}
                           )
        tpl(12345.1234, datetime.date(2013, 12, 25))
        self.assertEqual('12,345.12 2013-12-25', f.getvalue().strip())
    
    
    def test_invalid_column_number(self):
        tpl = TableLogger(file=io.StringIO())
        tpl(1, 2)
        self.assertRaises(ValueError, lambda: tpl(1,2,3))
    
    
    def test_timestamp_column(self):
        f = io.StringIO()
        tpl = TableLogger(file=f, timestamp=True, border=False)
        tpl()
        val = datetime.datetime.strptime(' '.join(f.getvalue().split()[-2:]), 
                                         '%Y-%m-%d %H:%M:%S.%f')
        self.assertTrue((datetime.datetime.now() - val).total_seconds() < 1)
    
    
    def test_time_delta_column(self):
        f = io.StringIO()
        tpl = TableLogger(file=f, time_delta=True, border=False)
        tpl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(0, val, places=2)
        
        time.sleep(1)
        tpl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(1, val, places=2)
        
        time.sleep(3)
        tpl()
        val = float(f.getvalue().split()[-1])
        self.assertAlmostEqual(3, val, places=2)
    
    
    def test_rownum_column(self):
        f = io.StringIO()
        tpl = TableLogger(file=f, rownum=True, border=False)
        
        for i in range(1, 10):
            tpl()
            val = int(f.getvalue().split()[-1])
            self.assertEqual(i, val)
    
        
if __name__ == "__main__":
    unittest.main()
    