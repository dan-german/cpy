import unittest
from cpy.sem import *
from cpy.prs import Prs
from cpy.vst import bfs

class TestSem(unittest.TestCase):
   ########################    ERRORS    ########################
   def test_undeclared_vars(self): 
      with self.assertRaises(Undeclared):analyze(Prs("a;").parse())
      with self.assertRaises(Undeclared):analyze(Prs("int f(){a;}").parse())
      with self.assertRaises(Undeclared):analyze(Prs("int f(){{int b = 2;}b;}").parse())
      with self.assertRaises(Undeclared):analyze(Prs("int f(){a;} int a = 1;").parse())
      with self.assertRaises(Undeclared):analyze(Prs("int f(){return a;} int a = 1;").parse())
      
   def test_undeclared_fn(self): 
      with self.assertRaises(Undeclared):analyze(Prs("int main() { a(); }").parse())
      analyze(Prs("void a(){}int main() { a(); }").parse()) # assert ok

   def test_var_redefinition(self): 
      with self.assertRaises(Redefinition):analyze(Prs("int a; int a;").parse())
      with self.assertRaises(Redefinition):analyze(Prs("void f(){int a; int a;}").parse())
      with self.assertRaises(Redefinition):analyze(Prs("void f(int a){int a;}").parse())
      with self.assertRaises(Redefinition):analyze(Prs("int a(){}int a(){}").parse())
      with self.assertRaises(Redefinition):analyze(Prs("void f(){int c=1; int c=1;}").parse())
      with self.assertRaises(Redefinition):analyze(Prs("int a(){} int a=3;").parse())
      with self.assertRaises(Redefinition):analyze(Prs("int a=1;int a(){}").parse())

   def test_fn_def_unallowed(self):
      with self.assertRaises(DefUnallowed):analyze(Prs("int a(){int b(){}}").parse())

   def test_global_scopes(self):
      with self.assertRaises(GlobalScope):analyze(Prs("{}").parse())
      with self.assertRaises(GlobalScope):analyze(Prs("{{}}").parse())

   ########################    SYMBOL TABLES    ########################
   def analyze_code(self,code): return analyze(list(Prs(code).parse()))
   def filter_scopes(self,ast): return [node for node,_ in bfs(ast) if isinstance(node,Scope)]

   def test_functions(self):
      self.assertEqual(self.analyze_code("void a(){}int b(){}int c(){}")[2],{"a":"void","b":"int","c":"int"})

   def test_tables1(self): 
      self.assertEqual(str(self.analyze_code("int a;int b;int c;")[1]), "a:(int,a0,global),b:(int,b0,global),c:(int,c0,global)")

   def test_tables2(self): 
      ast,globals,functions = self.analyze_code("int a;int f(){int a;}")
      self.assertEqual(str(globals), "a:(int,a0,global)")
      self.assertEqual(functions, {"f": "int"})
      scopes = self.filter_scopes(ast)
      self.assertEqual(str(scopes[0].sym),"a:(int,a1,local)")

   def test_tables3(self): 
      ast,globals,functions = self.analyze_code("int f(){int a; {int a;}}int a;")
      self.assertEqual(str(globals), "a:(int,a2,global)")
      self.assertEqual(functions, {"f": "int"})
      scopes = self.filter_scopes(ast)
      self.assertEqual(str(scopes[0].sym),"a:(int,a0,local)")
      self.assertEqual(str(scopes[1].sym),"a:(int,a1,local)")

   def test_params(self):
      ast,_,_ = self.analyze_code("void f(int a,float b){}")
      scopes = self.filter_scopes(ast)
      self.assertEqual(str(scopes[0].sym),"a:(int,a0,arg),b:(float,b0,arg)")

   # def test_params(self):
   #    ast,_,_ = self.analyze_code("void f(int f()){}")
   #    scopes = self.filter_scopes(ast)
   #    self.assertEqual(str(scopes[0].sym),"a:(int,a0,arg),b:(float,b0,arg)") 

if __name__ == "__main__":
  unittest.main(verbosity=1)