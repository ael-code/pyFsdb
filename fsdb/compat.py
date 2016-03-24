import sys


ISPYTHON2 = sys.version_info[0] < 3

if ISPYTHON2:
    string_types = basestring
else:
    string_types = str
