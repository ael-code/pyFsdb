.. Fsdb documentation master file, created by
   sphinx-quickstart on Mon Feb  9 16:35:29 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Fsdb documentation
===================
Fsdb is a one class solution to expose a simple api (add,get,remove) to menage the saving of files on disk.  
Files are placed under specified fsdb root folder and are managed using a directory tree generated from the file digest.

Quick start
-----------

Installation
^^^^^^^^^^^^
Fsdb is available on PyPI so you can easily install through pip

``pip install Fsdb``

Usage
^^^^^
.. code-block:: python

    from fsdb import Fsdb

    #create new fsdb instance
    myFsdb = Fsdb("/tmp/fsdbRoot")

    #add file
    fileDigest = myFsdb.add("/path/to/an/existing/file")

    #control if file exists
    myFsdb.exists(fileDigest)

    #get file path
    myFsdb.get_file_path(fileDigest)

    #remove file
    myFsdb.remove(fileDigest)


Contents
--------
.. toctree::
    :maxdepth: 2

    api/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
