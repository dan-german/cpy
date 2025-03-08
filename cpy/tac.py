from cpy.vst import *
from cpy.prs import Prs
from cpy.ast_models import *
import cpy.dbg as dbg
import cpy.sem as sem
from collections import OrderedDict
from dataclasses import dataclass, field

@dataclass
class TACFn: 
    id: str
    args: list["TACArg"] = field(default_factory=list)
    block: list = field(default_factory=list)
    ids: dict = field(default_factory=dict)
    def __str__(self): return f"{self.id}:"

@dataclass 
class TACStore:
    id: str
    def __str__(self): return f"store {self.id}"

@dataclass 
class TACLoad:
    id: str
    def __str__(self): return f"load {self.id}"

@dataclass 
class TACAssign:
    id: str
    value: str
    # def __str__(self): return f"{self.id} = {self.value}"
    def __str__(self): return f"assign {self.id}, {self.value}"

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

@dataclass
class TACTable:
    functions: list[TACFn]
    def __str__(self):
        return "\n".join(
            f"{fn.id}:\n  " + "\n  ".join(map(str, fn.block))
            for fn in self.functions
        )

def to_tac(sem_result):
    stmts,global_vars,functions,symbol_table = sem_result
    generated_var_counter = -1

    def find_var(node, scope: Scope): 
        return (scope.find_var(node) or global_vars[node.id]).id

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def process_node(tac_fn:TACFn,node,scope:Scope):
        if isinstance(node,BOp): 
            tac_id = generate_id()
            tac_fn.block.append(TACStore(tac_id))
            left = tac_fn.ids[id(node.left)]
            right = tac_fn.ids[id(node.right)]

            tac_fn.block.append(TACLoad(left))
            tac_fn.block.append(TACLoad(right))

            tac_fn.block.append(TACOp(tac_id, left, node.op, right))
            tac_fn.ids[id(node)] = tac_id
            symbol_table[tac_id] = ()
        elif isinstance(node,Var): 
            tac_id = find_var(node,scope)
            tac_fn.block.append(TACStore(tac_id))
            tac_fn.block.append(TACAssign(tac_id,tac_fn.ids[id(node.value)]))
            tac_fn.ids[id(node)] = tac_id
        elif isinstance(node,Const): 
            tac_id = generate_id()
            tac_fn.block.append(TACStore(tac_id))
            tac_fn.block.append(TACAssign(tac_id,node.value))
            tac_fn.ids[id(node)] = tac_id
            symbol_table

    def process_scope(tac_fn,scope:Scope,v=0):
        for node in scope.stmts:
            if isinstance(node, Scope):
                process_scope(tac_fn,node,v)
            else: 
                for n in postorder(node):
                    process_node(tac_fn,n,scope)

    def add_fn(fn:Fn):
        nonlocal generated_var_counter
        generated_var_counter = -1
        tac_fn = TACFn(fn.id)
        tac_fn.args = [TACArg(arg.id) for arg in fn.args]
        process_scope(tac_fn,fn.scope)
        return tac_fn

    return TACTable([add_fn(node) for node,_ in bfs(stmts) if isinstance(node,Fn)])

if __name__ == "__main__":
    code = "int a(){int a=1+2;}"
    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    dbg.pn(ast)
    res = to_tac((a,b,c,d))
    print(res)
    # print("\n".join([str(x) for x in res.values()]))




        # elif isinstance(node,Ret): tac_fn.block[id(node)] = TACRet(tac_fn.ids[id(node.value)])
        # elif isinstance(node,Call):
        #     return_val = None if functions[node.id] == "void" else generate_id()
        #     tac_fn.block[id(node)] = TACCall(return_val, tac_fn.block[node.id].id)