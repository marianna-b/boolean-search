#!/usr/bin/env python2
# coding=utf-8
import os

import sys

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

    length = os.path.getsize(url_index.filename) / 8
    lines = []
    for line in sys.stdin.readlines():
        root = parse_query(line[:-1].decode("utf-8").lower())

        res = []
        root.setup(index, words, length)
        i = -1
        while i != -2:
            root.goto(i + 1)
            i = root.eval()
            if i != -2:
                res.append(i)
        lines.append(line[:-1])
        lines.append(str(len(res)))
        lines.extend(map(lambda s: load_url(s), res))
    print "\n".join(lines)