__all__ = ['SeqWriter']
import io

class SeqWriter(io.RawIOBase):
    """Write by appending to a sequence."""
    def __init__(self, cls=list):
        """Initialize SeqWriter.

        cls: If a type, then use cls(), otherwise
            cls should be a an instance with an append() method.
        Unseekable, and position = total amount written, not necessarily
        total data in sequence. (For example, if cls is
        deque(maxlen!=None))
        """
        if isinstance(cls, type):
            self.data = cls()
        else:
            self.data = cls
        self.pos = 0

    def writable(self):
        return True
    def readable(self):
        return False
    def seekable(self):
        return False

    def write(self, data):
        self.data.append(data)
        dlen = len(data)
        self.pos += dlen
        return dlen
    def seek(self, pos, whence=None):
        raise io.UnsupportedOperation
    def tell(self):
        return self.pos

    def isatty(self):
        return False
    def close(self):
        self.data = None
        super(SeqWriter, self).close()
    def fileno(self):
        raise OSError("SeqWriter has no fileno.")
    def flush(self):
        pass


if __name__ == '__main__':
    with SeqWriter() as f:
        f.write(b'hello')
        f.write(b'world')
        f.writelines([b'hello world!', b'goodbye world!'])
        assert f.data == [b'hello', b'world', b'hello world!', b'goodbye world!']

    import collections
    with SeqWriter(collections.deque(maxlen=2)) as f:
        f.writelines('hello world')
        assert list(f.data) == ['l', 'd']
    import pickle
    item = [1, 3.14, ('a', b'b'), dict(a=1, b=2, c=3.14, d=None)]
    with SeqWriter() as f:
        pickle.dump(item, f)
        assert pickle.loads(b''.join(f.data)) == item
    print('pass')
