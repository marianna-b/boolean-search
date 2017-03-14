import struct

import mmh3

import mmap

REC_SIZE_INT = struct.calcsize('i')


class SimpleStorage:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        self.fd = open("./" + filename, mode)
        if mode != "w+":
            self.m = mmap.mmap(self.fd.fileno(), 0, access=mmap.ACCESS_READ)
        self.size = 0

    def add_int(self, x):
        arr = struct.pack('i', x)
        self.fd.write(arr)
        self.size += len(arr)

    def next_free(self):
        return self.size

    def add_string(self, s):
        self.fd.write(s)
        self.size += len(s)
        return len(s)

    def get_int(self, idx):
        try:
            tmp = self.m[idx * REC_SIZE_INT : idx * REC_SIZE_INT + 4]
            val = struct.unpack('i', tmp)[0]
            return val
        except IOError:
            return -1

    def get_string(self, idx, len):
        try:
            return self.m[idx:idx + len]
        except IOError:
            return -1


HASH = 4
ITEM = 4

def bsearch_reads(m, off, l, h, x,):
    while l < h:
        mid = (l + h) // 2
        tmp = m[off + mid * (HASH + ITEM): off + mid * (HASH + ITEM) + HASH]
        val = struct.unpack('i', tmp)[0]
        if x == val:
            tmp = m[off + mid * (HASH + ITEM) + HASH: off + (mid + 1) * (HASH + ITEM)]
            return struct.unpack('i', tmp)[0]
        if x < val:
            h = mid
        else:
            l = mid + 1

    return -1

class InMemoryHashTable:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        self.dict = {}
        self.n = 0
        self.index = SimpleStorage(self.filename, mode)

    def add(self, word, n):
        h = mmh3.hash(word.encode("utf-8"))
        self.dict[h] = n

    def get_from_dict(self, word):
        h = mmh3.hash(word.encode("utf-8"))
        if self.dict.has_key(h):
            return self.dict[h]
        else:
            return None

    def get(self, word):
        h = mmh3.hash(word)
        n = self.index.get_int(0)
        idx = 0
        for i in range(h % n):
            idx += self.index.get_int(i + 1)
        len = self.index.get_int((h % n) + 1)

        return bsearch_reads(self.index.m, (n + 1) * 4, idx, idx + len, h)

    def store(self):
        self.n = len(self.dict) / 512
        t = {}
        for h in self.dict:
            bask = h % self.n
            if not t.has_key(bask):
                t[bask] = [(h, self.dict[h])]
            else:
                t[bask].append((h, self.dict[h]))

        self.index.add_int(self.n)
        for i in range(self.n):
            self.index.add_int(len(t[i]))

        for i in range(self.n):
            t[i].sort()
            for (h, elem) in t[i]:
                self.index.add_int(h)
                self.index.add_int(elem)
