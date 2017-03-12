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
    if words.dict.has_key(term):
        word_count.__add__(1)
        words.add(term, word_count)
        return word_count
    return words.dict.get(term)


if __name__ == '__main__':
    cmd = parse_command_line()
    reader = DocumentStreamReader(cmd.files)
    if cmd.code == "varbyte":
        index = VarByte("docindex")
    else:
        index = Simple9("docindex")

    doc_count = -1

    for doc in reader:
        doc_count += 1
        add_doc(doc.url)

        terms = set(extract_words(doc.text))

        for term in terms:
            index.add(get_wordid(term), doc_count)

    store(index.filename, index.dict)