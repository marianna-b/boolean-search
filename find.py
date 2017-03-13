#!/usr/bin/env python2
# coding=utf-8
import os

from simple9 import Simple9
from storage import SimpleStorage, InMemoryHashTable
from tree import parse_query
from varbyte import VarByte

url_index = SimpleStorage("url_index", "r")
urls = SimpleStorage("url_strings", "r")
words = InMemoryHashTable("words", "r")


def load_url(r):
    idx = url_index.get_int(2 * r)
    l = url_index.get_int(2 * r + 1)
    return urls.get_string(idx, l)

# def invoke(root, depth=0):
#     if root.is_operator:
#         if root.value == '!' and root.right.value == '!':
#             return invoke(root.right.right, depth)
#
#         need_brackets = depth > 0 and root.value != '!'
#         res = ''
#         if need_brackets:
#             res += '('
#
#         if root.left:
#             res += qtree2str(root.left, depth+1)
#
#         if root.value == '!':
#             res += root.value
#         else:
#             res += ' ' + root.value + ' '
#
#         if root.right:
#             res += qtree2str(root.right, depth+1)
#
#         if need_brackets:
#             res += ')'
#
#         return res
#     else:
#         return root.value


if __name__ == '__main__':

    fd = open("./docindex_", "r")
    if fd.read(7) == "varbyte":
        index = VarByte("docindex", "r")
    else:
        index = Simple9("docindex", "r")

    import fileinput

    length = os.path.getsize(url_index.filename) / 8

    l = 0
    index.set(7000)
    while l >= 0:
        l = index.get_next(7000)
        print l

    for line in fileinput.input():
        print words.get(line[:-1])
        # root = parse_query(line[:-1])
        # i = -1
        # res = []
        # while i < length:
        #     i = root.evaluate()
        #     res.append(i)
        # print line
        # print len(res)
        # for r in res:
        #     print load_url(r)
