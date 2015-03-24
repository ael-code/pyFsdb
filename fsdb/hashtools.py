import hashlib
from os import stat


def calc_file_digest(filePath, algorithm):
    try:
        block_size = stat(filePath).st_blksize
    except AttributeError:
        block_size = None

    with open(filePath, 'rb', block_size) as f:
        digest = calc_digest(f, algorithm, block_size)

    return digest


def calc_digest(origin, algorithm="sha1", block_size=None):
    """Calculate digest of a readable object

     Args:
        origin -- a readable object for which calculate digest
        algorithn -- the algorithm to use. See ``hashlib.algorithms_available`` for supported algorithms.
        block_size -- the size of the block to read at each iteration
    """
    try:
        hashM = hashlib.new(algorithm)
    except ValueError:
        raise ValueError('hash algorithm not supported by the underlying platform: "{}"'.format(algorithm))

    while True:
        chunk = origin.read(block_size) if block_size else origin.read()
        if not chunk:
            break
        hashM.update(chunk)
    return hashM.hexdigest()
