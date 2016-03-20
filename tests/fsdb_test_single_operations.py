from __future__ import unicode_literals

import errno
from . import FsdbTest
from . import randomID


class FsdbTestSingleOperations(FsdbTest):

    def test_file_exists(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.assertTrue(self.fsdb.exists(digest))

    def test_file_not_exists(self):
        self.assertFalse(self.fsdb.exists(randomID(20)))

    def test_remove_existing_file(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.fsdb.remove(digest)

    def test_remove_not_existing_file(self):
        try:
            self.fsdb.remove(randomID(20))
            self.fail('Should raises OSError')
        except OSError as oe:
            self.assertEqual(oe.errno, errno.ENOENT)  # No such file or directory

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

    def test_contains(self):
        digest = self.fsdb.add(self.createTestFile())
        self.assertTrue(digest in self.fsdb)

    def test_contains_empty(self):
        digest = self.fsdb.add(self.createTestFile())
        self.assertTrue(digest in self.fsdb)
