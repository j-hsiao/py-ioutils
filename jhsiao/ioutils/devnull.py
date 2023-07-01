"""Null device file."""
__all__ = ['DevNull']
import io
import os

class DevNull(io.RawIOBase):
    """Null device file-like object.

    If an fd is requested via fileno(), then open the appropriate
    device (nul on Windows, else /dev/null) and use the resulting fd.
    """
    try:
        from subprocess import DEVNULL
    except ImportError:
        DEVNULL = None

    def __init__(self, subprocess=False):
        """Initialize DevNull.

        If subprocess, DevNull is being used as a subprocess file.
        In this case, fileno() should return subprocess.DEVNULL
        instead of opening os.devnull and returning that fileno.
        """
        self._is_sp = subprocess
        self._f = None

    def __repr__(self):
        return 'DevNull'

    def fileno(self):
        if self._is_sp and self._DEVNULL is not None:
            return self._DEVNULL
        if self._f is None:
            try:
                self._f = open(os.devnull, 'r+b')
            except AttributeError:
                import platform
                if platform.system() == 'Windows':
                    self._f = open('NUL', 'r+b')
                else:
                    self._f = open('/dev/null', 'r+b')
        return self._f.fileno()

    def close(self):
        if self._f is not None:
            self._f.close()
            self._f = None

    def flush(self):
        pass
    def isatty(self):
        return False
    def readable(self):
        return True
    def readline(self, size=-1):
        return b''
    def readlines(self, hint=-1):
        return []
    def seek(self, offset, whence=io.SEEK_SET):
        return 0
    def seekable(self):
        return True
    def tell(self):
        return 0
    def truncate(self, size=None):
        return 0
    def writable(self):
        return True
    def writelines(self, lines):
        pass
    def write(self, buf):
        return len(buf)
    def read(self, size=-1):
        return b''
    def readall(self):
        return b''
    def readinto(self, buf):
        return 0
    read1 = read
    readinto1 = readinto

if __name__ == '__main__':
    import os

    with DevNull() as f:
        assert f.readlines() == []
        assert f.read(69) == b''
        assert f.tell() == 0
        assert f.seek(69) == 0
        assert f.write(b'hello world') == len(b'hello world')
        fd = f.fileno()
        print(os.fstat(f.fileno()))
    try:
        os.fstat(fd)
        assert False, "fd should be closed."
    except EnvironmentError:
        print('pass')
