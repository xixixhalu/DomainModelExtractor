import os, os.path
import errno
import shutil

class fileOps:
# Taken from https://stackoverflow.com/a/600612/119527
    @staticmethod
    def mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

    @staticmethod
    def safe_open_w(path):
        ''' Open "path" for writing, creating any parent directories as needed.
        '''
        fileOps.mkdir_p(os.path.dirname(path))
        return open(path, 'w')

    @staticmethod
    def safe_delete_dir(path):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
