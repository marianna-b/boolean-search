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


class Simple9:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        if mode == "w+":
            fd1 = open("./" + filename + "_", mode)
            fd1.write("simple9")
            fd1.close()
        self.dict = {}
        self.waiting = {}
        self.last = {}
        self.tmpbuf = {}
        self.curr = {}
        self.prev = {}
        self.a = {}
        self.mode = mode

    def simple9_encode(self, word):
        global en_simple
        off = 0
        length = len(self.a[word])
        while off < length:
            for t in en_simple:
                n, threshold, code, shift = t[0], t[1], t[2], t[3]

                if off + n <= length and max(self.a[word][off:off + n]) <= t[1]:
                    tmp = self.a[word][off]
                    for i in xrange(1, n):
                        tmp |= (self.a[word][off + i] << (shift * i))
                    tmp |= t[2]
                    self.dict[word].append((tmp >> 24) & 0xff)
                    self.dict[word].append((tmp >> 16) & 0xff)
                    self.dict[word].append((tmp >> 8) & 0xff)
                    self.dict[word].append(tmp & 0xff)
                    off += n
                    break
        self.a[word] = self.a[word][:off]

    def add(self, word, doc):
        if not self.dict.has_key(word):
            self.dict[word] = bytearray()
            self.tmpbuf[word] = []
            self.a[word] = []
            self.curr[word] = 0
            self.prev[word] = 0
            self.last[word] = -1

        self.a[word].append(doc - max(0, self.last[word]))
        self.last[word] = doc
        if len(self.a[word]) > 27:
            self.simple9_encode(word)

    def simple9_decode(self, word):
        if len(self.dict[word]) <= self.curr[word]:
            return
        global de_simple
        t = 0
        for i in range(4):
            t <<= 8
            t |= self.dict[word][self.curr[word] + i]
        self.curr[word] += 4

        code = t & 0xf0000000
        data = t & 0xfffffff
        info = de_simple[code]
        n, bit, shift = info[0], info[1], info[2]

        for i in range(n):
            self.tmpbuf[word].append(data & bit)
            data >>= shift

    def load(self, word):
        index = SimpleStorage(self.filename + "_idx", self.mode)
        docs = SimpleStorage(self.filename, self.mode)
        idx = index.get_int(2 * word)
        l = index.get_int(2 * word + 1)
        self.tmpbuf[word] = []
        self.a[word] = []
        self.curr[word] = 0
        self.prev[word] = 0
        self.last[word] = -1
        self.dict[word] = bytearray()
        self.dict[word].extend(docs.get_string(idx, l))

    def forget(self, word):
        self.dict.pop(word)
        self.waiting.pop(word)
        self.last.pop(word)
        self.tmpbuf.pop(word)
        self.curr.pop(word)
        self.prev.pop(word)
        self.a.pop(word)

    def get_next(self, word):
        if len(self.tmpbuf[word]) == 0:
            self.simple9_decode(word)

        if len(self.tmpbuf[word]) == 0:
            return -1

        res = self.tmpbuf[word].pop(0)

        self.prev[word] += res
        return self.prev[word]

    def flush(self):
        for word in self.a:
            self.simple9_encode(word)