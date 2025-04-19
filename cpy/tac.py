from cpy.vst import *
from cpy.prs import Prs, ASSIGN_OPS
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
class TACWhile:
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

if_counter = 0
while_counter = 0

def to_tac(sem_result):
    stmts,global_vars,functions,_ = sem_result
    generated_var_counter = -1

    def get_symbol(node, scope: Scope): return (scope.find_var(node) or global_vars[node.id]).id

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
                        case Ref():
                            arg_sym = get_symbol(arg, scope)
                            arg_list.append(TACRef(arg_sym))
                            tac_fn.ids[id(arg)] = arg_sym
                        case Const(): arg_list.append(arg)
                        case _: raise Exception("unhandled")
                if functions[fn_id] == "void": tac_fn.block.append(TACCall(fn_id, arg_list, None))
                else:
                    new_tac_id = generate_id()
                    tac_fn.ids[id(node)] = new_tac_id
                    tac_fn.block.append(TACCall(fn_id, arg_list, new_tac_id))

    def unwrap(tac_fn,node,scope): 
        for n in postorder(node): add_tac(tac_fn,n,scope)

    def if_(tac_fn,node:If,scope:Scope):
        global if_counter
        unwrap(tac_fn,node.test,scope)
        tac_fn.block.append(TACIf(tac_id_for_node(tac_fn,node.test), f"if_then_{if_counter}", tac_fn.block[-1].op))
        if_counter += 1
        if node.else_: process_scope(tac_fn,node.else_)
        if_counter -= 1
        tac_fn.block.append(TACGoto(f"if_exit_{if_counter}"))
        tac_fn.block.append(TACLabel(f"if_then_{if_counter}"))
        if_counter += 1
        process_scope(tac_fn,node.body)
        if_counter -= 1
        tac_fn.block.append(TACGoto(f"if_exit_{if_counter}"))
        tac_fn.block.append(TACLabel(f"if_exit_{if_counter}"))

    def while_(tac_fn,node:While,scope:Scope):
        global while_counter
        tac_fn.block.append(TACLabel(f"loop_start_{while_counter}"))
        unwrap(tac_fn,node.test,scope)
        tac_fn.block.append(TACIf(tac_id_for_node(tac_fn,node.test), f"loop_do_{while_counter}", tac_fn.block[-1].op))
        tac_fn.block.append(TACGoto(f"loop_exit_{while_counter}"))
        tac_fn.block.append(TACLabel(f"loop_do_{while_counter}"))
        while_counter += 1
        process_scope(tac_fn, node.body)
        while_counter -= 1
        tac_fn.block.append(TACGoto(f"loop_start_{while_counter}"))
        tac_fn.block.append(TACLabel(f"loop_exit_{while_counter}"))

    def process_scope(tac_fn,scope:Scope):
        for node in scope.stmts:
            match node:
                case Scope(): process_scope(tac_fn,node)
                case If(): if_(tac_fn,node,scope)
                case While(): while_(tac_fn,node,scope)
                case _: unwrap(tac_fn,node,scope)

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

if __name__ == "__main__":
    code =\
    """
    int main() { 
        int x = 1;
        int i = 0;
        while (i < 2) { 
            int j = 3;
            x *= 2;
            while (j != 0) { 
                x *= 2;
                j -= 1;
            }
            i+=1;
        }
        return x;
    }
    """
    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    dbg.pn(ast)
    res = to_tac((a,b,c,d))
    print(res)