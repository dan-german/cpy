import unittest
from cpy.opt import fold
from cpy.prs import Prs

class TestFold(unittest.TestCase):
    def to_str(self, input, fn = Prs.stmnt) -> str: return str(fold(fn(Prs(input))))
    
    def test_fold(self):
        self.assertEqual(self.to_str("1*2+3*4", Prs.expr), "Const(14)")
        self.assertEqual(self.to_str("a+2*3", Prs.expr), "BOp(Ref(a)+Const(6))")
        self.assertEqual(self.to_str("a==b", Prs.expr), "BOp(Ref(a)+Const(6))")

if __name__ == "__main__":
    unittest.main(verbosity=1)