import unittest
from cpy.lex import Lex

class TestLex(unittest.TestCase):
    def test_lex(self):
        input = "int f(int a) { int b = a + 1.9f; return b * 2; }"
        expected = [
           ('int', 'type'), 
           ('f', 'id'), 
           ('(', 'op'), 
           ('int', 'type'), 
           ('a', 'id'), 
           (')', 'op'), 
           ('{', 'op'), 
           ('int', 'type'), 
           ('b', 'id'), 
           ('=', 'op'), 
           ('a', 'id'), 
           ('+', 'op'), 
           ('1.9', 'float_literal'), 
           (';', 'op'), 
           ('return', 'op'), 
           ('b', 'id'), 
           ('*', 'op'), 
           ('2', 'int_literal'), 
           (';', 'op'),
           ('}', 'op')
        ]

        tokens = [t for t in Lex(input)]
        self.assertEqual(tokens, expected)

if __name__ == '__main__':
  unittest.main(verbosity=2)