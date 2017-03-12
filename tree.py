#!/usr/bin/env python2
import re
import unittest

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


class QTreeOperator(QtreeTypeInfo):
    def __init__(self, op):
        QtreeTypeInfo.__init__(self, op, op=True)
        self.priority = get_operator_prio(op)
        self.left = None
        self.right = None


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


""" Collect query tree to sting back. It needs for tests. """
def qtree2str(root, depth=0):
    if root.is_operator:
        need_brackets = depth > 0 and root.value != '!'
        res = ''
        if need_brackets:
            res += '('

        if root.left:
            res += qtree2str(root.left, depth+1)

        if root.value == '!':
            res += root.value
        else:
            res += ' ' + root.value + ' '

        if root.right:
            res += qtree2str(root.right, depth+1)

        if need_brackets:
            res += ')'

        return res
    else:
        return root.value

    
""" Test tokenizer and parser itself """
class QueryParserTest(unittest.TestCase):
    @staticmethod
    def parsed_tree(q):
        return qtree2str(parse_query(q)).decode('utf-8')

    def test_tokenizer(self):
        self.assertEqual(['foxy', '&', 'lady'], tokenize_query('foxy & lady'))
        self.assertEqual(['foxy', '&', 'lady', '|', 'madam'], tokenize_query('foxy & lady | madam'))
        self.assertEqual(['foxy', '&', '(', 'lady', '|', 'madam', ')'], tokenize_query('foxy & (lady | madam)'))
        self.assertEqual(['foxy', '&', '(', '!', 'lady', '|', 'madam', ')'], tokenize_query('foxy & (!lady | madam)'))

    def test_parser(self):
        self.assertEqual('foxy & lady', QueryParserTest.parsed_tree('foxy & lady'))
        self.assertEqual('(foxy & lady) | madam', QueryParserTest.parsed_tree('foxy & lady | madam'))
        self.assertEqual('foxy & (lady | madam)', QueryParserTest.parsed_tree('foxy & (lady | madam)'))

    def test_right_order(self):
        self.assertEqual('((one & two) & three) & four', QueryParserTest.parsed_tree('one & two & three & four'))

    def test_neg(self):
        self.assertEqual('foxy & !(lady | madam)', QueryParserTest.parsed_tree('foxy & !(lady | madam)'))


suite = unittest.TestLoader().loadTestsFromTestCase(QueryParserTest)
unittest.TextTestRunner().run(suite)
