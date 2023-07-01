__all__ = ['BytesReader']
import io

class BytesReader(io.RawIOBase):
    """Use a bytes as contents of a file (readonly).

    Basically an io.BytesIO() except it does not copy
    data and is not writable.
    """
    def __init__(self, data):
        """Initialize BytesReader

        data: the data to wrap.
        memviews: Return memoryviews when reading to reduce copies.
        """
        self.data = memoryview(data)
        self.pos = 0

    def writable(self):
        return False
    def readable(self):
        return True
    def seekable(self):
        return True

    def read(self, size=-1):
        """Read size bytes and return a bytes object."""
        return self.readview(size).tobytes()

    def readview(self, size=-1):
        """Read size bytes and return a memoryview."""
        data = self.data
        pos = self.pos
        dlen = len(data)
        if size is None or size < 0:
            ret = data[pos:]
            self.pos = dlen
            return ret
        end = min(pos+size, dlen)
        ret = data[pos:end]
        self.pos = end
        return ret

    def readinto(self, buf):
        """Read data into the given buffer."""
        pos = self.pos
        data = self.data
        size = min(len(buf), len(data)-pos)
        buf[:size] = data[pos:pos+size]
        self.pos += size
        return size

    def readall(self):
        return self.read()

    def truncate(self, size):
        """Just slice data and make another fobj."""
        raise NotImplementedError
    def seek(self, pos, whence=io.SEEK_SET):
        dlen = len(self.data)
        if whence == io.SEEK_CUR:
            pos += self.pos
        elif whence == io.SEEK_END:
            pos += dlen
        self.pos = max(min(dlen, pos), 0)
        return self.pos
    def tell(self):
        return self.pos

    def isatty(self):
        return False
    def close(self):
        self.data = None
        super(BytesReader, self).close()
    def fileno(self):
        raise OSError("BytesReader has no fileno.")
    def flush(self):
        pass

if __name__ == '__main__':
    msg = b'hello world!\ngoodbye world!'
    with BytesReader(msg) as f:
        assert list(f) == msg.splitlines(True)
        f.seek(0)
        assert list(f) == msg.splitlines(True)
        f.seek(0, io.SEEK_END)
        assert list(f) == []
        f.seek(-2, io.SEEK_END)
        assert list(f) == [b'd!']
    print('pass')
