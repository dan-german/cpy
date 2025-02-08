import unittest
from cpy import Lex, Prs
from cpy.lex import Tok
from cpy.classes import *

class TestPrs(unittest.TestCase):
    def test_var(self):
        self.assertEqual(Prs("int a=+-1;").parse(), VarDecl("a", "int", UOp("+", UOp("-", Const("1")))))
        self.assertEqual(Prs("int a=13;").parse(), VarDecl("a", "int", Const("13")))
        self.assertEqual(Prs("int a=1+2*3;").parse(), VarDecl("a", "int", BinOp("+", Const("1"), BinOp("*", Const("2"), Const("3")))))
        self.assertEqual(Prs("int a=1*2*3;").parse(), VarDecl("a", "int", BinOp("*", BinOp("*", Const("1"), Const("2")), Const("3"))))
        self.assertEqual(Prs("int aa=10*22+33;").parse(), VarDecl("aa", "int", BinOp("+", BinOp("*", Const("10"), Const("22")), Const("33"))))
        self.assertEqual(Prs("int a=(1+2)*3").parse(), VarDecl("a", "int", BinOp("*", BinOp("+", Const("1"), Const("2")), Const("3"))))
        self.assertEqual(Prs("int a=(1+(2-1))*3").parse(), VarDecl("a", "int", BinOp("*", BinOp("+", Const("1"), BinOp("-", Const("2"), Const("1"))), Const("3"))))
        self.assertEqual(Prs("int a=(1+(2-1))*3").parse(), VarDecl("a", "int", BinOp("*", BinOp("+", Const("1"), BinOp("-", Const("2"), Const("1"))), Const("3"))))

    def test_func(self): 
        code = """
        int a(int b, int c) {
            return b * c;
        }
"""

if __name__ == "__main__": 
    unittest.main(verbosity=1)