import unittest
import tempfile
import shutil
from fsdb import Fsdb

class FsdbTestConfig(unittest.TestCase):

    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")

    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def test_creation_without_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path)

    def test_creation_with_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode="0600",
                    dmode="0700",
                    deep=10,
                    hash_alg="sha2")
        self.assertEqual(fsdb._conf['fmode'], int("0600",8))
        self.assertEqual(fsdb._conf['dmode'], int("0700",8))
        self.assertEqual(fsdb._conf['deep'], 10)
        self.assertEqual(fsdb._conf['hash_alg'], "sha2")

    def test_negative_depth(self):
        fsdb = Fsdb(self.fsdb_tmp_path,
                    deep=5,
                    hash_alg="sha1")
    def test_fmode_passing(self):
        fmode = "0600"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=fmode)
        self.assertEqual(fsdb._conf['fmode'], int(fmode,8))

    def test_dmode_passing(self):
        dmode = "0700"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=dmode)
        self.assertEqual(fsdb._conf['dmode'], int(dmode,8))

    def test_fmode_other_session(self):
        fmode = "0600"
        Fsdb(self.fsdb_tmp_path, fmode=fmode)
        fsdb = Fsdb(self.fsdb_tmp_path,fmode="0000")
        self.assertEqual(fsdb._conf['fmode'], int(fmode,8))
