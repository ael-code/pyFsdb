import os
import filecmp
import stat
from . import Fsdb
from . import FsdbTest


class FsdbTestInsertion(FsdbTest):

    def test_add(self):
        '''test insertion through path'''
        self.fsdb.add(self.createTestFile())

    def test_add_readable(self):
        '''test insertion through readable object'''
        with open(self.createTestFile(), 'rb') as testFile:
            self.fsdb.add(testFile)

    def test_get_file_path(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        self.assertIsInstance(self.fsdb.get_file_path(digest), basestring)
        self.assertTrue(os.path.isabs(self.fsdb.get_file_path(digest)))

    def test_same_digest_file_and_readable(self):
        '''path and readable opbject of the same file
           should have same id
        '''
        testFilePath = self.createTestFile()
        fileDigest = self.fsdb.add(testFilePath)
        with open(testFilePath, 'rb') as testFile:
            readableDigest = self.fsdb.add(testFile)
        self.assertTrue(readableDigest == fileDigest)

    def test_same_file_content_after_retrieval(self):
        testFilePath = self.createTestFile()
        digest = self.fsdb.add(testFilePath)
        storedFilePath = self.fsdb.get_file_path(digest)
        self.assertTrue(filecmp.cmp(testFilePath, storedFilePath, shallow=False))

    def test_same_readable_content_after_retrieval(self):
        testFilePath = self.createTestFile()
        with open(testFilePath, 'rb') as testFile:
            digest = self.fsdb.add(testFile)
        storedFilePath = self.fsdb.get_file_path(digest)
        self.assertTrue(filecmp.cmp(testFilePath, storedFilePath, shallow=False))

    def test_get_item_with_file_insertion(self):
        fpath = self.createTestFile()
        digest = self.fsdb.add(fpath)
        with open(fpath, 'rb') as f1, self.fsdb[digest] as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_get_item_with_readable_insertion(self):
        fpath = self.createTestFile()
        with open(fpath, 'rb') as testFile:
            digest = self.fsdb.add(testFile)
        with open(fpath, 'rb') as f1, self.fsdb[digest] as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_get_item_type_error(self):
        with self.assertRaises(TypeError):
            self.fsdb[3]
        with self.assertRaises(TypeError):
            self.fsdb[list()]

    def test_get_item_key_error(self):
        fpath = self.createTestFile()
        digest = self.fsdb._calc_digest(fpath)
        with self.assertRaises(KeyError):
            self.fsdb[digest]

    def test_right_permission(self):
        self.fsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "fsdbRoot_"),
                         fmode="0600",
                         dmode="0700",
                         deep=1)
        digest = self.fsdb.add(self.createTestFile())
        path = self.fsdb.get_file_path(digest)
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), self.fsdb._conf['fmode'])
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(path)).st_mode), self.fsdb._conf['dmode'])

    def test_not_enough_permission_on_directory(self):
        with self.assertRaisesRegexp(OSError, "Permission denied"):
            self.fsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "fsdbRoot_"),
                             dmode="0600")

    def test_not_enough_permission_on_file(self):
        with self.assertRaisesRegexp(OSError, "Permission denied"):
            self.fsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "fsdbRoot_"),
                             fmode="0400")
