About
======
Fsdb is a python implementation of a `content addressable storage`_, it is designed to work with a huge number of big files and it will use your filesystem in a smart way.

Fsdb is the right library for every one that doesn't want to store big files on his database.

Fsdb will works alongside your favorite database, it will help you to easily store and manage files while your database will handle metadata managment.

Quick start
===========

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
    file_digest = myFsdb.add("/path/to/an/existing/file")

    #control if file exists
    if file_digest in myFsdb:
        # file exists

    #get file object
    myFsdb[file_digest]

    #get file path
    myFsdb.get_file_path(file_digest)

    #check file integrity
    myFsdb.check(file_digest)

    #remove file
    myFsdb.remove(file_digest)

Configuration
=============

There are two ways to configure fsbd:
 - passing arguments to class constructor :py:func:`Fsdb.__init__()`
 - editing the json config file

The config file must be in the fsdb root folder with name ```.fsdb.conf``` and must be written in a valid json syntax

=============  ========  =================  ===================================================
config name    type      default value      description
=============  ========  =================  ===================================================
depth           int       3                  number of levels to use for directory tree
hash_alg       string    "sha1"             name of the hash algorithm to use for file digest
fmode          string    "660"              permissions mask to use in files creation
dmode          string    see :ref:`dmode`   permissions mask to use in folders creation
=============  ========  =================  ===================================================

.. _dmode:

dmode
^^^^^
If dmode is not provided, the default value will be used. The default value for dmode will be calculated from the fmode,
It will inherit all permissions from fmode and for every role that has read permission will be setted also the execute permission.

Path example
============
.. important::
   you shouldn't make any assumption about fsdb paths structure.
   The following explanation is for illustrative purpose only.

If you add a file with the following sha1sum to an fsdb instance with a configured depth level of 3

    ``7bf770901365d4b12ce46a2d545407daf224e583``

The file will be placed in

    ``/path_To_Fsdb_Root/7b/f770/901365d4/b12ce46a2d545407daf224e583``

.. _`content addressable storage`: http://en.wikipedia.org/wiki/Content-addressable_storage

