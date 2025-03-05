from cpy.vst import *
from cpy.prs import Prs
from cpy.ast_models import *
import cpy.sem as sem
import cpy.dbg as dbg
from collections import OrderedDict

@dataclass
class TACLabel: 
    id: str
    def __str__(self): return f"{self.id}:"

@dataclass 
class TACVar:
    id: str
    value: str
    def __str__(self): return f"{self.id} = {self.value}"

@dataclass
class TACArg:
    id: str
    def __str__(self): return f"param {self.id}"

@dataclass
class TACOp: 
    id: str
    left: Symbol
    op: str
    right: str
    def __str__(self): return f"{self.id} = {self.left} {self.op} {self.right}"

@dataclass
class TACRet: 
    value: str
    def __str__(self): return f"return {self.value}"

@dataclass
class TACCall: 
    id: str # None if void
    fn: str
    def __str__(self): return f"{self.id} = call {self.fn}" if self.id else f"call {self.fn}"

def generate(sem_result):
    stmts,global_vars,functions = sem_result
    table = OrderedDict()
    generated_var_counter = -1

    def find_var(node, scope: Scope):
        return (scope.find_var(node) or global_vars[node.id]).id

    def to_operand(node,scope:Scope) -> str:
        """
        Returns an appropriate operand for a tac.
        """
        if isinstance(node,Const): return node.value
        elif isinstance(node,Ref): return find_var(node,scope)
        elif id(node) in table: return table[id(node)].id

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def process_node(node,scope:Scope):
        if isinstance(node,BOp): table[id(node)] = TACOp(generate_id(),to_operand(node.left,scope),node.op,to_operand(node.right,scope))
        elif isinstance(node,Var): table[id(node)] = TACVar(find_var(node,scope),to_operand(node.value,scope))
        elif isinstance(node,Ret): table[id(node)] = TACRet(to_operand(node.value,scope))
        elif isinstance(node,Call): add_call(node)

    def add_arg(arg: Arg): 
        table[id(arg)] = TACArg(arg.id)

    def inspect_scope(scope:Scope):
        # build tacs in post-order to give lower BOp leaves priority
        for node in postorder(scope):
            process_node(node,scope)

    def add_call(node: Call):
        return_val = None if functions[node.id] == "void" else generate_id()
        table[id(node)] = TACCall(return_val, table[node.id].id)

    def add_fn(fn:Fn):
        table[fn.id] = TACLabel(fn.id) # functions can be id'd by their name as sem prevents duplicates
        for arg in fn.args: 
            add_arg(arg)
        for scope in (n for n,_ in bfs(fn) if isinstance(n,Scope)):
            nonlocal generated_var_counter
            generated_var_counter = -1
            inspect_scope(scope)

    for node in (n for n,_ in bfs(stmts) if isinstance(n,Fn)):
        add_fn(node)
    return table

if __name__ == "__main__":
    code = """
    int a(int a, int b){}
    """

    """
    a: 
        param a
    """

    res = generate(sem.analyze(list(Prs(code).parse())))
    print("\n".join([str(x) for x in res.values()]))