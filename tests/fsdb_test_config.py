from fsdb import Fsdb
import fsdb.config
import unittest
import tempfile
import shutil
import os
from nose.tools import raises
from StringIO import StringIO


class FsdbTestConfig(unittest.TestCase):

    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")

    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def test_creation_without_params(self):
        Fsdb(self.fsdb_tmp_path)

    def test_creation_with_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode="0600",
                    dmode="0700",
                    deep=10,
                    hash_alg="sha512")
        self.assertEqual(fsdb._conf['fmode'], int("0600", 8))
        self.assertEqual(fsdb._conf['dmode'], int("0700", 8))
        self.assertEqual(fsdb._conf['deep'], 10)
        self.assertEqual(fsdb._conf['hash_alg'], "sha512")

    def test_negative_depth(self):
        Fsdb(self.fsdb_tmp_path,
             deep=5,
             hash_alg="sha1")

    def test_fmode_passing(self):
        fmode = "0600"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=fmode)
        self.assertEqual(fsdb._conf['fmode'], int(fmode, 8))

    def test_dmode_passing(self):
        dmode = "0700"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=dmode)
        self.assertEqual(fsdb._conf['dmode'], int(dmode, 8))

    def test_fmode_other_session(self):
        fmode = "0600"
        Fsdb(self.fsdb_tmp_path, fmode=fmode)
        fsdb = Fsdb(self.fsdb_tmp_path, fmode="0000")
        self.assertEqual(fsdb._conf['fmode'], int(fmode, 8))

    def test_all_algorithm(self):
        testStr = "quellochetepare"
        for alg in fsdb.config.ACCEPTED_HASH_ALG:
            mFsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "test_alg"), hash_alg=alg, deep=0)
            digest = mFsdb.add(StringIO(testStr))
            with mFsdb[digest] as f:
                self.assertEqual(f.read(), testStr)

    @raises(ValueError)
    def test_wrong_algorithm(self):
        Fsdb(self.fsdb_tmp_path, hash_alg="verystrangealgorithm")
