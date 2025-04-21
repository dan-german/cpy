import unittest
import cpy.prs as prs
import cpy.sem as sem
from cpy.tac import *

class TestTac(unittest.TestCase):
    def to_tac(self,code:str): return to_tac(sem.analyze(list(prs.Prs(code).parse())))

    def test1(self): 
        code =\
        """
        int main() {
            int a = 2;
            int b = a * a;
            a = 3;
            b = b + a;
            return a + b;
        }
        """
        self.assertEqual(self.to_tac(code).functions[0].code, [
            TACAssign(id='a0', value=Const(value='2'), op='='), 
            TACOp(id='G0', left='a0', op='*', right='a0'), 
            TACAssign(id='b0', value='G0', op='='), 
            TACAssign(id='a0', value=Const(value='3'), op='='), 
            TACOp(id='G1', left='b0', op='+', right='a0'), 
            TACAssign(id='b0', value='G1', op='='), 
            TACOp(id='G2', left='a0', op='+', right='b0'), 
            TACRet(value='G2')
        ])

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

        self.assertEqual(f1.code,[
            TACOp(id='G0', left='x0', op='*', right=Const(value='2')), 
            TACOp(id='G1', left='G0', op='*', right='x0'), 
            TACRet(value='G1')
        ])

        f2 = tac_table.functions[1]
        self.assertEqual(f2.args,[TACArg("int", "x1")])
        self.assertEqual(f2.code,[
            TACCall("f1", ["x1"], "G0"),
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

        self.assertEqual(main.code, [
            TACAssign(id='x0', value=Const(value='0'), op='='), 
            TACAssign(id='x0', value=Const(value='2'), op='='),
            TACAssign(id='y0', value='x0', op='='),
            TACAssign(id='y0', value='x0', op='='),
            TACOp(id='G0', left='x0', op='+', right='y0'),
            TACRet(value='G0')
        ])

    def test_if(self): 
        code =\
        """
        int main() { 
            int x = 0;
            if (x < 0) { 
                x = 1;
            } else { 
                x = 2;
            }
            return x;
        }
        """
        tac_table = self.to_tac(code)
        self.assertEqual(tac_table.functions[0].code, [
            TACAssign(id='x0', value=Const(value='0'), op='='), 
            TACOp(id='G0', left='x0', op='<', right=Const(value='0')), 
            TACCondJump(value='G0', target='if_then_0', last_test_op='<'), 
            TACAssign(id='x0', value=Const(value='2'), op='='), 
            TACJump(target='if_exit_0'), 
            TACLabel(label='if_then_0'), 
            TACAssign(id='x0', value=Const(value='1'), op='='), 
            TACJump(target='if_exit_0'), 
            TACLabel(label='if_exit_0'), 
            TACRet(value='x0')])

    def test_while(self):
        code =\
        """
        int main() { 
            int x = 1;
            int i = 0;
            while (i < 2) { 
                x *= 2;
                i+=1;
            }
            return x;
        }
        """
        tac_table = self.to_tac(code)
        self.assertEqual(tac_table.functions[0].code, [
            TACAssign(id='x0', value=Const(value='1'), op='='), 
            TACAssign(id='i0', value=Const(value='0'), op='='), 
            TACLabel(label='loop_start_0'), 
            TACOp(id='G0', left='i0', op='<', right=Const(value='2')), 
            TACCondJump(value='G0', target='loop_do_0', last_test_op='<'), 
            TACJump(target='loop_exit_0'), 
            TACLabel(label='loop_do_0'), 
            TACAssign(id='x0', value=Const(value='2'), op='*='), 
            TACAssign(id='i0', value=Const(value='1'), op='+='), 
            TACJump(target='loop_start_0'), 
            TACLabel(label='loop_exit_0'), 
            TACRet(value='x0')
        ])

        code =\
        """
        int main() { 
            int x = 1;
            int i = 0;
            while (i < 2) { 
                int j = 3;
                x *= 2;
                while (j != 0) { 
                    x *= 2;
                    j -= 1;
                }
                i+=1;
            }
            return x;
        }
        """

        tac_table = self.to_tac(code)
        print(tac_table.functions[0].code)
        self.assertEqual(tac_table.functions[0].code, [
            TACAssign(id='x0', value=Const(value='1'), op='='), 
            TACAssign(id='i0', value=Const(value='0'), op='='), 
            TACLabel(label='loop_start_0'), 
            TACOp(id='G0', left='i0', op='<', right=Const(value='2')), 
            TACCondJump(value='G0', target='loop_do_0', last_test_op='<'), 
            TACJump(target='loop_exit_0'), 
            TACLabel(label='loop_do_0'), 
            TACAssign(id='j0', value=Const(value='3'), op='='), 
            TACAssign(id='x0', value=Const(value='2'), op='*='), 
            TACLabel(label='loop_start_1'), 
            TACOp(id='G1', left='j0', op='!=', right=Const(value='0')), 
            TACCondJump(value='G1', target='loop_do_1', last_test_op='!='), 
            TACJump(target='loop_exit_1'), 
            TACLabel(label='loop_do_1'), 
            TACAssign(id='x0', value=Const(value='2'), op='*='), 
            TACAssign(id='j0', value=Const(value='1'), op='-='), 
            TACJump(target='loop_start_1'), 
            TACLabel(label='loop_exit_1'), 
            TACAssign(id='i0', value=Const(value='1'), op='+='), 
            TACJump(target='loop_start_0'), 
            TACLabel(label='loop_exit_0'), 
            TACRet(value='x0')
        ])

if __name__ == "__main__":
  unittest.main(verbosity=1)