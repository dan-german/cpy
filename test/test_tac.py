import unittest
import cpy.prs as prs
import cpy.sem as sem
from cpy.tac import *

class TestTac(unittest.TestCase):
    def to_tac(self,code:str): return to_tac(sem.analyze(list(prs.Prs(code).parse())))

    def test_fn_and_arith(self):
        code =\
        """
        int a = 3;
        int b = 4;
        int f1(int x) {return x*2*x;}
        int f2(int x) {return f1(x);}
        """
        tac_table = self.to_tac(code)
        self.assertEqual(len(tac_table.globals),2)
        self.assertEqual(len(tac_table.functions),2)
        self.assertEqual(tac_table.globals[0], TACGlobal("a", prs.Const("3")))
        self.assertEqual(tac_table.globals[1], TACGlobal("b", prs.Const("4")))

        f1 = tac_table.functions[0]
        self.assertEqual(f1.args,[TACArg("int", "x0")])
        self.assertEqual(f1.block,[
            TACAssign("G0",Const("2")),
            TACOp("G1","x0","*","G0"),
            TACOp("G2","G1","*","x0"),
            TACRet("G2")
        ])

        f2 = tac_table.functions[1]
        self.assertEqual(f2.args,[TACArg("int", "x1")])
        self.assertEqual(f2.block,[
            TACCall("f1", [TACRef("x1")], "G0"),
            TACRet("G0")
        ])

    def test_reassignment(self): 
        code =\
        """
        int main() { 
            int x = 0;
            x = 2;
            int y = x;
            y = x;
            return x + y;
        }
        """
        tac_table = self.to_tac(code)
        main = tac_table.functions[0]
        self.assertEqual(main.block, [
            TACAssign("G0",Const("0")),
            TACAssign("x0",TACRef("G0")),
            TACAssign("G1",Const("2")),
            TACAssign("x0",TACRef("G1")),
            TACAssign("y0",TACRef("x0")),
            TACAssign("y0",TACRef("x0")),
            TACOp("G2", "x0", "+", "y0"),
            TACRet("G2")
        ])

    def test_branch(self): 
        code =\
        """
        int main() { 
            int x = 0;
            if (1 == 2) { x = 1; } else { x = 2; }
            return x;
        }
        """
        tac_table = self.to_tac(code)
        print(tac_table)

if __name__ == "__main__":
  unittest.main(verbosity=1)