import struct

from storage import SimpleStorage


class VarByte:
    def __init__(self, filename):
        self.filename = filename
        fd1 = open("./" + filename + "_", "r+")
        fd1.write("varbyte")
        fd1.close()
        self.dict = {}
        self.last = {}

        self.next = {}
        self.prev = {}

    def add(self, word, doc):

        if not self.dict.has_key(word):
            self.dict[word] = bytearray()
            self.next[word] = 0
            self.prev[word] = 0
            self.last[word] = -1

        i = doc - max(0, self.last[word])
        self.last[word] = doc

        result = []
        if i >= 128:
            result.append(i & 0x7f)
            i >>= 7
            while i >= 128:
                result.append(i & 0x7f)
                i >>= 7
            result.append(i & 0x7f)
        else:
            result.append(i)

        for r in range(len(result) - 1):
            self.dict[word].extend(struct.pack("c", result[r]))
        self.dict[word].extend(struct.pack("c", result[0] | 0x80))

    def flush(self):
        pass

    def load(self, word):
        index = SimpleStorage(self.filename + "_idx")
        docs = SimpleStorage(self.filename)
        idx = index.get_int(2 * word)
        l = idx.get_int(2 * word + 1)
        self.prev[word] = 0
        self.last[word] = -1
        self.dict[word] = bytearray()
        self.dict[word].extend(docs.get_string(idx, l))

    def forget(self, word):
        self.dict.pop(word)
        self.last.pop(word)
        self.prev.pop(word)

    def get_next(self, word):
        if self.next[word] >= len(self.dict[word]):
            return -1

        res = 0
        while self.dict[word][self.next[word]] < 128 and self.next[word] < len(self.dict[word]):
            res <<= 7
            res += self.dict[word][self.next[word]] & 0x7f
            self.next[word] += 1

        res <<= 7
        res += self.dict[word][self.next[word]] & 0x7f
        self.prev[word] += res
        return self.prev[word]
