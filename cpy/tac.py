from cpy.prs import Prs
from cpy.classes import *
import cpy.dbg as dbg

res = []

def generate(ast): 
    for node in ast: 
        if isinstance(node,Var):
            res.append((node.id,"=",node.value.value))

code = """
int a = 1 + 2 * 3;
"""

"""
expected:
g1 = 2 * 3
a0 = 1 + g1
"""

if __name__ == "__main__":
    ast = list(Prs(code).parse())
    dbg.pn(ast)