#!/usr/bin/env python2
# coding=utf-8
from simple9 import Simple9
from storage import SimpleStorage, InMemoryHashTable
from varbyte import VarByte

url_index = SimpleStorage("url_index", "r")
urls = SimpleStorage("url_strings", "r")
words = InMemoryHashTable("words", "r")


def load_url(r):
    idx = url_index.get_int(2 * r)
    l = url_index.get_int(2 * r + 1)
    return urls.get_string(idx, l)


def parse_request(line):
    return


def invoke(line):
    return []


if __name__ == '__main__':

    fd = open("./docindex_", "r")
    if fd.read(7) == "varbyte":
        index = VarByte("docindex", "r")
    else:
        index = Simple9("docindex", "r")

    # l = 0
    # index.load(0)
    # while l != -1:
    #     l = index.get_next(0)
    #     print l

    import fileinput

    for line in fileinput.input():
        print words.get(line[:-1])
        # res = invoke(line)
        # print line
        # print len(res)
        # for r in res:
        #     print load_url(r)
