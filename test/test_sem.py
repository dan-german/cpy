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
        with self.assertRaises(Undeclared):analyze(Prs("int main(){a();}").parse())
        analyze(Prs("void a(){}int main(){a();}").parse()) # assert ok

    def test_args_miscount(self): 
        with self.assertRaises(ArgsMiscount):analyze(Prs("int a(int a){}void main(){a(1,2);}").parse())
        with self.assertRaises(ArgsMiscount):analyze(Prs("int a(){}void main(){a(1);}").parse())
        analyze(Prs("int a(){}void main(){a();}").parse()) # assert ok

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
        functions = self.analyze_code("void a(){}int b(){}int c(){}")[2]
        self.assertEqual(len(functions),3)
        self.assertIn("a",functions)
        self.assertIn("b",functions)
        self.assertIn("c",functions)
        self.assertIsInstance(functions["a"],Fn)
        self.assertIsInstance(functions["b"],Fn)
        self.assertIsInstance(functions["c"],Fn)
        self.assertEqual(functions["a"].type,"void")
        self.assertEqual(functions["b"].type,"int")
        self.assertEqual(functions["c"].type,"int")

    def test_tables1(self): 
        _, globals_dict,_,_ = self.analyze_code("int a;int b;int c;")
        expected_globals = {
           "a": Symbol(id="a0", type="int", scope="global"),
           "b": Symbol(id="b0", type="int", scope="global"),
           "c": Symbol(id="c0", type="int", scope="global")
        }
        self.assertEqual(globals_dict, expected_globals)

    def test_tables2(self): 
        ast, globals_dict, functions,_ = self.analyze_code("int a;int f(){int a;}")
        self.assertEqual(globals_dict, {"a": Symbol(id='a0', type='int', scope='global')})
        self.assertIsInstance(functions["f"], Fn)
        scopes = self.filter_scopes(ast)
        self.assertEqual(scopes[0].sym, {"a": Symbol(id="a1", type="int", scope="local")})

    def test_tables3(self): 
        ast, globals_dict, functions,_ = self.analyze_code("int f(){int a; {int a;}}int a;")
        self.assertEqual(globals_dict, {"a": Symbol(id="a2", type="int", scope="global")})
        self.assertIsInstance(functions["f"], Fn)
        scopes = self.filter_scopes(ast)
        self.assertEqual(scopes[0].sym, {"a": Symbol(id="a0", type="int", scope="local")})
        self.assertEqual(scopes[1].sym, {"a": Symbol(id="a1", type="int", scope="local")})

    def test_all_symbols(self):
        _, _, _, all_symbols = self.analyze_code("int f(){int a; {int a;}}int a; int f2(int a){}int f3(){int a=0;}")
        expected = {'a0': Symbol(id='a0', type='int', scope='local'), 
                    'a1': Symbol(id='a1', type='int', scope='local'), 
                    'a2': Symbol(id='a2', type='int', scope='global'), 
                    'a3': Symbol(id='a3', type='int', scope='arg'), 
                    'a4': Symbol(id='a4', type='int', scope='local')} 
        self.assertEqual(all_symbols,expected)

    def test_params(self):
        ast, _, _,_ = self.analyze_code("void f(int a,float b){}")
        scopes = self.filter_scopes(ast)
        self.assertEqual(scopes[0].sym, {
           "a": Symbol(id="a0", type="int", scope="arg"),
           "b": Symbol(id="b0", type="float", scope="arg")
        })

    # def test_params(self):
    #    ast,_,_ = self.analyze_code("void f(int f()){}")
    #    scopes = self.filter_scopes(ast)
    #    self.assertEqual(str(scopes[0].sym),"a:(int,a0,arg),b:(float,b0,arg)") 

if __name__ == "__main__":
  unittest.main(verbosity=1)