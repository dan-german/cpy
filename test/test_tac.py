import unittest
from cpy.lex import Lex
from cpy.tac import TACGen

class TestTac(unittest.TestCase):
    def test_tac(self): 
        self.assertEqual(TACGen("1 * 2 + 3 * 9").generate(),[('t0', '1', '*', '2'), ('t1', '3', '*', '9'), ('t2', 't0', '+', 't1')])

if __name__ == "__main__":
  unittest.main(verbosity=1)