#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import unittest
import os
import random
import shutil
import filecmp
import string
import tempfile
from fsdb import Fsdb

class FsdbTestFunction(unittest.TestCase):
    
    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")
        self.fsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "fsdbRoot"))
    
    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def createTestFile(self):
        fd, fpath = tempfile.mkstemp(prefix='test_file',
                                    dir=self.fsdb_tmp_path)
        f = os.fdopen(fd, 'w')
        f.write("test"+randomID(7))
        f.close()
        return fpath

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

    def test_get_all(self):
        num = 10
        digests = list()
        for d in range(0,num):
            digests.append(self.fsdb.add(self.createTestFile()))
        inserted = [ i for i in self.fsdb ]
        # check that the two list contain exactly the same elements ( order does not metter )
        self.assertTrue(len(set(digests).intersection(inserted)) == num)

    def test_get_all_empty(self):
        inserted = [ i for i in self.fsdb ]
        self.assertFalse(inserted)

    def test_corrupted(self):
        num_corr = 3
        num_ok = 7
        corr = list()
        for _ in range(num_ok):
            self.fsdb.add(self.createTestFile())
        for i in range(num_corr):
            digest = self.fsdb.add(self.createTestFile())
            corr.append(digest)
            with open(self.fsdb.get_file_path(digest), "w") as f:
                f.write("more is less, less is more "+str(i))
        corrupted = [ d for d in self.fsdb.corrupted() ]
        self.assertTrue(len(set(corr).intersection(corrupted)) == num_corr)

    def test_corrupted_empty(self):
        num = 4
        for _ in range(num):
            self.fsdb.add(self.createTestFile())
        self.assertFalse([d for d in self.fsdb.corrupted()])


class FsdbTestConfig(unittest.TestCase):

    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")

    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def test_creation_without_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path)

    def test_creation_with_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path,
                    mode="0770",
                    deep=5,
                    hash_alg="sha1")


def randomID(length):
        return ''.join(random.choice(string.hexdigits) for _ in range(length))


if __name__ == '__main__':
    unittest.main()
