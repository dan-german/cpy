import unittest
from cpy.lex import Lex

class TestLex(unittest.TestCase):
    def assert_lex(self, *, code, expected): 
        tokens = list(map(lambda x: str(x), list(Lex(code))))
        self.assertEqual(tokens, expected)

    def test_lex(self):
        self.assert_lex(code="1 1.0 23 23. 45.6", expected=["NUM 1", "NUM 1.0", "NUM 23", "NUM 23.", "NUM 45.6"])
        self.assert_lex(code="auto break case", expected=["KEYWORD auto", "KEYWORD break", "KEYWORD case"])
        self.assert_lex(code="a aa a1 aa11", expected=["ID a", "ID aa", "ID a1", "ID aa11"])
        self.assert_lex(code=r'"a" "\"" "\n"', expected=[r'STR "a"', r'STR "\""', r'STR "\n"'])
        self.assert_lex(code="){,;", expected=["PUNCTUATION )", "PUNCTUATION {", "PUNCTUATION ,", "PUNCTUATION ;"])
        self.assert_lex(code="< > >= <= <<= >>= ^", expected=[ "OP <", "OP >", "OP >=", "OP <=", "OP <<=", "OP >>=", "OP ^"])
        self.assert_lex(code= "'a' 'b'", expected=["CHAR 'a'", "CHAR 'b'"])
        self.assert_lex(code= "//comment", expected=["COMMENT //comment"])

if __name__ == "__main__":
  unittest.main(verbosity=1)