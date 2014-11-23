pyFsdb
======
python file system database
-----
One class solution to expose a simple api (add,get,remove) to menage the saving of files on disk.  
Files are placed under specified fsdb root folder and are managed using a directory tree generated from the file checksum  
It is possible to choose how much levels to use in the directory tree.
#####Example
If you add a file with the following sha1sum to an fsdb instance with a deep level of 3
`7bf770901365d4b12ce46a2d545407daf224e583`  
The file will be placed in  
`/path_To_Fsdb_Root/7b/f770/901365d4/b12ce46a2d545407daf224e583`
#####Installation
`pip install Fsdb`
