from storage import SimpleStorage, InMemoryHashTable

url_index = SimpleStorage("url_index")
urls = SimpleStorage("url_strings")
words = InMemoryHashTable("words")


def load_url(r):
    idx = url_index.get_int(2 * r)
    l = url_index.get_int(2 * r + 1)
    return urls.get_string(idx, l)


def parse_request(line):
    return


def invoke(line):
    return []


if __name__ == '__main__':
    import fileinput

    for line in fileinput.input():
        res = invoke(line)
        print line
        print len(res)
        for r in res:
            print load_url(r)
