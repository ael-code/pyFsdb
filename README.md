pyFsdb
======
python file system database
-----
One class solution to expose a simple api (add,get,remove) to menage the saving of files on disk.  
Files are placed under specified fsdb root folder and are managed using a directory tree generated from the file digest

#####Installation
Fsdb it's available on PyPI so you can easily install through pip  
`pip install Fsdb`

#####Usage
```python
from fsdb import Fsdb

#create new fsdb instance
myFsdb = Fsdb("/tmp/fsdbRoot",mode=0770,deep=4)

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
