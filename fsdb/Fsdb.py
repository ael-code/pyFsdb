# -*- coding: utf-8 -*- 

import os
import errno
import stat
import unicodedata
import hashlib
import shutil
import warnings


import config


class Fsdb(object):
   """File system database
      expose a simple api (add,get,remove) to menage the saving of files on disk.
      files are placed under specified fsdb root folder and 
      are managed using a directory tree generated from the file checksum
   """
   
   CONFIG_FILE = ".fsdb.conf"
   
   def __init__(self, fsdbRoot, mode=None, deep=None):
      """Create an fsdb instance.
         If file named ".fsdb.conf" it is found in @fsdbRoot, 
         the file will be parsed, config options will be loded and
         function parameters will be ignored.
         If there is not such file, function parameters will be loaded and 
         written to ".fsdb.conf" in @fsdbRoot
       Args:
         fsdbRoot -- root path under will be placed all files
         mode  -- mask (octal) to use for files/folders creation (default: 0770)
         deep  -- number of' levels to use for directory tree (default: 3)         
      """
      
      #cleanup the path
      fsdbRoot = os.path.expanduser(fsdbRoot)   # replace ~
      fsdbRoot = os.path.expandvars(fsdbRoot)   # replace vars
      fsdbRoot = os.path.normpath(fsdbRoot)     # replace /../ and so on
      fsdbRoot = os.path.realpath(fsdbRoot)     # resolve links
      
      #check if path it's absolute
      if not os.path.isabs(fsdbRoot):
         raise Exception("fsdb can not operate on relative path")
      
      #on different platforms same unicode string could have different rappresentation
      if isinstance(fsdbRoot, unicode):
         fsdbRoot = unicodedata.normalize("NFC", fsdbRoot)
      
      configPath = os.path.join(fsdbRoot,Fsdb.CONFIG_FILE)
      
      if Fsdb.configExists(fsdbRoot):
         ##warn user about config ignoring and load config from file
         warnings.warn("fsdb config file found. Runtime parameters will be ignored", RuntimeWarning)
         
         conf = config.loadConf(configPath)
         self._mode = conf['mode']
         self._deep = conf['deep']
         
      else:
         conf = config.getDefaultConf()
         if mode != None:
            conf['mode'] = mode
         if deep != None:
            conf['deep'] = deep
         
         self._mode = conf['mode']
         self._deep = conf['deep']
         
         #make all parent directories if they do not exist
         self._makedirs(fsdbRoot)
         
         #write config file
         config.writeConf(configPath,conf)
         oldmask = os.umask(0)
         os.chmod(configPath,self._mode)
         os.umask(oldmask)
         
         
      #fsdbRoot it is an existing regular folder and we have read and write permission
      self.fsdbRoot = fsdbRoot
      
   
   def add(self,filePath):
      """Add an existing file to fsdb.
         File under @filePath will be copied under fsdb directory tree
       Args:
         filePath -- path of the file to be add
       Returns:
         String rapresenting the checksum of the file
      """
      if not os.path.isfile(filePath):
         raise Exception("fsdb can not add: not regular file received")
      
      checksum = Fsdb.fileChecksum(filePath)
      
      absPath=self.getFilePath(checksum)
      absFolderPath = os.path.dirname(absPath)
      
      #make all parent directories if they do not exist
      self._makedirs(absFolderPath)
      
      #copy file and set permission
      oldmask = os.umask(0)
      shutil.copyfile(filePath, absPath)
      os.chmod(absPath,self._mode)
      os.umask(oldmask)
      
      return checksum
   
   def remove(self,checksum):
      """Remove an existing file from fsdb.
         File with the given checksum will be removed from fsdb and
         the directory tree will be cleaned (remove empty folders)
       Args:
         checksum -- checksum of the file to remove
      """
      #remove file
      absPath=self.getFilePath(checksum)
      os.remove(absPath)
      
      #clean directory tree
      tmpPath = os.path.dirname(absPath)
      while tmpPath != self.fsdbRoot:
         if os.path.islink(tmpPath):
            raise Exception("fsdb found a link in db tree: \""+tmpPath+'\"')
         if len(os.listdir(tmpPath)) > 0:
            break
         os.rmdir(tmpPath)
         tmpPath=os.path.dirname(tmpPath)
   
   def exists(self,checksum):
      """Check file existence in fsdb
        Returns:
         True if file exists under this instance of fsdb, false otherwise
      """
      return os.path.isfile(self.getFilePath(checksum))
   
   def getFilePath(self,checksum):
      """Retrieve path to the file with the given checksum
        Args:
         checksum -- checksum of the file
        Returns:
         String rapresenting the absolute path of the file      
      """
      relPath=Fsdb.generateDirTreePath(checksum,self._deep)
      return os.path.join(self.fsdbRoot,relPath)
      
   def _makedirs(self,path):
      """Make folders recursively for the given path and 
         check read and write permission on the path
        Args:
         path -- path to the leaf folder   
      """
      try:
         oldmask = os.umask(0)
         os.makedirs(path,self._mode)
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
      return "{root: "+self.fsdbRoot+", mode: "+str(oct(self._mode))+", deep: "+str(self._deep)+"}"


   @staticmethod
   def fileChecksum(filepath,block_size=2**20):
      """Calculate checksum
         File with the given checksum will be removed from fsdb and
         the directory tree will be cleaned (remove empty folders)
       Args:
         checksum -- checksum of the file to remove
      """
      hashM = hashlib.sha1()
      with open(filepath, 'r') as f:
         data = f.read(block_size)
         hashM.update(data)
      return hashM.hexdigest()
   
   @staticmethod
   def generateDirTreePath(fileChecksum,deep):
      """Generate a relative path from the given fileCheckSum
         relative path has a numbers of directories levels according to @deep
       Args:
         fileChecksum -- checksum for which the relative path will be generate
         deep -- number of levels to use in relative path generation
       Returns:
         relative path for the given checksum
      """
      if(deep < 0):
         raise Exception("deep level can not be negative")
      if( os.path.split(fileChecksum)[1] != fileChecksum):
         raise Exception("fileCheckSum cannot contain path separator")
      
      #calculate min length for the given deep (2^1+2^2+...+2^deep+ 1)
      min = (2**(deep+1))-1
      if( len(fileChecksum) < min):
         raise Exception("fileChecksum too short for the given deep")
         
      path=""
      index=0
      for p in range(1,deep+1):
         jump = 2**p
         path = os.path.join(path,fileChecksum[index:index+jump])
         index += jump
      path = os.path.join(path,fileChecksum[index:])
      return path
      
   @staticmethod
   def configExists(fsdbRoot):
      path = os.path.join(fsdbRoot,Fsdb.CONFIG_FILE)
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
