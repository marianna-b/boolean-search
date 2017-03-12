#!/usr/bin/env python2
from docreader import DocumentStreamReader, parse_command_line, extract_words
from simple9 import Simple9
from storage import SimpleStorage, InMemoryHashTable, store
from varbyte import VarByte

word_count = -1

url_index = SimpleStorage("url_index")
urls = SimpleStorage("url_strings")
words = InMemoryHashTable("words")


def add_doc(url):
    url_index.add_int(urls.next_free())
    url_index.add_int(urls.add_string(url))
    pass


def get_wordid(term):
    if not words.dict.has_key(term):
        global word_count
        word_count += 1
        words.add(term, word_count)
        print term + " " + str(word_count)
        return word_count
    return words.dict.get(term)


if __name__ == '__main__':
    cmd = parse_command_line()
    reader = DocumentStreamReader(cmd.files)
    if cmd.code[0] == "varbyte":
        index = VarByte("docindex")
    else:
        index = Simple9("docindex")

    doc_count = -1

    for doc in reader:
        doc_count += 1
        add_doc(doc.url)

        terms = set(extract_words(doc.text))

        for term in terms:
            tmp = get_wordid(term)
            #index.add(tmp, doc_count)

    #index.flush()
    #store(index.filename, index.dict)
    words.store()