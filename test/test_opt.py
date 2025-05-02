import unittest
from cpy import Prs, sem, tac, opt
from cpy.opt import *
from cpy.tac import *

class TestOpt(unittest.TestCase):
    def get_tac(self,code:str): 
        ast = list(Prs(code).parse())
        return tac.to_tac(sem.analyze(ast) )

    def test_bb(self):
        code =\
        """
        int main() { 
            int x = 0;
            int a = 1;
            if (x==x) { 
                x = a;
            } else { 
                x = a*2;
            }
            return x;
        }
        """
        tac_res = self.get_tac(code)
        blocks = opt.blockify_fn(tac_res.functions[0])
        opt.analyze_next_uses(blocks)
        self.assertEqual(str(blocks),
"""\
BasicBlock 0, targets: [7, 4]:
0) x0 = Const(0)
1) a0 = Const(1) uses: {'x0': 2}
2) G0 = x0 == x0 uses: {'a0': 4, 'x0': 2}
3) jump if_then_0 if G0 uses: {'a0': 4}
BasicBlock 4, targets: [10]:
4) G1 = a0 * Const(2) uses: {'a0': 4}
5) x0 = G1 uses: {'a0': 8, 'G1': 5}
6) jump if_exit_0 uses: {'a0': 8}
BasicBlock 7, targets: [10]:
7) if_then_0: uses: {'a0': 8}
8) x0 = a0 uses: {'a0': 8}
9) jump if_exit_0 uses: {'x0': 11}
BasicBlock 10, targets: None:
10) if_exit_0: uses: {'x0': 11}
11) return x0 uses: {'x0': 11}
""")

if __name__ == "__main__": 
    unittest.main(verbosity=0)