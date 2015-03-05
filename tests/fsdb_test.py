#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import unittest
import os
import random
import shutil
import filecmp
import string
from fsdb import Fsdb

class FsdbTest(unittest.TestCase):
    
    def setUp(self):
        self.FSDB_TMP_PATH="/tmp/fsdb"
        self.fsdb = Fsdb(self.FSDB_TMP_PATH+"/fsdbRoot")
    
    def createTestFile(self):
        testFilePath = os.path.join(self.FSDB_TMP_PATH,
                                    "testFile_"+randomID(4))
        with open(testFilePath, 'w') as f:
            f.write("test"+randomID(7))
        
        return testFilePath

    def test_creation_without_params(self):
        fsdbRootPath = os.path.join(self.FSDB_TMP_PATH, 
                                    "fsdbRoot_"+randomID(4))
        fsdb = Fsdb(fsdbRootPath)

    def test_creation_with_params(self):
        fsdbRootPath = os.path.join(self.FSDB_TMP_PATH,
                                    "fsdbRoot_"+randomID(4))
        fsdb = Fsdb(fsdbRootPath,
                    mode="0770",
                    deep=5,
                    hash_alg="sha1")

    def test_add(self):
        self.fsdb.add(self.createTestFile())

    def test_file_exists(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.assertTrue(self.fsdb.exists(digest))

    def test_file_not_exists(self):
        self.assertFalse(self.fsdb.exists(randomID(20)))

    def test_get_file_path(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.assertIsInstance(self.fsdb.get_file_path(digest),basestring)
        self.assertTrue(os.path.isabs(self.fsdb.get_file_path(digest)))

    def test_same_file_after_retrieval(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        storedFilePath = self.fsdb.get_file_path(digest)
        self.assertTrue( filecmp.cmp(testFilePath, storedFilePath, shallow=False) )
        
    def test_remove_existing_file(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.fsdb.remove(digest)
        
    def test_remove_not_existing_file(self):
        with self.assertRaisesRegexp(OSError,"No such file or directory"):
            self.fsdb.remove(randomID(20))

    def test_check(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.assertTrue(self.fsdb.check(digest))

    def test_check_fail(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        storedFilePath = self.fsdb.get_file_path(digest)
        with open(storedFilePath, 'w+') as f:
            f.write("more is less, less is more")
        self.assertFalse(self.fsdb.check(digest))

    def tearDown(self):
        shutil.rmtree(self.FSDB_TMP_PATH)


def randomID(length):
        return ''.join(random.choice(string.hexdigits) for _ in range(length))


if __name__ == '__main__':
    unittest.main()
