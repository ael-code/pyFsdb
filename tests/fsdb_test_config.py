from __future__ import unicode_literals

from fsdb import Fsdb
import fsdb.config
import unittest
import tempfile
import shutil
import os
from nose.tools import raises
from io import BytesIO


class FsdbTestConfig(unittest.TestCase):

    def setUp(self):
        self.fsdb_tmp_path = tempfile.mkdtemp(prefix="fsdb_test")

    def tearDown(self):
        shutil.rmtree(self.fsdb_tmp_path)

    def test_creation_without_params(self):
        Fsdb(self.fsdb_tmp_path)

    def test_creation_with_params(self):
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode="600",
                    dmode="700",
                    depth=10,
                    hash_alg="sha512")
        self.assertEqual(fsdb._conf['fmode'], int("600", 8))
        self.assertEqual(fsdb._conf['dmode'], int("700", 8))
        self.assertEqual(fsdb._conf['depth'], 10)
        self.assertEqual(fsdb._conf['hash_alg'], "sha512")

    def test_undirect_relative_path(self):
        '''A relative path containing back reference (/../) should be accepted and sanitized'''
        relPath = os.path.relpath(self.fsdb_tmp_path)
        fsdb = Fsdb(relPath)
        self.assertEqual(fsdb.fsdbRoot, self.fsdb_tmp_path)

    def test_direct_relative_path(self):
        '''A relative path should be accepted and sanitized'''
        absdir = os.path.dirname(self.fsdb_tmp_path)
        os.chdir(absdir)
        relPath = os.path.relpath(self.fsdb_tmp_path, absdir)
        fsdb = Fsdb(relPath)
        self.assertEqual(fsdb.fsdbRoot, self.fsdb_tmp_path)

    @raises(ValueError)
    def test_negative_depth(self):
        Fsdb(self.fsdb_tmp_path,
             depth=-5,
             hash_alg="sha1")

    def test_fmode_passing(self):
        fmode = "600"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=fmode)
        self.assertEqual(fsdb._conf['fmode'], int(fmode, 8))

    def test_dmode_passing(self):
        dmode = "700"
        fsdb = Fsdb(self.fsdb_tmp_path,
                    fmode=dmode)
        self.assertEqual(fsdb._conf['dmode'], int(dmode, 8))

    def test_fmode_other_session(self):
        fmode = "600"
        Fsdb(self.fsdb_tmp_path, fmode=fmode)
        fsdb = Fsdb(self.fsdb_tmp_path, fmode="000")
        self.assertEqual(fsdb._conf['fmode'], int(fmode, 8))

    def test_all_algorithm(self):
        testStr = b'quellochetepare'
        for alg in fsdb.config.ACCEPTED_HASH_ALG:
            mFsdb = Fsdb(os.path.join(self.fsdb_tmp_path, "test_alg"), hash_alg=alg, depth=0)
            digest = mFsdb.add(BytesIO(testStr))
            with mFsdb[digest] as f:
                self.assertEqual(f.read(), testStr)

    @raises(ValueError)
    def test_wrong_algorithm(self):
        Fsdb(self.fsdb_tmp_path, hash_alg="verystrangealgorithm")

    def test_config_converted(self):
        conf = fsdb.config.get_defaults()
        fsdb.config.from_json_format(conf)
        fsdb.config.to_json_format(conf)
        self.assertEqual(conf, fsdb.config.get_defaults())

    def test_deep_retrocompatibility(self):
        conf = fsdb.config.get_defaults()
        conf['deep'] = conf.pop('depth') + 1
        confFile = os.path.join(self.fsdb_tmp_path, Fsdb.CONFIG_FILE)
        fsdb.config.writeConf(confFile, conf)
        myFsdb = Fsdb(self.fsdb_tmp_path)
        self.assertEqual(myFsdb._conf['depth'], fsdb.config.get_defaults()['depth'] + 1)

    def test_write_default_config(self):
        Fsdb(self.fsdb_tmp_path)
        confFile = os.path.join(self.fsdb_tmp_path, Fsdb.CONFIG_FILE)
        conf = fsdb.config.loadConf(confFile)
        self.assertEqual(conf, fsdb.config.get_defaults())
