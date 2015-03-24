# -*- coding: utf-8 -*-

import os
import errno
import stat
import unicodedata
import shutil
import logging
import string
import config
import hashtools


class Fsdb(object):
    """File system database
    expose a simple api (add,get,remove)
    to menage the saving of files on disk.
    files are placed under specified fsdb root folder and
    are managed using a directory tree generated from the file  digest
    """

    BLOCK_SIZE = 2**20
    CONFIG_FILE = ".fsdb.conf"

    def __init__(self, fsdbRoot, deep=None, hash_alg=None, fmode=None, dmode=None):
        """Create an fsdb instance.

        If file named ".fsdb.conf" it is found in @fsdbRoot,
        the file will be parsed, config options will be loded and
        function parameters will be ignored.
        If there is not such file, function parameters will be loaded and
        written to ".fsdb.conf" in @fsdbRoot

        Args:
            fsdbRoot -- root path under will be placed all files
            deep  -- number of levels to use for directory tree (default: 3)
            hash_alg -- string name of the hash algorithm to use (default: "sha1")
            fmode  -- string reppresenting the mask (octal) \
              to use for files creation (default: "0660")
            dmode  -- string reppresenting the mask (octal) \
              to use for folders creation (default depends on fmode)
        """

        self.logger = logging.getLogger(__name__)

        # cleanup the path
        fsdbRoot = os.path.expanduser(fsdbRoot)    # replace ~
        fsdbRoot = os.path.expandvars(fsdbRoot)    # replace vars
        fsdbRoot = os.path.normpath(fsdbRoot)      # replace /../ and so on
        fsdbRoot = os.path.realpath(fsdbRoot)      # resolve links

        # check if path it's absolute
        if not os.path.isabs(fsdbRoot):
            raise Exception("fsdb can not operate on relative path")

        # on different platforms same unicode string could have different rappresentation
        if isinstance(fsdbRoot, unicode):
            fsdbRoot = unicodedata.normalize("NFC", fsdbRoot)

        configPath = os.path.join(fsdbRoot, Fsdb.CONFIG_FILE)

        if Fsdb.config_exists(fsdbRoot):
            # warn user about config ignoring and load config from file
            self.logger.debug("Fsdb config file found. Runtime parameters will be ignored. ["+configPath+"]")

            conf = config.loadConf(configPath)
            self._conf = conf

        else:
            conf = dict()

            if deep is not None:
                conf['deep'] = deep
            if hash_alg is not None:
                conf['hash_alg'] = hash_alg
            if fmode is not None:
                conf['fmode'] = fmode
            if dmode is not None:
                conf['dmode'] = dmode

            conf = config.normalizeConf(conf)

            self._conf = conf

            # make all parent directories if they do not exist
            self._makedirs(fsdbRoot)

            # write config file
            self._create_empty_file(configPath)
            config.writeConf(configPath, conf)

        # fsdbRoot it is an existing regular folder and we have read and write permission
        self.fsdbRoot = fsdbRoot

        self.logger.debug("Fsdb initialized successfully: "+self.__str__())

    def _calc_digest(self, origin):
        """calculate digest for the given file or readable/seekable object

         Args:
            origin -- could be the path of a file or a readable/seekable object ( fileobject, stream, stringIO...)
         Returns:
            String rapresenting the digest for the given origin
        """
        if hasattr(origin, 'read') and hasattr(origin, 'seek'):
            pos = origin.tell()
            digest = hashtools.calc_digest(origin, algorithm=self._conf['hash_alg'])
            origin.seek(pos)
        else:
            digest = hashtools.calc_file_digest(origin, algorithm=self._conf['hash_alg'])
        return digest

    def _copy_content(self, origin, dstPath):
        """copy the content of origin into dstPath"""

        if hasattr(origin, 'read') and hasattr(origin, 'seek'):
            pos = origin.tell()
            with open(dstPath, 'wb') as dst:
                while True:
                    chunk = origin.read(Fsdb.BLOCK_SIZE)
                    if not chunk:
                        break
                    dst.write(chunk)
            origin.seek(pos)
        else:
            shutil.copyfile(origin, dstPath)

    def _create_empty_file(self, path):
        oldmask = os.umask(0)
        fd = os.open(path, os.O_CREAT | os.O_WRONLY, self._conf['fmode'])
        os.close(fd)
        os.umask(oldmask)

    def _makedirs(self, path):
        """Make folders recursively for the given path and
           check read and write permission on the path
          Args:
            path -- path to the leaf folder
        """
        try:
            oldmask = os.umask(0)
            os.makedirs(path, self._conf['dmode'])
            os.umask(oldmask)
        except OSError, e:
            if(e.errno == errno.EACCES):
                raise Exception("not sufficent permissions to write on fsdb folder: \""+path+'\"')
            elif(e.errno == errno.EEXIST):
                fstat = os.stat(path)
                if not stat.S_ISDIR(fstat.st_mode):
                    raise Exception("fsdb folder already exists but it is not a regular folder: \""+path+'\"')
                elif not os.access(path, os.R_OK and os.W_OK):
                    raise Exception("not sufficent permissions to write on fsdb folder: \""+path+'\"')
            else:
                raise e

    def add(self, origin):
        """Add new element to fsdb.

         Args:
            origin -- could be the path of a file or a readable/seekable object ( fileobject, stream, stringIO...)
         Returns:
            String rapresenting the digest of the file
        """

        digest = self._calc_digest(origin)

        if self.exists(digest):
            self.logger.debug('Added File: ['+digest+'] ( Already exists. Skipping transfer)')
            return digest

        absPath = self.get_file_path(digest)
        absFolderPath = os.path.dirname(absPath)

        # make all parent directories if they do not exist
        self._makedirs(absFolderPath)
        self._create_empty_file(absPath)
        self._copy_content(origin, absPath)

        self.logger.debug('Added file: "'+digest+'" [ '+absPath+' ]')

        return digest

    def remove(self, digest):
        """Remove an existing file from fsdb.
           File with the given digest will be removed from fsdb and
           the directory tree will be cleaned (remove empty folders)
         Args:
            digest -- digest of the file to remove
        """
        # remove file
        absPath = self.get_file_path(digest)
        os.remove(absPath)

        # clean directory tree
        tmpPath = os.path.dirname(absPath)
        while tmpPath != self.fsdbRoot:
            if os.path.islink(tmpPath):
                raise Exception('fsdb found a link in db tree: "'+tmpPath+'"')
            if len(os.listdir(tmpPath)) > 0:
                break
            os.rmdir(tmpPath)
            tmpPath = os.path.dirname(tmpPath)

        self.logger.debug('Removed file: "'+absPath+'" [ '+digest+' ]')

    def exists(self, digest):
        """Check file existence in fsdb

          Returns:
            True if file exists under this instance of fsdb, false otherwise
        """
        return os.path.isfile(self.get_file_path(digest))

    def get_file_path(self, digest):
        """Retrieve the absolute path to the file with the given digest

          Args:
            digest -- digest of the file
          Returns:
            String rapresenting the absolute path of the file
        """
        relPath = Fsdb.generate_tree_path(digest, self._conf['deep'])
        return os.path.join(self.fsdbRoot, relPath)

    def check(self, digest):
        """Check the integrity of the file with the given digest

          Args:
            digest -- digest of the file to check
          Returns:
            True if the file is not corrupted
        """
        path = self.get_file_path(digest)
        if self._calc_digest(path) != digest:
            self.logger.warning("found corrupted file: '{}'".format(path))
            return False
        return True

    def corrupted(self):
        """Iterate over digests of all corrupted stored files"""
        for digest in self:
            if not self.check(digest):
                yield digest

    def __iter__(self):
        """Iterate over digests of all stored files

        Fsdb does not use auxiliary data structure, so this function
        will search the underlying filesystem for all the file at the expected depth.
        """
        for dirpath, dirnames, filenames in os.walk(self.fsdbRoot):
            rel_dirpath = os.path.relpath(dirpath, self.fsdbRoot)
            # rel_dirpath does not have os.sep neither on front nor at the end. Ex uno/due/tre
            if (string.count(rel_dirpath, os.sep) + 1) != self._conf['deep']:
                continue
            for f in filenames:
                yield string.replace(rel_dirpath+f, os.sep, "")

    def __str__(self):
        return "{root: " + self.fsdbRoot + \
               ", deep: " + str(self._conf['deep']) + \
               ", hash_alg: " + self._conf['hash_alg'] + \
               ", fmode: " + str(oct(self._conf['fmode'])) + \
               ", dmode: " + str(oct(self._conf['dmode'])) + \
               "}"

    def __len__(self):
        """Return the number of stored files"""
        count = 0
        for _ in self:
            count += 1
        return count

    def __contains__(self, digest):
        return self.exists(digest)

    def __getitem__(self, digest):
        """Return an readable only file object of the stored file with the given digest

           Client should care about closing the file object after finished with it.

           Could raise ``IOError`` acoording to the standard ``open()`` function.
           If you need to write on file or implement some more complicated logic refer to :py:func:`get_file_path()`
        """
        if not isinstance(digest, basestring):
            raise TypeError("key must be instance of basestring")
        if not self.exists(digest):
            raise KeyError("no stored file found for '{}'".format(digest))
        return open(self.get_file_path(digest), 'rb')

    @staticmethod
    def generate_tree_path(fileDigest, deep):
        """Generate a relative path from the given fileDigest
            relative path has a numbers of directories levels according to @deep

         Args:
            fileDigest -- digest for which the relative path will be generate
            deep -- number of levels to use in relative path generation
         Returns:
            relative path for the given digest
        """
        if(deep < 0):
            raise Exception("deep level can not be negative")
        if(os.path.split(fileDigest)[1] != fileDigest):
            raise Exception("fileDigest cannot contain path separator")

        # calculate min length for the given deep (2^1+2^2+...+2^deep+ 1)
        min = (2**(deep+1))-1
        if(len(fileDigest) < min):
            raise Exception("fileDigest too short for the given deep")

        path = ""
        index = 0
        for p in range(1, deep+1):
            jump = 2**p
            path = os.path.join(path, fileDigest[index:index+jump])
            index += jump
        path = os.path.join(path, fileDigest[index:])
        return path

    @staticmethod
    def config_exists(fsdbRoot):
        path = os.path.join(fsdbRoot, Fsdb.CONFIG_FILE)
        try:
            os.stat(path)
        except OSError, e:
            if(e.errno == errno.EACCES):
                raise Exception("not sufficent permissions to stat fsdb config file: \""+path+'\"')
            elif(e.errno == errno.ENOENT):
                return False
            else:
                raise e
        return True
