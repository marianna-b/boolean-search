import struct

from storage import SimpleStorage

SIMPLE_9 = 0x90000000
SIMPLE_8 = 0x80000000
SIMPLE_7 = 0x70000000
SIMPLE_6 = 0x60000000
SIMPLE_5 = 0x50000000
SIMPLE_4 = 0x40000000
SIMPLE_3 = 0x30000000
SIMPLE_2 = 0x20000000
SIMPLE_1 = 0x10000000

en_simple = [[28, 1, SIMPLE_9, 1],
             [14, 3, SIMPLE_8, 2],
             [9, 7, SIMPLE_7, 3],
             [7, 15, SIMPLE_6, 4],
             [5, 31, SIMPLE_5, 5],
             [4, 127, SIMPLE_4, 7],
             [3, 511, SIMPLE_3, 9],
             [2, 16383, SIMPLE_2, 14],
             [1, 268435455, SIMPLE_1, 28]
             ]

de_simple = {SIMPLE_9: [28, 0x1, 1],
             SIMPLE_8: [14, 0x3, 2],
             SIMPLE_7: [9, 0x7, 3],
             SIMPLE_6: [7, 0xf, 4],
             SIMPLE_5: [5, 0x1f, 5],
             SIMPLE_4: [4, 0x7f, 7],
             SIMPLE_3: [3, 0x1ff, 9],
             SIMPLE_2: [2, 0x3fff, 14],
             SIMPLE_1: [1, 0xfffffff, 28]
             }


class Simple9Item:
    def __init__(self, arr):
        self.arr = arr
        self.a = []
        self.curr = 0
        self.last = -1

    def simple9_decode(self):
        if len(self.arr) <= self.curr:
            return
        global de_simple
        t = 0
        for i in range(4):
            t <<= 8
            t |= self.arr[self.curr + i]
        self.curr += 4

        code = t & 0xf0000000
        data = t & 0xfffffff
        info = de_simple[code]
        n, bit, shift = info[0], info[1], info[2]

        for i in range(n):
            self.a.append(data & bit)
            data >>= shift

    def get(self):
        if len(self.a) == 0:
            self.simple9_decode()
        if len(self.a) == 0:
            return -1

        if self.last == -1:
            self.last = 0

        self.last += self.a.pop(0)
        return self.last

    def simple9_encode(self):
        global en_simple
        off = 0
        length = len(self.a)
        while off < length:
            for t in en_simple:
                n, threshold, code, shift = t[0], t[1], t[2], t[3]

                if off + n <= length and max(self.a[off:off + n]) <= t[1]:
                    tmp = self.a[off]
                    for i in xrange(1, n):
                        tmp |= (self.a[off + i] << (shift * i))
                    tmp |= t[2]
                    self.arr.append((tmp >> 24) & 0xff)
                    self.arr.append((tmp >> 16) & 0xff)
                    self.arr.append((tmp >> 8) & 0xff)
                    self.arr.append(tmp & 0xff)
                    off += n
                    break
        self.a = []


class Simple9:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        if mode == "w+":
            fd1 = open("./" + filename + "_", mode)
            fd1.write("simple9")
            fd1.close()
        self.mode = mode
        self.dict = {}
        self.index = SimpleStorage(self.filename + "_idx", self.mode)
        self.docs = SimpleStorage(self.filename, self.mode)

    def add(self, word, doc):
        if not self.dict.has_key(word):
            self.dict[word] = Simple9Item(bytearray())

        self.dict[word].a.append(doc - max(0, self.dict[word].last))
        self.dict[word].last = doc
        if len(self.dict[word].a) > 27:
            self.dict[word].simple9_encode()

    def load(self, word):
        idx = self.index.get_int(2 * word)
        l = self.index.get_int(2 * word + 1)
        tmp = bytearray()
        tmp.extend(self.docs.get_string(idx, l))
        return Simple9Item(tmp)

    def set(self, word):
        self.dict[word] = self.load(word)

    def forget(self, word):
        self.dict.pop(word)

    def get_next(self, word):
        return self.dict[word].get()

    def flush(self):
        for word in self.dict:
            self.dict[word].simple9_encode()

    def store(self):
        for i in range(len(self.dict)):
            self.index.add_int(self.docs.next_free())
            self.index.add_int(self.docs.add_string(self.dict[i].arr))
