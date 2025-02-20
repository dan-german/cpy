from cpy.vst import *
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
t0 = 2 * 3
a0 = 1 + t0
"""

if __name__ == "__main__":
    ast = list(Prs(code).parse())
    dbg.pn(ast)
    levels = defaultdict(list)

    for node,level in bfs(ast):
        levels[level].append(node)

    print(levels)


{0: [Var(id='a', type='int', value=BOp(op='+', left=Const(value='1'), right=BOp(op='*', left=Const(value='2'), right=Const(value='3'))))], 
 1: [BOp(op='+', left=Const(value='1'), right=BOp(op='*', left=Const(value='2'), right=Const(value='3')))], 
 2: [Const(value='1'), 
     BOp(op='*', left=Const(value='2'), right=Const(value='3'))], 
 3: [Const(value='2'), 
     Const(value='3')]}
