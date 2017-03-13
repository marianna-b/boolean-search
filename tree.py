#!/usr/bin/env python2
import re

SPLIT_RGX = re.compile(r'\w+|[\(\)&\|!]', re.U)


class QtreeTypeInfo:
    def __init__(self, value, op=False, bracket=False, term=False, eof=False):
        self.value = value
        self.is_operator = op
        self.is_bracket = bracket
        self.is_term = term
        self.is_eof = eof

    def __repr__(self):
        return repr(self.value)

    def __eq__(self, other):
        if isinstance(other, QtreeTypeInfo):
            return self.value == other.value
        return self.value == other


class QTreeTerm(QtreeTypeInfo):
    def __init__(self, term):
        QtreeTypeInfo.__init__(self, term, term=True)
        self.stream = None
        self.curr = -1
        self.nothing = False

    def setup(self, index, words, length):
        id = words.get(self.value)
        if id == -1:
            self.curr = -2
        else:
            self.stream = index.load(id)

    def goto(self, docid):
        if self.nothing:
            return
        while self.curr < docid and self.curr != -2:
            self.curr = self.stream.get()
            if self.curr == -1:
                self.nothing = True
                self.curr = -2

    def eval(self):
        return self.curr


class QTreeOperator(QtreeTypeInfo):
    def __init__(self, op):
        QtreeTypeInfo.__init__(self, op, op=True)
        self.priority = get_operator_prio(op)
        self.left = None
        self.right = None
        self.docid = -1
        self.nothing = False

    def setup(self, index, words, length):
        self.length = length
        if self.left is not None:
            self.left.setup(index, words, length)
        if self.right is not None:
            self.right.setup(index, words, length)

    def goto(self, docid):
        if self.nothing or self.docid >= docid:
            return
        self.docid = docid
        if self.left is not None:
            self.left.goto(docid)
        if self.right is not None:
            self.right.goto(docid)

    def eval(self):
        if self.nothing:
            return -2
        if self.value == '!':
            res_right = self.right.eval()
            while self.docid == res_right:
                self.docid += 1
                self.right.goto(self.docid)
                res_right = self.right.eval()
            if self.docid < self.length:
                return self.docid
            else:
                self.nothing = True
                return -2
        if self.value == '&':
            res_left = self.left.eval()
            res_right = self.right.eval()
            while res_right != res_left:
                self.docid += 1 #= max(res_left, res_right)
                self.left.goto(self.docid)
                self.right.goto(self.docid)
                res_left = self.left.eval()
                res_right = self.right.eval()
            if res_left == -2:
                self.nothing = True
            return res_left
        if self.value == '|':
            res_left = self.left.eval()
            res_right = self.right.eval()
            if res_left == -2 or res_right == -2:
                self.nothing = True
            if res_left == -2:
                return res_right
            if res_right == -2:
                return res_left
            return min(res_left, res_right)


class QTreeBracket(QtreeTypeInfo):
    def __init__(self, bracket):
        QtreeTypeInfo.__init__(self, bracket, bracket=True)


class QTreeEOF(QtreeTypeInfo):
    def __init__(self):
        QtreeTypeInfo.__init__(self, "eof", eof=True)


class Parser:
    def __init__(self, tokens):
        self.pos = 0
        self.tokens = tokens

    def parse(self):
        return self.parse_prio(0)

    def parse_prio(self, prio):
        if prio == 2:
            return self.parse_term()
        left = self.parse_prio(prio + 1)
        while self.current_token().is_operator \
                and get_operator_prio(self.current_token().value) == prio:
            token = self.current_token()
            self.skip_token()
            right = self.parse_prio(prio + 1)
            token.left = left
            token.right = right
            left = token
        assert not self.current_token().is_term, "Parse error: %r" % self.current_token()
        return left

    def parse_term(self):
        token = self.current_token()
        if token.is_bracket and token.value == '(':
            self.skip_token()
            res = self.parse_prio(0)
            self.skip_token()
            return res
        elif token.is_operator and token.value == '!':
            self.skip_token()
            token.right = self.parse_term()
            return token
        elif token.is_term:
            self.skip_token()
            return token
        assert False, "Unknown token type: %r" % token

    def current_token(self):
        if self.pos >= len(self.tokens):
            return QTreeEOF()
        return self.tokens[self.pos]

    def skip_token(self):
        self.pos += 1


def get_operator_prio(s):
    if s == '|':
        return 0
    if s == '&':
        return 1
    if s == '!':
        return 2

    return None


def is_operator(s):
    return get_operator_prio(s) is not None


def tokenize_query(q):
    tokens = []
    for t in map(lambda w: w.encode('utf-8'), re.findall(SPLIT_RGX, q)):
        if t == '(' or t == ')':
            tokens.append(QTreeBracket(t))
        elif is_operator(t):
            tokens.append(QTreeOperator(t))
        else:
            tokens.append(QTreeTerm(t))

    return tokens


def build_query_tree(tokens):
    return Parser(tokens).parse()


def parse_query(q):
    tokens = tokenize_query(q)
    return build_query_tree(tokens)
