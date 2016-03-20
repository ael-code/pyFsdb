from __future__ import unicode_literals

from . import FsdbTest
from os.path import getsize


class FsdbTestPluralOperations(FsdbTest):

    def test_get_all(self):
        num = 10
        digests = list()
        for d in range(0, num):
            digests.append(self.fsdb.add(self.createTestFile()))
        inserted = [i for i in self.fsdb]
        # check that the two list contain exactly the same elements ( order does not metter )
        self.assertTrue(len(set(digests).intersection(inserted)) == num)

    def test_get_all_empty(self):
        inserted = [i for i in self.fsdb]
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
                f.write("more is less, less is more " + str(i))
        corrupted = [d for d in self.fsdb.corrupted()]
        self.assertTrue(len(set(corr).intersection(corrupted)) == num_corr)

    def test_corrupted_empty(self):
        num = 4
        for _ in range(num):
            self.fsdb.add(self.createTestFile())
        self.assertFalse([d for d in self.fsdb.corrupted()])

    def test_len(self):
        num = 5
        for _ in range(num):
            self.fsdb.add(self.createTestFile())
        self.assertEqual(len(self.fsdb), num)

    def test_len_empty(self):
        self.assertEqual(len(self.fsdb), 0)

    def test_size_0(self):
        self.assertEqual(self.fsdb.size(), 0)

    def test_size(self):
        num = 5
        tot = 0
        for _ in range(num):
            path = self.createTestFile()
            tot += getsize(path)
            self.fsdb.add(path)
        self.assertEqual(self.fsdb.size(), tot)
