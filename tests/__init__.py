from fsdb import Fsdb

import tempfile
import unittest
import os
import random
import shutil
import string


class FsdbTest(unittest.TestCase):

    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")
        self.fsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "fsdbRoot"))

    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def createTestFile(self):
        fd, fpath = tempfile.mkstemp(prefix='test_file',
                                     dir=self.fsdb_tmp_path)
        f = os.fdopen(fd, 'w')
        f.write("test" + randomID(7))
        f.close()
        return fpath


def randomID(length):
        return ''.join(random.choice(string.hexdigits) for _ in range(length))
