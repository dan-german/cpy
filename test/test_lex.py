import unittest
from cpy.lex import Lex

class TestLex(unittest.TestCase):
    def assert_lex(self, *, code, exp): 
        tokens = list(Lex(code))
        expected_token_pairs = [tuple(s.split(" ")) for s in exp]
        self.assertEqual(tokens, expected_token_pairs)

    def test_keywords(self): 
        self.assert_lex(
           code="auto break case",
           exp=["KEYWORD auto", "KEYWORD break", "KEYWORD case"]
        )

    def test_identifiers(self): 
        self.assert_lex(
           code="a aa a1 aa11",
           exp=["ID a", "ID aa", "ID a1", "ID aa11"]
        )

    def test_nums(self): 
        self.assert_lex(
           code="1 1.0 23 23. 45.6",
           exp=["NUM 1", "NUM 1.0", "NUM 23", "NUM 23.", "NUM 45.6"]
        )

    def test_strings(self):
        self.assert_lex(
            code=r'"a" "\"" "\n"',
            exp=[r'STR "a"', r'STR "\""', r'STR "\n"']
        )

    def test_punctuation(self): 
        self.assert_lex(
           code="){,;",
           exp=["PUNCTUATION )", "PUNCTUATION {", "PUNCTUATION ,", "PUNCTUATION ;"]
        )

    def test_ops(self): 
        self.assert_lex(
           code="< > >= <= <<= >>= ^",
           exp=[ "OP <", "OP >", "OP >=", "OP <=", "OP <<=", "OP >>=", "OP ^"]
        )

    def test_whitespace(self): 
        self.assert_lex(
           code= "    ",
           exp=[]
        )

    def test_char(self): 
        self.assert_lex(
           code= "'a' 'b'",
           exp=["CHAR 'a'", "CHAR 'b'"]
        )

    def test_comments(self): 
        self.assert_lex(
           code= "//comment",
           exp=["COMMENT //comment"]
        )

if __name__ == "__main__":
  unittest.main(verbosity=1)