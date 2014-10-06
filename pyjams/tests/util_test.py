"""
"""

import unittest
import tempfile
import pyjams.util as util
import os


class UtilTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_read_lab(self):
        fid, fpath = tempfile.mkstemp(suffix='.lab')
        lab_data = [(0, 1.5, 'a'),
                    (),
                    ('# I am a comment'),
                    ('b', -2, -5.5)]
        text = ["".join(["%s\t" % _ for _ in row]) + "\n" for row in lab_data]
        fhandle = os.fdopen(fid, 'w')
        fhandle.writelines(text)
        fhandle.close()
        col1, col2, col3 = util.read_lab(fpath, num_columns=3)
        self.assertEqual(col1, [0, 'b'])
        self.assertEqual(col2, [1.5, -2])
        self.assertEqual(col3, ['a', -5.5])

if __name__ == "__main__":
    unittest.main()
