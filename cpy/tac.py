from cpy.vst import *
from cpy.prs import ASSIGN_OPS
from cpy.ast_models import *
import cpy.sem as sem
from dataclasses import dataclass, field

@dataclass
class TACFn: 
    id: str
    args: list["TACArg"] = field(default_factory=list)
    code: list = field(default_factory=list)
    id_map: dict = field(default_factory=dict)
    symbols: set = field(default_factory=set)
    def get_id(self,id:str): return self.id_map[id]
    def __str__(self): return f"{self.id}: {[str(x) for x in self.args]}"
    def add_id(self,k,v):
        self.id_map[k] = v
        self.symbols.add(v if type(k) == int else k)

@dataclass 
class TAC:
    next_use: dict[int] = field(default_factory=dict, init=False)

@dataclass
class TACJump(TAC):
    target: str
    def __str__(self): return f"jump {self.target}"

@dataclass
class TACLabel(TAC): 
    label: str
    def __str__(self): return f"{self.label}:"

@dataclass 
class TACCondJump(TAC):
    value: str
    target: str
    last_test_op: str
    def __str__(self): return f"jump {self.target} if {self.value}"

@dataclass 
class TACWhile(TAC):
    value: str
    label: str
    last_test_op: str
    def __str__(self): return f"jump {self.label} if {self.value}"

@dataclass 
class TACAssign(TAC):
    id: str
    value: str
    op: str
    def __str__(self): return f"{self.id} {self.op} {self.value}"

@dataclass
class TACArg(TAC):
    type: str
    value: str
    def __str__(self): return f"{self.value}"

@dataclass
class TACOp(TAC): 
    id: str
    left: str
    op: str
    right: str
    def __str__(self): return f"{self.id} = {self.left} {self.op} {self.right}"

@dataclass
class TACRet(TAC): 
    value: str | Const
    def __str__(self): return f"return {self.value}"
    
@dataclass
class TACGlobal(TAC): 
    id: str
    value: str
    def __str__(self): return f"global {self.id} = {self.value}"

@dataclass
class TACCall(TAC): 
    fn: str
    args: list
    return_value_id: str # None if void
    def __str__(self): return f"{self.return_value_id} = call {self.fn} {self.args}"

@dataclass
class TACTable:
    functions: list[TACFn]
    globals: list[TACGlobal]
    def __str__(self):
        globals = "\n".join(str(x) for x in self.globals)
        functions="\n".join(
            f"{str(fn)}\n  " + "\n  ".join([(str(i)+") "+str(x)) for i,x in enumerate(fn.code)])
            for fn in self.functions
        )
        return f"{globals}\n{functions}"

if_counter = 0
while_counter = 0

