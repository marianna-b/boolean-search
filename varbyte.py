from storage import SimpleStorage


class VarByteElem:
    def __init__(self, arr):
        self.arr = arr
        self.curr = 0
        self.last = -1

    def get(self):
        if self.curr >= len(self.arr):
            return -1

        res = 0
        while self.arr[self.curr] < 128 and self.curr < len(self.arr):
            res <<= 7
            res |= self.arr[self.curr] & 0x7f
            self.curr += 1

        res <<= 7
        res |= self.arr[self.curr] & 0x7f
        self.curr += 1
        if self.last == -1:
            self.last = 0
        self.last += res
        return self.last


class VarByte:
    def __init__(self, filename, mode="w+"):
        self.filename = filename
        if mode == "w+":
            fd1 = open("./" + filename + "_", mode)
            fd1.write("varbyte")
            fd1.close()
        self.mode = mode
        self.index = SimpleStorage(self.filename + "_idx", self.mode)
        self.docs = SimpleStorage(self.filename, self.mode)

        self.dict = {}

    def add(self, word, doc):
        if not self.dict.has_key(word):
            self.dict[word] = VarByteElem(bytearray())
        elem = self.dict[word]

        i = doc - max(0, elem.last)
        elem.last = doc

        result = []
        while i >= 128:
            result.append(i & 0x7f)
            i >>= 7
        result.append(i & 0x7f)

        for r in reversed(range(1, len(result))):
            elem.arr.append(result[r])

        elem.arr.append(result[0] | 0x80)

    def load(self, word):
        idx = self.index.get_int(2 * word)
        l = self.index.get_int(2 * word + 1)
        tmp = bytearray()
        tmp.extend(self.docs.get_string(idx, l))
        return VarByteElem(tmp)

    def set(self, word):
        self.dict[word] = self.load(word)

    def forget(self, word):
        self.dict.pop(word)

    def get_next(self, word):
        return self.dict[word].get()

    def flush(self):
        pass

    def store(self):
        for i in range(len(self.dict)):
            self.index.add_int(self.docs.next_free())
            self.index.add_int(self.docs.add_string(self.dict[i].arr))