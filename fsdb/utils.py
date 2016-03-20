import os
import errno
import tempfile
import platform


def calc_dir_mode(mode):
    R_OWN = int("0400", 8)
    R_GRP = int("0040", 8)
    R_OTH = int("0004", 8)
    X_OWN = int("0100", 8)
    X_GRP = int("0010", 8)
    X_OTH = int("0001", 8)
    # W_OWN = int("0200", 8)
    # W_GRP = int("0020", 8)
    # W_OTH = int("0002", 8)

    if mode & R_OWN:
        mode |= X_OWN
    if mode & R_GRP:
        mode |= X_GRP
    if mode & R_OTH:
        mode |= X_OTH
    return mode


def copy_content(origin, dstPath, blockSize, mode):
    ''' copy the content of `origin` to `dstPath` in a safe manner.

        this function will first copy the content to a temporary file
        and then move it atomically to the requested destination.

        if some error occurred during content copy or file movement
        the temporary file will be deleted.
    '''
    tmpFD, tmpPath = tempfile.mkstemp(prefix=os.path.basename(dstPath) + "_", suffix='.tmp', dir=os.path.dirname(dstPath))
    try:
        try:
            # change mode of the temp file
            oldmask = os.umask(0)
            try:
                os.chmod(tmpPath, mode)
            finally:
                os.umask(oldmask)
            # copy content to temporary file
            while True:
                chunk = origin.read(blockSize)
                if not chunk:
                    break
                os.write(tmpFD, chunk)
        finally:
            os.close(tmpFD)

        # move temporary file to actual requested destination
        try:
            os.rename(tmpPath, dstPath)
        except OSError as e:
            # on Windows if dstPath already exists at renaming time, an OSError is raised.
            if platform.system() is 'Windows' and e.errno is errno.EEXIST:
                pass
            else:
                raise
    except:
        os.remove(tmpPath)
        raise
