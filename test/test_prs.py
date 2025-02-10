import unittest
from cpy import Prs
from cpy.lex import Tok
from cpy.debug import pn

class TestPrs(unittest.TestCase):
    def expr(self, input) -> str: return str(Prs(input).expr())
    def uop(self, input) -> str: return str(Prs(input).uop())
    def decl(self, input) -> str: return str(Prs(input).decl())

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

    def test_variable(self):
        self.assertEqual(self.decl("int a=2;"),"Var(type=int,id=a,value=2)")
        self.assertEqual(self.decl("int a=2*b;"),"Var(type=int,id=a,value=(2*b))")
        self.assertEqual(self.decl("int a=b+=1;"),"Var(type=int,id=a,value=(b+=1))")

    def test_func(self):
        self.assertEqual(self.decl("int f(){}"),"Func(type=int,id=f,args=[],stmts=[])")
        self.assertEqual(self.decl("int f(int a,int b){}"),"Func(type=int,id=f,args=[int a,int b],stmts=[])")
        self.assertEqual(self.decl("int f(int a,int b){int c = a + b; b = 1; }"),"Func(type=int,id=f,args=[int a,int b],stmts=[Var(type=int,id=c,value=(a+b)),(b=1)])")

if __name__ == "__main__": 
    unittest.main(verbosity=0)