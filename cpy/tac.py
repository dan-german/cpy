from cpy.vst import *
from cpy.prs import Prs
from cpy.ast_models import *
import cpy.dbg as dbg
import cpy.sem as sem
from dataclasses import dataclass, field

@dataclass
class TACFn: 
    id: str
    args: list["TACArg"] = field(default_factory=list)
    block: list = field(default_factory=list)
    ids: dict = field(default_factory=dict)
    def __str__(self): return f"{self.id}: {[str(x) for x in self.args]}"

@dataclass
class TACGoto:
    label: str
    def __str__(self): return f"goto {self.label}"

@dataclass
class TACLabel: 
    label: str
    def __str__(self): return f"{self.label}:"

@dataclass 
class TACIf:
    value: str
    label: str
    def __str__(self): return f"if {self.value} goto {self.label}"
    # def __str__(self): return f"if {self.left} {self.op} {self.right}"

@dataclass 
class TACAssign:
    id: str
    value: str
    def __str__(self): return f"{self.id} = {self.value}"

@dataclass
class TACArg:
    type: str
    value: str
    def __str__(self): return f"{self.value}"

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
class TACGlobal: 
    id: str
    value: str
    def __str__(self): return f"global {self.id} = {self.value}"

@dataclass
class TACCall: 
    fn: str
    args: list
    return_value_id: str # None if void
    def __str__(self): return f"{self.return_value_id} = call {self.fn} {self.args}"

@dataclass
class TACRef: 
    id: str
    def __str__(self): return f"ref {self.id}"

@dataclass
class TACTable:
    functions: list[TACFn]
    globals: list[TACGlobal]
    def __str__(self):
        globals = "\n".join(str(x) for x in self.globals)
        functions="\n".join(
            f"{str(fn)}\n  " + "\n  ".join(map(str, fn.block))
            for fn in self.functions
        )
        return f"{globals}\n{functions}"

def to_tac(sem_result):
    stmts,global_vars,functions,_ = sem_result
    generated_var_counter = -1

    def get_symbol(node, scope: Scope): 
        return (scope.find_var(node) or global_vars[node.id]).id

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def find_existing_tac_id(tac_fn:TACFn,node): 
        return tac_fn.ids[node.id] if isinstance(node,Ref) else tac_fn.ids[id(node)]

    def assign(tac_fn:TACFn,node:BOp):
        left = find_existing_tac_id(tac_fn,node.left)
        right = find_existing_tac_id(tac_fn,node.right)
        tac_fn.block.append(TACAssign(left, TACRef(right)))
        tac_fn.ids[id(node)] = left

    def bop(tac_fn:TACFn,node: BOp):
        new_tac_id = generate_id()
        left,right = find_existing_tac_id(tac_fn,node.left),find_existing_tac_id(tac_fn,node.right)
        tac_fn.block.append(TACOp(new_tac_id, left, node.op, right))
        tac_fn.ids[id(node)] = new_tac_id 

    def add_tac(tac_fn:TACFn,node,scope:Scope):
        if isinstance(node,BOp): 
            if node.op == "=": 
                assign(tac_fn,node)
            else:
                bop(tac_fn,node)
        elif isinstance(node,Var): 
            new_tac_id = get_symbol(node,scope)
            tac_ref = None
            if (isinstance(node.value,Ref)):
                tac_ref = TACRef(tac_fn.ids[node.value.id])
            else:
                tac_ref = TACRef(tac_fn.ids[id(node.value)])
            tac_fn.block.append(TACAssign(new_tac_id,tac_ref))
            tac_fn.ids[node.id] = new_tac_id
        elif isinstance(node,Const): 
            new_tac_id = generate_id()
            tac_fn.block.append(TACAssign(new_tac_id,node))
            tac_fn.ids[id(node)] = new_tac_id 
            tac_fn.ids[id(node)] = new_tac_id 
        elif isinstance(node,Ret): 
            ref = None
            if isinstance(node.value,(BOp,Const,Call)):
                ref = tac_fn.ids[id(node.value)]
            else: 
                ref = get_symbol(node.value,scope)
            tac_fn.block.append(TACRet(ref))
        elif isinstance(node,Call):
            args = []
            for arg in node.args:
                if isinstance(arg,Const):
                    args.append(arg)
                elif isinstance(arg,Ref):
                    arg_sym = get_symbol(arg,scope)
                    args.append(TACRef(arg_sym))
                    tac_fn.ids[id(arg)] = arg_sym
                else: 
                    raise Exception("unhandled")
            if functions[node.id] == "void":
                tac_fn.block.append(TACCall(node.id,args,None))
            else:
                new_tac_id = generate_id()
                return_value_id = tac_fn.ids[id(node)] = new_tac_id
                tac_fn.block.append(TACCall(node.id,args,return_value_id))
                tac_fn.ids[id(node)] = new_tac_id 
    def process_scope(tac_fn,scope:Scope,v=0):
        if_counter = 0
        for node in scope.stmts:
            if isinstance(node, Scope):
                process_scope(tac_fn,node,v)
            elif isinstance(node, If):
                if_counter += 1

                for n in postorder(node.test):
                    add_tac(tac_fn,n,scope)
                tac_fn.block.append(TACIf(find_existing_tac_id(tac_fn,node.test), f"then_{if_counter}"))
                tac_fn.block.append(TACGoto(f"else_{if_counter}"))
                tac_fn.block.append(TACLabel(f"then_{if_counter}"))

                for n in postorder(node.else_):
                    add_tac(tac_fn,n,scope)
                tac_fn.block.append(TACGoto(f"exit_{if_counter}"))
                tac_fn.block.append(TACLabel(f"else_{if_counter}"))

                for n in postorder(node.body.stmts):
                    add_tac(tac_fn,n,scope)
                tac_fn.block.append(TACGoto(f"exit_{if_counter}"))
                tac_fn.block.append(TACLabel(f"exit_{if_counter}"))
                continue
            else: 
                for n in postorder(node):
                    add_tac(tac_fn,n,scope)

    def add_fn(fn:Fn):
        nonlocal generated_var_counter
        generated_var_counter = -1
        tac_fn = TACFn(fn.id)
        for arg in fn.args: 
            arg_sym = get_symbol(arg,fn.scope)
            tac_fn.args.append(TACArg("int",arg_sym))
            tac_fn.ids[arg.id] = arg_sym
        process_scope(tac_fn,fn.scope)
        return tac_fn

    tac_fns,tac_globals=[],[]
    for statement in stmts:
        if isinstance(statement,Var): tac_globals.append(TACGlobal(statement.id,statement.value))
        elif isinstance(statement,Fn): tac_fns.append(add_fn(statement))
    return TACTable(tac_fns,tac_globals)


#   G0 = Const(0)
#   x0 = ref G0
#   G1 = Const(2)
#   G2 = x0 = G1

if __name__ == "__main__":
    code =\
    """
    int main() { 
        int x = 0;
        x = 2;
    }
    """
    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    dbg.pn(ast)
    res = to_tac((a,b,c,d))
    print("tac")
    print(res)