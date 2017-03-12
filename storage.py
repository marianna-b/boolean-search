import struct

import mmh3

REC_SIZE_INT = struct.calcsize('I')


class SimpleStorage:
    def __init__(self, filename):
        self.filename = filename
        self.fd = open("./" + filename, "r+")
        self.size = 0

    def add_int(self, x):
        arr = struct.pack('I', x)
        self.fd.write(arr)
        self.size += len(arr)

    def next_free(self):
        return self.size

    def add_string(self, s):
        self.fd.write(s)
        self.size += len(s)
        return len(s)

    def get_int(self, idx):
        self.fd.seek(idx * REC_SIZE_INT)
        val = struct.unpack_from('I', self.fd.read(REC_SIZE_INT))[0]
        return val

    def get_string(self, idx, len):
        self.fd.seek(idx)
        return self.fd.read(len)


HASH = 4
ITEM = 4

def bsearch_reads(fd, l, h, x):

    while l < h:
        mid = (l + h) // 2
        fd.seek(mid * (HASH + ITEM))
        val = struct.unpack('I', fd.read(HASH))[0] #  The result is a tuple even if it contains exactly one item
        if x == val:
            fd.seek(mid * (HASH + ITEM) + HASH)
            return struct.unpack('I', fd.read(ITEM))[0]
        if x < val:
            h = mid
        else:
            l = mid + 1

    return -1

class InMemoryHashTable:
    def __init__(self, filename):
        self.filename = filename
        self.dict = {}
        self.n = 0
        self.index = SimpleStorage(self.filename)

    def add(self, word, n):
        self.dict[word] = n

    def get(self, word):
        h = mmh3.hash(word.encode('utf-8'))
        n = self.index.get_int(0)
        idx = 0
        for i in range(1, (h % n)):
            idx += self.index.get_int(i)
        len = self.index.get_int(h % n)
        return bsearch_reads(self.index.fd, idx, idx + len, h)

    def store(self):
        self.n = len(self.dict) / 512
        t = {}
        for word in self.dict:
            h = mmh3.hash(word.encode('utf-8'))
            bask = h % self.n
            if t.has_key(bask):
                t[bask] = [(h, self.dict[word])]
            else:
                t[bask].extend((h, self.dict[word]))

        self.index.add_int(self.n)
        for i in range(self.n):
            self.index.add_int(len(t[i]))

        for i in range(self.n):
            for (h, elem) in sorted(t[i]):
                self.index.add_int(h)
                self.index.add_int(elem)


def store(filename, dict):
    index = SimpleStorage(filename + "_idx")
    docs = SimpleStorage(filename)
    for i in range(len(dict)):
        index.add_int(docs.next_free())
        index.add_int(docs.add_string(dict[i]))