def to_tac(sem_result: sem.SemResult) -> TACTable:
    generated_var_counter = -1
    def get_symbol(node, scope: Scope): return (scope.find_var(node) or sem_result.global_vars[node.id]).id

    def generate_id():
        nonlocal generated_var_counter
        generated_var_counter += 1
        return f"G{generated_var_counter}" # G for generated

    def tac_id_for_node(tac_fn:TACFn,node, scope: Scope): 
        if isinstance(node,Ref): 
            if id(node) in tac_fn.id_map: return tac_fn.get_id(id(node))
            else: return get_symbol(node,scope)
        elif isinstance(node,Const): return node
        else: return tac_fn.get_id(id(node))

    def assign(tac_fn:TACFn,node:BOp, scope: Scope):
        left = tac_id_for_node(tac_fn,node.left,scope)
        right = tac_id_for_node(tac_fn,node.right,scope)
        tac_fn.code.append(TACAssign(left, right, node.op))
        tac_fn.add_id(id(node),left)

    def bop(tac_fn:TACFn, node: BOp,scope:Scope):
        new_tac_id = generate_id()
        left = tac_id_for_node(tac_fn,node.left,scope)
        right = tac_id_for_node(tac_fn,node.right,scope)
        tac_fn.code.append(TACOp(new_tac_id, left, node.op, right))
        tac_fn.add_id(id(node),new_tac_id)

    def var(tac_fn: TACFn, node: Var, scope):
        new_tac_id = get_symbol(node, scope)
        tac_ref = None
        if isinstance(node.value,Ref): tac_ref = tac_fn.get_id(node.value.id)
        elif isinstance(node.value,BOp): tac_ref = tac_fn.get_id(id(node.value))
        else: tac_ref = node.value
        tac_fn.code.append(TACAssign(new_tac_id, tac_ref, "="))
        tac_fn.add_id(node.id,new_tac_id)

    def add_tac(tac_fn: TACFn, node, scope: Scope):
        match node:
            case BOp():
                if node.op in ASSIGN_OPS: assign(tac_fn, node, scope)
                else: bop(tac_fn, node,scope)
            case Var(): var(tac_fn,node,scope)
            case Ret(value=ret_value):
                ref = None
                if (isinstance(ret_value, (BOp, Call))): ref = tac_fn.get_id(id(ret_value))
                elif isinstance(ret_value, Const): ref = ret_value
                else: ref = get_symbol(ret_value, scope)
                tac_fn.code.append(TACRet(ref))
            case Call(id=fn_id, args=args):
                arg_list = []
                for arg in args:
                    match arg:
                        case Ref():
                            arg_sym = get_symbol(arg, scope)
                            arg_list.append(arg_sym)
                            tac_fn.add_id(id(arg), arg_sym)
                        case Const(): arg_list.append(arg)
                        case _: raise Exception("unhandled")
                if sem_result.functions[fn_id] == "void": tac_fn.code.append(TACCall(fn_id, arg_list, None))
                else:
                    new_tac_id = generate_id()
                    tac_fn.add_id(id(node),new_tac_id)
                    tac_fn.code.append(TACCall(fn_id, arg_list, new_tac_id))

    def unwrap(tac_fn,node,scope): 
        for n in postorder(node): add_tac(tac_fn,n,scope)

    def if_(tac_fn:TACFn,node:If,scope:Scope):
        global if_counter
        unwrap(tac_fn,node.test,scope)
        tac_fn.code.append(TACCondJump(tac_id_for_node(tac_fn,node.test,scope), f"if_then_{if_counter}", tac_fn.code[-1].op))
        if_counter += 1
        if node.else_: process_scope(tac_fn,node.else_)
        if_counter -= 1
        tac_fn.code.append(TACJump(f"if_exit_{if_counter}"))
        tac_fn.code.append(TACLabel(f"if_then_{if_counter}"))
        if_counter += 1
        process_scope(tac_fn,node.body)
        if_counter -= 1
        tac_fn.code.append(TACJump(f"if_exit_{if_counter}"))
        tac_fn.code.append(TACLabel(f"if_exit_{if_counter}"))

    def while_(tac_fn:TACFn,node:While,scope:Scope):
        global while_counter
        tac_fn.code.append(TACLabel(f"loop_start_{while_counter}"))
        unwrap(tac_fn,node.test,scope)
        tac_fn.code.append(TACCondJump(tac_id_for_node(tac_fn,node.test,scope), f"loop_do_{while_counter}", tac_fn.code[-1].op))
        tac_fn.code.append(TACJump(f"loop_exit_{while_counter}"))
        tac_fn.code.append(TACLabel(f"loop_do_{while_counter}"))
        while_counter += 1
        process_scope(tac_fn, node.body)
        while_counter -= 1
        tac_fn.code.append(TACJump(f"loop_start_{while_counter}"))
        tac_fn.code.append(TACLabel(f"loop_exit_{while_counter}"))

    def process_scope(tac_fn:TACFn,scope:Scope):
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
            tac_fn.add_id(arg.id, arg_sym)
        process_scope(tac_fn,fn.scope)
        return tac_fn

    tac_fns,tac_globals=[],[]
    for statement in sem_result.stmts:
        if isinstance(statement,Var): tac_globals.append(TACGlobal(statement.id,statement.value))
        elif isinstance(statement,Fn): tac_fns.append(add_fn(statement))
    return TACTable(tac_fns,tac_globals)