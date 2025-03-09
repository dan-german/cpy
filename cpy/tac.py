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
    def __str__(self): return f"{self.id} = {self.value}"

@dataclass
class TACArg:
    id: str
    def __str__(self): return f"param {self.id}"

@dataclass
class TACOp: 
    id: str
    left: str
    op: str
    right: str
    def __str__(self): return f"{self.id} = {self.left} {self.op} {self.right}"

@dataclass
class TACRet: 
    value: str
    def __str__(self): return f"return {self.value}"

@dataclass
class TACCall: 
    fn: str
    ret_val_id: str # None if void
    def __str__(self): return f"{self.ret_val_id} = call {self.fn}" if self.ret_val_id else f"call {self.fn}"

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

    def find_organic_symobl(node, scope: Scope): 
        return (scope.find_var(node) or global_vars[node.id]).id

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def add_tac(tac_fn:TACFn,node,scope:Scope):
        tac_id = generate_id()
        if isinstance(node,BOp): 
            left,right = tac_fn.ids[id(node.left)],tac_fn.ids[id(node.right)]
            tac_fn.block.append(TACOp(tac_id, left, node.op, right))
            tac_fn.ids[id(node)] = tac_id 
        elif isinstance(node,Var): 
            tac_id = find_organic_symobl(node,scope)
            tac_fn.block.append(TACAssign(tac_id,tac_fn.ids[id(node.value)]))
            tac_fn.ids[id(node)] = tac_id 
        elif isinstance(node,Const): 
            tac_id = generate_id()
            tac_fn.block.append(TACAssign(tac_id,node.value))
            tac_fn.ids[id(node)] = tac_id 
        elif isinstance(node,Ret): 
            ref = None
            if isinstance(node.value,(BOp,Const,Call)):
                ref = tac_fn.ids[id(node.value)]
            else: 
                ref = find_organic_symobl(node.value,scope)
            tac_fn.block.append(TACRet(ref))
        elif isinstance(node,Call):
            if functions[node.id] == "void":
                tac_fn.block.append(TACCall(node.id,None))
            else:
                return_value_id = tac_fn.ids[id(node)] = generate_id()
                tac_fn.block.append(TACCall(node.id,return_value_id))
                tac_fn.ids[id(node)] = tac_id 

    def process_scope(tac_fn,scope:Scope,v=0):
        for node in scope.stmts:
            if isinstance(node, Scope):
                process_scope(tac_fn,node,v)
            else: 
                for n in postorder(node):
                    add_tac(tac_fn,n,scope)

    def add_fn(fn:Fn):
        nonlocal generated_var_counter
        generated_var_counter = -1
        tac_fn = TACFn(fn.id)
        tac_fn.args = [TACArg(arg.id) for arg in fn.args]
        process_scope(tac_fn,fn.scope)
        return tac_fn

    return TACTable([add_fn(node) for node,_ in bfs(stmts) if isinstance(node,Fn)])

if __name__ == "__main__":
    code = """
    int b() {
        return 2 + 3;
    }
    int main(){
        int a = b();
    }"""
    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    dbg.pn(ast)
    res = to_tac((a,b,c,d))
    print(res)
    # print("\n".join([str(x) for x in res.values()]))

