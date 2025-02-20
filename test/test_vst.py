import unittest
from cpy import Prs
from cpy.vst import *

class TestVst(unittest.TestCase):
    def test_bfs(self):
        ast = list(Prs("1*2*3*4").parse())
        expected = [
            ('BOp(BOp(BOp(Const(1)*Const(2))*Const(3))*Const(4))', 0), 
            ('BOp(BOp(Const(1)*Const(2))*Const(3))', 1), 
            ('Const(4)', 1), 
            ('BOp(Const(1)*Const(2))', 2), 
            ('Const(3)', 2), 
            ('Const(1)', 3), 
            ('Const(2)', 3)
        ]
        self.assertEqual([(str(node), level) for node,level in bfs(ast)],expected)

    def test_preorder(self):
        ast = list(Prs("1*2*3*4").parse())
        expected = [
            ('BOp(BOp(BOp(Const(1)*Const(2))*Const(3))*Const(4))', 0), 
            ('BOp(BOp(Const(1)*Const(2))*Const(3))', 1), 
            ('BOp(Const(1)*Const(2))', 2), 
            ('Const(1)', 3), 
            ('Const(2)', 3), 
            ('Const(3)', 2), 
            ('Const(4)', 1)
        ]  
        self.assertEqual([(str(node),level) for node,level in preorder(ast)],expected)

if __name__ == "__main__": 
    unittest.main(verbosity=0)