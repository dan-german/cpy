import unittest
from cpy import Prs
from cpy.lex import Tok
from cpy.debug import pn

class TestPrs(unittest.TestCase):
    def to_str(self, input) -> str: return str(Prs(input).stmnt())
    
    def test_uop(self):
        self.assertEqual(self.to_str("abc"), "Ref(abc)")
        self.assertEqual(self.to_str("1"), "Const(1)")
        self.assertEqual(self.to_str("-+p"), "UOp(-UOp(+Ref(p)))")
        self.assertEqual(self.to_str("-+9"), "UOp(-UOp(+Const(9)))")
    
    def test_bop(self):
        self.assertEqual(self.to_str("a+b"), "BOp(Ref(a)+Ref(b))")
        self.assertEqual(self.to_str("1+2"), "BOp(Const(1)+Const(2))")
        self.assertEqual(self.to_str("(1+2)"), "BOp(Const(1)+Const(2))")
        self.assertEqual(self.to_str("1+2+3"), "BOp(BOp(Const(1)+Const(2))+Const(3))")
        self.assertEqual(self.to_str("1+(2+3)"), "BOp(Const(1)+BOp(Const(2)+Const(3)))")
        self.assertEqual(self.to_str("(1+2)+3"), "BOp(BOp(Const(1)+Const(2))+Const(3))")
        self.assertEqual(self.to_str("(1+2)*3"), "BOp(BOp(Const(1)+Const(2))*Const(3))")
        self.assertEqual(self.to_str("11+22+33"), "BOp(BOp(Const(11)+Const(22))+Const(33))")
        self.assertEqual(self.to_str("11+22*33"), "BOp(Const(11)+BOp(Const(22)*Const(33)))")
        self.assertEqual(self.to_str("999*999*999*999"), "BOp(BOp(BOp(Const(999)*Const(999))*Const(999))*Const(999))")

        self.assertEqual(self.to_str("a=b=c;"), "BOp(Ref(a)=BOp(Ref(b)=Ref(c)))")
        self.assertEqual(self.to_str("a+=a+=3;"), "BOp(Ref(a)+=BOp(Ref(a)+=Const(3)))")
        self.assertEqual(self.to_str("c-=c-=33;"), "BOp(Ref(c)-=BOp(Ref(c)-=Const(33)))")
    
    def test_variable(self):
        self.assertEqual(self.to_str("int a=2;"), "Var(type=int,id=a,value=Const(2))")
        self.assertEqual(self.to_str("int a=2*b;"), "Var(type=int,id=a,value=BOp(Const(2)*Ref(b)))")
        self.assertEqual(self.to_str("int a=b+=1;"), "Var(type=int,id=a,value=BOp(Ref(b)+=Const(1)))")
    
    def test_func(self):
        self.assertEqual(self.to_str("int f(){}"), "Func(type=int,id=f,args=[],stmts=[])")
        self.assertEqual(self.to_str("int g(int a,int b){}"), "Func(type=int,id=g,args=[Arg(int a),Arg(int b)],stmts=[])")
        self.assertEqual(self.to_str("int h(int a,int b){int c = a + b; b = 1; }"), "Func(type=int,id=h,args=[Arg(int a),Arg(int b)],stmts=[Var(type=int,id=c,value=BOp(Ref(a)+Ref(b))),BOp(Ref(b)=Const(1))])")
        self.assertEqual(self.to_str("int x = o(1) * p(987);"), "Var(type=int,id=x,value=BOp(Call(Ref(o),args=Const(1))*Call(Ref(p),args=Const(987))))")
    
    def test_return(self): 
        self.assertEqual(self.to_str("return 2;"), "Return(Const(2))")
    
    def test_call(self):
        self.assertEqual(self.to_str("f();"), "Call(Ref(f),args=)")
        self.assertEqual(self.to_str("f(g());"), "Call(Ref(f),args=Call(Ref(g),args=))")
        self.assertEqual(self.to_str("f(1,a, b += 3);"), "Call(Ref(f),args=Const(1),Ref(a),BOp(Ref(b)+=Const(3)))")
        self.assertEqual(self.to_str("f(g(1));"), "Call(Ref(f),args=Call(Ref(g),args=Const(1)))")
    
    def test_code(self): 
        code="""
        int f() { return 1 + 2; }
        int main() { return f(); }
        """
        stmnts = Prs(code).parse()
        self.assertEqual(str(stmnts[0]), "Func(type=int,id=f,args=[],stmts=[Return(BOp(Const(1)+Const(2)))])")
        self.assertEqual(str(stmnts[1]), "Func(type=int,id=main,args=[],stmts=[Return(Call(Ref(f),args=))])")

if __name__ == "__main__": 
    unittest.main(verbosity=0)