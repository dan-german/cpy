import unittest
import cpy.prs as prs
import cpy.sem as sem
from cpy.tac import *

class TestTac(unittest.TestCase):
    def to_tac(self,code:str): return to_tac(sem.analyze(list(prs.Prs(code).parse())))

    def test_a(self):
        code = """\
        int a = 3;
        int b = 4;
        int f1(int x) {return x*2;}
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
            TACRet("G1")
        ])

        f2 = tac_table.functions[1]
        self.assertEqual(f2.args,[TACArg("int", "x1")])
        self.assertEqual(f2.block,[
            TACCall("f1", [TACRef("x1")], "G0"),
            TACRet("G0")
        ])

    def test_a(self):
        code = """\
        int f1() {
            int x = 0;
            return x*x;
        }
        """
        tac_table = self.to_tac(code)
        self.assertEqual(len(tac_table.globals),0)
        self.assertEqual(len(tac_table.functions),1)
        f1 = tac_table.functions[0]
        self.assertEqual(f1.args,[])
        self.assertEqual(f1.block,[
            TACAssign("G0",Const("0")),
            TACAssign("x0",TACRef("G0")),
            TACOp("G1","x0","*","x0"),
            TACRet("G1")
        ])

if __name__ == "__main__":
  unittest.main(verbosity=1)