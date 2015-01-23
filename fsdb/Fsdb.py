# -*- coding: utf-8 -*-

import os
import errno
import stat
import unicodedata
import hashlib
import shutil
import logging

import config


class Fsdb(object):
    """File system database
       expose a simple api (add,get,remove)
       to menage the saving of files on disk.
       files are placed under specified fsdb root folder and
       are managed using a directory tree generated from the file  digest
    """

    CONFIG_FILE = ".fsdb.conf"

    def __init__(self, fsdbRoot, mode=None, deep=None, hash_alg=None):
        """Create an fsdb instance.
           If file named ".fsdb.conf" it is found in @fsdbRoot,
           the file will be parsed, config options will be loded and
           function parameters will be ignored.
           If there is not such file, function parameters will be loaded and
           written to ".fsdb.conf" in @fsdbRoot
         Args:
            fsdbRoot -- root path under will be placed all files
            mode  -- string reppresenting the mask (octal)
                     to use for files/folders creation (default: "0770")
            deep  -- number of levels to use for directory tree (default: 3)
            hash_alg -- string name of the hash algorithm to use (default: "sha1")q
            logHandler -- handler that will be used to log message
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

        if Fsdb.configExists(fsdbRoot):
            # warn user about config ignoring and load config from file
            self.logger.debug("Fsdb config file found. Runtime parameters will be ignored. ["+configPath+"]")

            conf = config.loadConf(configPath)
            self._conf = conf

        else:
            conf = dict()

            if mode is not None:
                conf['mode'] = mode
            if deep is not None:
                conf['deep'] = deep
            if hash_alg is not None:
                conf['hash_alg'] = hash_alg

            conf = config.normalizeConf(conf)

            self._conf = conf

            # make all parent directories if they do not exist
            self._makedirs(fsdbRoot)

            # write config file
            config.writeConf(configPath, conf)
            oldmask = os.umask(0)
            os.chmod(configPath, self._conf['mode'])
            os.umask(oldmask)

        # fsdbRoot it is an existing regular folder and we have read and write permission
        self.fsdbRoot = fsdbRoot

        self.logger.debug("Fsdb initialized successfully: "+self.__str__())

    def add(self, filePath):
        """Add an existing file to fsdb.
            File under @filePath will be copied under fsdb directory tree
         Args:
            filePath -- path of the file to be add
         Returns:
            String rapresenting the digest of the file
        """
        if not os.path.isfile(filePath):
            raise Exception("fsdb can not add: not regular file received")

        digest = Fsdb.fileDigest(filePath, algorithm=self._conf['hash_alg'])

        if self.exists(digest):
            self.logger.debug('Added File: ['+digest+'] ( Already exists. Skipping transfer)')
            return digest

        absPath = self.getFilePath(digest)
        absFolderPath = os.path.dirname(absPath)

        # make all parent directories if they do not exist
        self._makedirs(absFolderPath)

        # copy file and set permission
        oldmask = os.umask(0)
        shutil.copyfile(filePath, absPath)
        os.chmod(absPath, self._conf['mode'])
        os.umask(oldmask)

        self.logger.debug('Added file: "'+filePath+'" -> "'+absPath+'" [ '+digest+' ]')

        return digest

    def remove(self, digest):
        """Remove an existing file from fsdb.
            File with the given digest will be removed from fsdb and
            the directory tree will be cleaned (remove empty folders)
         Args:
            digest -- digest of the file to remove
        """
        # remove file
        absPath = self.getFilePath(digest)
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
        return os.path.isfile(self.getFilePath(digest))

    def getFilePath(self, digest):
        """Retrieve path to the file with the given digest
          Args:
            digest -- digest of the file
          Returns:
            String rapresenting the absolute path of the file
        """
        relPath = Fsdb.generateDirTreePath(digest, self._conf['deep'])
        return os.path.join(self.fsdbRoot, relPath)

    def _makedirs(self, path):
        """Make folders recursively for the given path and
            check read and write permission on the path
          Args:
            path -- path to the leaf folder
        """
        try:
            oldmask = os.umask(0)
            os.makedirs(path, self._conf['mode'])
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

    def __str__(self):
        return "{root: "+self.fsdbRoot+", mode: "+str(oct(self._conf['mode']))+", deep: "+str(self._conf['deep'])+", hash_alg: "+self._conf['hash_alg']+"}"

    @staticmethod
    def fileDigest(filepath, algorithm="sha1", block_size=2**20):
        """Calculate digest
            File with the given digest will be removed from fsdb and
            the directory tree will be cleaned (remove empty folders)
         Args:
            digest -- digest of the file to remove
        """
        if(algorithm == "md5"):
            algFunct = hashlib.md5
        elif(algorithm == "sha1" or algorithm == "sha"):
            algFunct = hashlib.sha1
        elif(algorithm == "sha224"):
            algFunct = hashlib.sha224
        elif(algorithm == "sha256"):
            algFunct = hashlib.sha256
        elif(algorithm == "sha384"):
            algFunct = hashlib.sha384
        elif(algorithm == "sha512" or algorithm == "sha2"):
            algFunct = hashlib.sha512
        else:
            raise ValueError('"' + algorithm + '" it is not a supported algorithm function')

        hashM = algFunct()
        with open(filepath, 'r') as f:
            data = f.read(block_size)
            hashM.update(data)
        return hashM.hexdigest()

    @staticmethod
    def generateDirTreePath(fileDigest, deep):
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
    def configExists(fsdbRoot):
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
