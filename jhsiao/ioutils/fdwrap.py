import io
import os

from .forwarder import Forwarder

class FDWrap(io.RawIOBase):
    """Wrap a file-like object with a fileno from pipes.

    A forwarder is created to forward data from the file-like object to
    one end of a pipe.  The FDWrap returns the fileno of the other end
    of the pipe.  This results in a fileno that can essentially read
    from or write to the file-like object using the forwarder as an
    intermediate.

    If used as a context manager, the corresponding pipe end will be
    closed on __exit__.  This can be especially important when using
    write mode because it would allow the read end of the pipe to see
    the eof.
    """
    def __init__(self, fobj, mode):
        """Iniitialize FDWrap.

        fobj: file-like object.
            The object to wrap.
        mode: str ['r'|'w']['b']
            Specify whether the FDWrap should in read or write mode.
            Only one of read or write mode is allowed.  If a b is in
            the mode, then binary mode will be used.
        """
        self._orig = fobj
        r, w = os.pipe()
        if 'r' in mode:
            self.file = os.fdopen(r, mode)
            self._forward = Forwarder(
                fobj, os.fdopen(w, 'wb'), False, True)
        else:
            self.file = os.fdopen(w, mode)
            self._forward = Forwarder(
                os.fdopen(r, 'rb'), fobj, True, False)

    def __enter__(self):
        return self

    def __exit__(self, tp, exc, tb):
        self.file.close()

    def join(self):
        """Wait for forwarding to end and return original file object."""
        self.file.close()
        self._forward.join()
        return self._orig

    def detach(self):
        """Close the corresponding pipe end and return forwarder."""
        self._forward.stop()
        return self._orig

    def close(self):
        """Detach and also close original file-like object."""
        self.detach().close()

    def fileno(self):
        return self.file.fileno()

    @staticmethod
    def isatty():
        return False
    @staticmethod
    def readable():
        return False
    @staticmethod
    def writable():
        return False
    @staticmethod
    def seekable():
        return False

if __name__ == '__main__':
    import subprocess as sp
    import sys
    import io
    commands = io.StringIO(
        'import sys\nprint(sys.version_info)\nexit()\n')
    with FDWrap(commands, 'rb') as wrap:
        p = sp.Popen(
            [sys.executable], stdin=wrap, stdout=sp.PIPE, stderr=sp.PIPE)
    assert wrap.join() is commands
    stdo, stde = p.communicate()
    commands.close()
    assert io.TextIOWrapper(io.BytesIO(stdo)).read().strip() == str(sys.version_info)
    assert stde == b''

    with FDWrap(io.StringIO(), 'wb') as wrap:
        p = sp.Popen(
            [sys.executable], stdin=sp.PIPE,
            stdout=wrap, stderr=sp.PIPE)
    assert p.stdout is None
    stdo, stde = p.communicate(
        b'import sys\nprint(sys.version_info)\nexit()\n')
    buf = wrap.join()
    assert buf.getvalue().strip() == str(sys.version_info)
    assert stde == b''
    print('pass')
