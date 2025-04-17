import unittest
from cpy import Prs

class TestPrs(unittest.TestCase):
    def to_str(self, input, fn = Prs.stmnt) -> str: return str(fn(Prs(input)))
    
    def test_uop(self):
        self.assertEqual(self.to_str("abc", Prs.expr), "Ref(abc)")
        self.assertEqual(self.to_str("1", Prs.expr), "Const(1)")
        self.assertEqual(self.to_str("-+p", Prs.expr), "UOp(-UOp(+Ref(p)))")
        self.assertEqual(self.to_str("-+9", Prs.expr), "UOp(-UOp(+Const(9)))")
    
    def test_bop(self):
        # arithmetic
        self.assertEqual(self.to_str("a+b", Prs.expr), "BOp(Ref(a)+Ref(b))")
        self.assertEqual(self.to_str("1+2", Prs.expr), "BOp(Const(1)+Const(2))")
        self.assertEqual(self.to_str("(1+2)", Prs.expr), "BOp(Const(1)+Const(2))")
        self.assertEqual(self.to_str("1+2+3", Prs.expr), "BOp(BOp(Const(1)+Const(2))+Const(3))")
        self.assertEqual(self.to_str("1+(2+3)", Prs.expr), "BOp(Const(1)+BOp(Const(2)+Const(3)))")
        self.assertEqual(self.to_str("(1+2)+3", Prs.expr), "BOp(BOp(Const(1)+Const(2))+Const(3))")
        self.assertEqual(self.to_str("(1+2)*3", Prs.expr), "BOp(BOp(Const(1)+Const(2))*Const(3))")
        self.assertEqual(self.to_str("11+22+33", Prs.expr), "BOp(BOp(Const(11)+Const(22))+Const(33))")
        self.assertEqual(self.to_str("11+22*33", Prs.expr), "BOp(Const(11)+BOp(Const(22)*Const(33)))")
        self.assertEqual(self.to_str("999*999*999*999", Prs.expr), "BOp(BOp(BOp(Const(999)*Const(999))*Const(999))*Const(999))")

        self.assertEqual(self.to_str("a=b=c;"), "BOp(Ref(a)=BOp(Ref(b)=Ref(c)))")
        self.assertEqual(self.to_str("a+=a+=3;"), "BOp(Ref(a)+=BOp(Ref(a)+=Const(3)))")
        self.assertEqual(self.to_str("c-=c-=33;"), "BOp(Ref(c)-=BOp(Ref(c)-=Const(33)))")
        # boolean logic
        self.assertEqual(self.to_str("a=b=c;"), "BOp(Ref(a)=BOp(Ref(b)=Ref(c)))")
    
    def test_variable(self):
        self.assertEqual(self.to_str("int a=*b;"), "Var(type=int,id=a,value=UOp(*Ref(b)))")
        self.assertEqual(self.to_str("int a=2;"), "Var(type=int,id=a,value=Const(2))")
        self.assertEqual(self.to_str("int a=2*b;"), "Var(type=int,id=a,value=BOp(Const(2)*Ref(b)))")
        self.assertEqual(self.to_str("int a=b+=1;"), "Var(type=int,id=a,value=BOp(Ref(b)+=Const(1)))")
    
    def test_fn(self):
        self.assertEqual(self.to_str("void f(){}"), "Fn(type=void,id=f,args=[],scope=Scope([]))")
        self.assertEqual(self.to_str("int g(float a,int b){}"), "Fn(type=int,id=g,args=[Arg(float a),Arg(int b)],scope=Scope([]))")
        self.assertEqual(self.to_str("float h(int a,int b){int c = a + b; b = 1; }"), "Fn(type=float,id=h,args=[Arg(int a),Arg(int b)],scope=Scope([Var(type=int,id=c,value=BOp(Ref(a)+Ref(b))),BOp(Ref(b)=Const(1))]))")
        self.assertEqual(self.to_str("int x = o(1) * p(987);"), "Var(type=int,id=x,value=BOp(Call(o,args=Const(1))*Call(p,args=Const(987))))")
    
    def test_ret(self): 
        self.assertEqual(self.to_str("return a*b;"), "Ret(BOp(Ref(a)*Ref(b)))")
        self.assertEqual(self.to_str("return 2;"), "Ret(Const(2))")
    
    def test_call(self):
        self.assertEqual(self.to_str("f();"), "Call(f,args=)")
        self.assertEqual(self.to_str("f(g());"), "Call(f,args=Call(g,args=))")
        self.assertEqual(self.to_str("f(1,*a, b += 3);"), "Call(f,args=Const(1),UOp(*Ref(a)),BOp(Ref(b)+=Const(3)))")
        self.assertEqual(self.to_str("f(g(1));"), "Call(f,args=Call(g,args=Const(1)))")

    def test_if(self): 
        self.assertEqual(self.to_str("if(1){}"), "If(test=Const(1),body=Scope([]),else=None)")
        self.assertEqual(self.to_str("if(x){}"), "If(test=Ref(x),body=Scope([]),else=None)")
        self.assertEqual(self.to_str("if(9==x){}"), "If(test=BOp(Const(9)==Ref(x)),body=Scope([]),else=None)")
        self.assertEqual(self.to_str("if(1){}else{}"), "If(test=Const(1),body=Scope([]),else=Scope([]))")
        self.assertEqual(self.to_str("if(1){}else{return 1;}"), "If(test=Const(1),body=Scope([]),else=Scope([Ret(Const(1))]))")
        self.assertEqual(self.to_str("if(1){}else if(2){}"), "If(test=Const(1),body=Scope([]),else=If(test=Const(2),body=Scope([]),else=None))")
        self.assertEqual(self.to_str("if(1){}else if(2){}else if(3){}"), "If(test=Const(1),body=Scope([]),else=If(test=Const(2),body=Scope([]),else=If(test=Const(3),body=Scope([]),else=None)))")
        self.assertEqual(self.to_str("if(x==1){}else if(y!=2){}else if(2==x){}"), "If(test=BOp(Ref(x)==Const(1)),body=Scope([]),else=If(test=BOp(Ref(y)!=Const(2)),body=Scope([]),else=If(test=BOp(Const(2)==Ref(x)),body=Scope([]),else=None)))")
    
    def test_scopes(self):
        self.assertEqual(self.to_str("{}"), "Scope([])") 
        self.assertEqual(self.to_str("{{}}"), "Scope([Scope([])])")
        self.assertEqual(self.to_str("{{}{}}"), "Scope([Scope([]),Scope([])])")

    def test_ref(self):
        self.assertEqual(self.to_str("a;"), "Ref(a)")

    def test_while(self):
        self.assertEqual(self.to_str("while(x<1){int a=2;}"), "While(test=BOp(Ref(x)<Const(1)),body=Scope([Var(type=int,id=a,value=Const(2))]))")

    def test_code(self): 
        code="""
        float f() { return 1.0f + 2.0f; }
        int* main() { return f(); }
        """
        stmts = list(Prs(code).parse())
        self.assertEqual(str(stmts[0]), "Fn(type=float,id=f,args=[],scope=Scope([Ret(BOp(Const(1.0)+Const(2.0)))]))")
        self.assertEqual(str(stmts[1]), "Fn(type=int*,id=main,args=[],scope=Scope([Ret(Call(f,args=))]))")

if __name__ == "__main__": 
    unittest.main(verbosity=0)