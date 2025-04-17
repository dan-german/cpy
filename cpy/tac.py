from cpy.vst import *
from cpy.prs import Prs, ASSIGN_OPS
from cpy.ast_models import *
import cpy.dbg as dbg
import cpy.sem as sem
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class TACFn: 
    id: str
    args: list["TACArg"] = field(default_factory=list)
    block: list = field(default_factory=list)
    ids: dict = field(default_factory=dict)
    def get_id(self,id:str): return self.ids[id]
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
    last_test_op: str
    def __str__(self): return f"if {self.value} goto {self.label}"

@dataclass 
class TACAssign:
    id: str
    value: str
    op: str
    def __str__(self): return f"{self.id} {self.op} {self.value}"

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
    value: str | Const
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
        res = (scope.find_var(node) or global_vars[node.id]).id
        return res

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def tac_id_for_node(tac_fn:TACFn,node): 
        if isinstance(node,Ref): return tac_fn.get_id(node.id)
        elif isinstance(node,Const): return node
        else: return tac_fn.get_id(id(node))

    def assign(tac_fn:TACFn,node:BOp):
        left = tac_id_for_node(tac_fn,node.left)
        right = tac_id_for_node(tac_fn,node.right)
        tac_fn.block.append(TACAssign(left, right, node.op))
        tac_fn.ids[id(node)] = left

    def bop(tac_fn:TACFn,node: BOp):
        new_tac_id = generate_id()
        left = tac_id_for_node(tac_fn,node.left)
        right = tac_id_for_node(tac_fn,node.right)
        tac_fn.block.append(TACOp(new_tac_id, left, node.op, right))
        tac_fn.ids[id(node)] = new_tac_id 

    def var(tac_fn,node:Var,scope):
        new_tac_id = get_symbol(node, scope)
        tac_ref = None
        if isinstance(node.value,Ref): tac_ref = TACRef(tac_fn.get_id(node.value.id))
        elif isinstance(node.value,BOp): tac_ref = tac_fn.get_id(id(node.value))
        else: tac_ref = node.value
        print(new_tac_id,tac_ref)
        tac_fn.block.append(TACAssign(new_tac_id, tac_ref, "="))
        tac_fn.ids[node.id] = new_tac_id

    def add_tac(tac_fn: TACFn, node, scope: Scope):
        match node:
            case BOp():
                if node.op in ASSIGN_OPS: assign(tac_fn, node)
                else: bop(tac_fn, node)
            case Var(): var(tac_fn,node,scope)
            case Ret(value=ret_value):
                ref = None
                if (isinstance(ret_value, (BOp, Call))): ref = tac_fn.get_id(id(ret_value))
                elif isinstance(ret_value, Const): ref = ret_value
                else: ref = get_symbol(ret_value, scope)
                tac_fn.block.append(TACRet(ref))
            case Call(id=fn_id, args=args):
                arg_list = []
                for arg in args:
                    match arg:
                        case Const():
                            arg_list.append(arg)
                        case Ref():
                            arg_sym = get_symbol(arg, scope)
                            arg_list.append(TACRef(arg_sym))
                            tac_fn.ids[id(arg)] = arg_sym
                        case _: raise Exception("unhandled")
                if functions[fn_id] == "void":
                    tac_fn.block.append(TACCall(fn_id, arg_list, None))
                else:
                    new_tac_id = generate_id()
                    tac_fn.ids[id(node)] = new_tac_id
                    tac_fn.block.append(TACCall(fn_id, arg_list, new_tac_id))

    def process_scope(tac_fn,scope:Scope,v=0):
        if_counter = 0
        for node in scope.stmts:
            if isinstance(node, Scope):
                process_scope(tac_fn,node,v)
            elif isinstance(node, If):
                last_op = None
                for n in postorder(node.test):
                    add_tac(tac_fn,n,scope)
                    last_op = n.op if isinstance(n, BOp) else None
                assert last_op
                tac_fn.block.append(TACIf(tac_id_for_node(tac_fn,node.test), f"then_{if_counter}", last_op))
                tac_fn.block.append(TACGoto(f"else_{if_counter}"))
                tac_fn.block.append(TACLabel(f"then_{if_counter}"))

                for n in postorder(node.body.stmts):
                    add_tac(tac_fn,n,scope)
                tac_fn.block.append(TACGoto(f"exit_{if_counter}"))
                tac_fn.block.append(TACLabel(f"else_{if_counter}"))

                for n in postorder(node.else_):
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

def inst_combine():
    pass   

def defuse(tac_table:TACTable):
    defs = []
    for item in tac_table.functions[0].block:
        if isinstance(item,TACAssign): 
            print("item", item)
            defs.append(item)
    print(defs)

if __name__ == "__main__":
    code =\
    """
    int main() {
        int i = 0;
        int x = 1;
        while (i < 2) { 
            x *= 2;
        }
        return x;
    }
    """
    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    dbg.pn(ast)
    res = to_tac((a,b,c,d))
    print(res)