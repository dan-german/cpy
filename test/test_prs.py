import unittest
from cpy import Lex, Prs
from cpy.lex import Tok
from cpy.classes import *
from cpy.debug import pn

class TestPrs(unittest.TestCase):
    def expr(self, input) -> str: return str(Prs(input).expr())
    def uop(self, input) -> str: return str(Prs(input).uop())

    def test_uop(self):
        self.assertEqual(self.uop("abc"),"abc")
        self.assertEqual(self.uop("1"),"1")
        self.assertEqual(self.uop("-+p"),"(-(+p))")
        self.assertEqual(self.uop("-+9"),"(-(+9))")
    
    def test_bop(self):
        self.assertEqual(self.expr("a+b"), "(a+b)")
        self.assertEqual(self.expr("1+2"), "(1+2)")
        self.assertEqual(self.expr("(1+2)"), "(1+2)")
        self.assertEqual(self.expr("1+2+3"), "((1+2)+3)")
        self.assertEqual(self.expr("1+(2+3)"), "(1+(2+3))")
        self.assertEqual(self.expr("(1+2)+3"), "((1+2)+3)")
        self.assertEqual(self.expr("(1+2)*3"), "((1+2)*3)")
        self.assertEqual(self.expr("11+22+33"), "((11+22)+33)")
        self.assertEqual(self.expr("11+22*33"), "(11+(22*33))")
        self.assertEqual(self.expr("999*999*999*999"), "(((999*999)*999)*999)")
        self.assertEqual(self.expr("a=b=c"), "(a=(b=c))")
        self.assertEqual(self.expr("a+=a+=3"),"(a+=(a+=3))")
        self.assertEqual(self.expr("c-=c-=33"),"(c-=(c-=33))")

if __name__ == "__main__": 
    unittest.main(verbosity=0)