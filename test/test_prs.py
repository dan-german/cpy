import unittest
from cpy import Lex, Prs

class TestPrs(unittest.TestCase):
    def test_arith_expr(self):
        code = "1*2+-3"
        output = Prs(code).parse()

if __name__ == "__main__":
  unittest.main(verbosity=1)