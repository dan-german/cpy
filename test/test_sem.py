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
      
   def test_var_redefinition(self): 
      with self.assertRaises(Redefinition):analyze(Prs("int a=1; int a=1;").parse())
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

   def test_global_vars(self): 
      _,global_vars,_ = self.analyze_code("int a;int b;int c;")
      self.assertEqual(global_vars, {"a":("int","a0"),"b":("int","b0"),"c":("int","c0")})

   def test_code1(self): 
      code = """
         int a(){
            int a=1;
            int b=2;
            {
               float a=2;
               float b=2;
            }
         }
      """
      expected_inner_scope = {
         "a":("int","a0"),
         "b":("int","b0")
      }
      expected_outer_scope = {
         "a":("float","a1"),
         "b":("float","b1")
      }
      ast,vars,functions = self.analyze_code(code)
      scopes1 = self.filter_scopes(ast)
      self.assertEqual(scopes1[0].sym,Sym(expected_inner_scope))
      self.assertEqual(scopes1[1].sym,Sym(expected_outer_scope))
      self.assertEqual(vars, {})
      self.assertEqual(functions, {"a":"int"})

   def test_code2(self): 
      code = """
         float a(){int a;}
         void b(){int b;}
         int glb = 1;
      """
      ast,vars,functions=self.analyze_code(code)
      scopes = self.filter_scopes(ast)
      self.assertEqual(scopes[0].sym,Sym({"a":("int","a0")}))
      self.assertEqual(scopes[1].sym,Sym({"b":("int","b0")}))
      self.assertEqual(vars, {"glb":("int","glb0")})
      self.assertEqual(functions, {"a":"float","b":"void"})

if __name__ == "__main__":
  unittest.main(verbosity=1)