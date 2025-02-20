from cpy.vst import *
from cpy.prs import Prs
from cpy.ast_models import *
from cpy.sem import *
import cpy.dbg as dbg
from collections import OrderedDict

table = OrderedDict()

@dataclass
class TACLabel: 
    id: str
    def __str__(self): return f"{self.id}:"

@dataclass 
class TACVar:
    id: str
    value: str
    def __str__(self): return f"  {self.id} = {self.value}"

@dataclass
class TACOp: 
    id: str
    left: str
    op: str
    right: str
    def __str__(self): return f"  {self.id} = {self.left} {self.op} {self.right}"

def to_operand(node,scope:Scope) -> str:
    if isinstance(node,Const): return node.value
    elif isinstance(node,Ref): return scope.sym_for_ref(node.id)[1]
    elif id(node) in table: return table[id(node)][0]

t = 0
def generate_id():
    global t
    id = f"G{t}" # G for generated
    t += 1
    return id

def node_to_tac(node,scope):
    print(type(node))
    if isinstance(node,BOp):
        add_bop(node,scope)
    elif isinstance(node,Var):
        value = to_operand(node.value,scope)
        tac = TACVar(scope.find_ref(node.id)[1],value)
        table[id(node)] = (tac.id, tac)

def inspect_scope(scope:Scope):
    for node in postorder(scope):
        node_to_tac(node,scope)

def add_bop(node:BOp,scope:Scope):
    left = to_operand(node.left,scope)
    right = to_operand(node.right,scope)
    tac = TACOp(generate_id(),left,node.op,right)
    table[id(node)] = (tac.id, tac)

def add_fn(fn:Fn):
    global t 
    t = 0
    table[id(fn)] = (fn.id,TACLabel(fn.id))
    for scope in (n for n,_ in bfs(fn) if isinstance(n,Scope)):
        inspect_scope(scope)

if __name__ == "__main__":
    code = """
        int a() {
            int a=1;
            int b=2;
            return a + b;
        }
        int main() { 
            return a();
        }
    """

    code = """
    int f() { return 1; }
    int main() { return f(); }
    """

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