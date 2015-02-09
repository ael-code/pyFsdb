pyFsdb
======
python file system database
-----
[![License](https://pypip.in/license/Fsdb/badge.svg?style=flat)](https://pypi.python.org/pypi/Fsdb/)
[![Latest Version](https://pypip.in/version/Fsdb/badge.svg?style=flat)](https://pypi.python.org/pypi/Fsdb/)
[![Documentation Status](https://readthedocs.org/projects/pyfsdb/badge/?version=latest)](https://pyfsdb.readthedocs.org/en/latest)

One class solution to expose a simple api (add,get,remove) to menage the saving of files on disk.  
Files are placed under specified fsdb root folder and are managed using a directory tree generated from the file digest

#####Installation
Fsdb is available on PyPI so you can easily install through pip  
`pip install Fsdb`

#####Usage
```python
from fsdb import Fsdb

#create new fsdb instance
myFsdb = Fsdb("/tmp/fsdbRoot")

#add file
fileDigest = myFsdb.add("/path/to/an/existing/file")

#control if file exists
myFsdb.exists(fileDigest)

#get file path
myFsdb.getFilePath(fileDigest)

#remove file
myFsdb.remove(fileDigest)
```

#####Path example
If you add a file with the following sha1sum to an fsdb instance with a configured deep level of 3
`7bf770901365d4b12ce46a2d545407daf224e583`  
The file will be placed in  
`/path_To_Fsdb_Root/7b/f770/901365d4/b12ce46a2d545407daf224e583`

#####Configuration
There are two ways to configure fsbd:
 - passing arguments to class constructor
 - editing the json config file
 
The config file must be in the fsdb root folder with name ```.fsdb.conf``` and must be written in a valid json syntax

| config name | type | default value | description |
|-------------|------|---------------|-------------|
|mode | string | "0770" | permissions mask to use in file/folder creation |
|deep | int | 3 | number of levels to use for directory tree |
|hash_alg | string | "sha1" | name of the hash algorithm to use for file digest|
