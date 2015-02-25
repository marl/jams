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
        lab_data = [[0, 1.5, 'a\tblah blah'],
                    [],
                    ['# I am a comment'],
                    ['b', -2, -5.5]]
        text = ["\t".join(["%s" % _ for _ in row]) + "\n" for row in lab_data]
        fhandle = os.fdopen(fid, 'w')
        fhandle.writelines(text)
        fhandle.close()
        result = util.read_lab(fpath, 3, delimiter='\t', comment='#')
        self.assertEqual(result[0], [0, 'b'])
        self.assertEqual(result[1], [1.5, -2])
        self.assertEqual(result[2], ['a\tblah blah', -5.5])

        result = util.read_lab(fpath, 4, delimiter='\t', comment='#')
        self.assertEqual(result[0], [0, 'b'])
        self.assertEqual(result[1], [1.5, -2])
        self.assertEqual(result[2], ['a', -5.5])
        self.assertEqual(result[3], ['blah blah', ''])

        os.remove(fpath)

if __name__ == "__main__":
    unittest.main()
