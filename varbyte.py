import struct

from storage import SimpleStorage


class VarByte:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        if mode == "w+":
            fd1 = open("./" + filename + "_", mode)
            fd1.write("varbyte")
            fd1.close()
        self.dict = {}
        self.last = {}
        self.mode = mode

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
        while i >= 128:
            result.append(i & 0x7f)
            i >>= 7
        result.append(i & 0x7f)

        for r in reversed(range(1, len(result))):
            self.dict[word].append(result[r])

        self.dict[word].append(result[0] | 0x80)

    def flush(self):
        pass

    def load(self, word):
        index = SimpleStorage(self.filename + "_idx", self.mode)
        docs = SimpleStorage(self.filename, self.mode)
        idx = index.get_int(2 * word)
        l = index.get_int(2 * word + 1)
        self.prev[word] = 0
        self.next[word] = 0
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
            res |= self.dict[word][self.next[word]] & 0x7f
            self.next[word] += 1

        res <<= 7
        res |= self.dict[word][self.next[word]] & 0x7f
        self.next[word] += 1
        self.prev[word] += res
        return self.prev[word]
