#!/usr/bin/env python2
import argparse
import document_pb2
import struct
import gzip

import re

SPLIT_RGX = re.compile(r'\w+', re.U)


def extract_words(text):
    words = re.findall(SPLIT_RGX, text)
    return map(lambda s: s.lower(), words)


class Docs:
    def __init__(self, url, docid):
        self.url = url
        self.docid = docid


class DocumentStreamReader:
    def __init__(self, paths):
        self.paths = paths

    def open_single(self, path):
        return gzip.open(path, 'rb') if path.endswith('.gz') else open(path, 'rb')

    def __iter__(self):
        for path in self.paths:
            with self.open_single(path) as stream:
                while True:
                    sb = stream.read(4)
                    if sb == '':
                        break

                    size = struct.unpack('i', sb)[0]
                    msg = stream.read(size)
                    doc = document_pb2.document()
                    doc.ParseFromString(msg)
                    yield doc


def parse_command_line():
    parser = argparse.ArgumentParser(description='compressed documents reader')
    parser.add_argument('code', nargs=1, help='Coding option')
    parser.add_argument('files', nargs='+', help='Input files (.gz or plain) to process')
    return parser.parse_args()
