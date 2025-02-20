from cpy.vst import *
from cpy.prs import Prs
from cpy.classes import *
from cpy.sem import *
import cpy.dbg as dbg
from collections import OrderedDict

code = """
int f() { 
    int a = 1 + 2 * 3;
    return a;
}
int main() { 
    int b = 3 * 4 - 9;
}
"""

"""
expected:
t0 = 2 * 3
a0 = 1 + t0
"""

table = OrderedDict()

@dataclass
class Label: 
    id: str
    def __str__(self): return f"{self.id}:"

@dataclass
class TAC: 
    id: str
    left: str
    op: str
    right: str
    def __str__(self): return f"  {self.id} = {self.left} {self.op} {self.right}"

def get_operand(node) -> str:
    if isinstance(node,Const): return node.value
    elif id(node) in table: return table[id(node)][0]

t = 0
def generate_id():
    global t
    id = f"t{t}"
    t += 1
    return id

def add_bop(node:BOp):
    left = get_operand(node.left)
    right = get_operand(node.right)
    tac = TAC(generate_id(),left,node.op,right)
    table[id(node)] = (tac.id, tac)

def add_fn(fn:Fn):
    global t 
    t = 0
    table[id(fn)] = (fn.id,Label(fn.id))
    for node in postorder(fn):
        if isinstance(node, BOp):
            add_bop(node)

if __name__ == "__main__":
    ast = list(Prs(code).parse())
    dbg.pn(ast)
    analyze(ast)
    for node in ast: 
        if isinstance(node, Fn):
            add_fn(node)
            
    print("\n".join([str(x[1]) for x in table.values()]))

# f:
#   t0 = 2 * 3
#   t1 = 1 + t0