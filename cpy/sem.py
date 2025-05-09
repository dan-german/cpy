from cpy.ast_models import *
from cpy.prs import Prs
from cpy.vst import *
import cpy.dbg as dbg
from collections import defaultdict

class GlobalCall(Exception): 
    def __init__(self,msg): super().__init__(f"Global scope call '{msg}'")
    
class Redefinition(Exception): 
    def __init__(self,msg): super().__init__(f"Redefinition of '{msg}'")

class Undeclared(Exception): 
    def __init__(self,msg): super().__init__(f"Use of undeclared id '{msg}'")

class DefUnallowed(Exception): 
    def __init__(self,msg): super().__init__(f"Function definition '{msg}' not allowed here.")

class ArgsMiscount(Exception): 
    def __init__(self,msg,args:int,given:int): super().__init__(f"Function '{msg}' requires {args} args, while {given} were given")
    
class GlobalScope(Exception): 
    def __init__(self): super().__init__(f"Global scopes unallowed")

@dataclass
class SemResult: 
    stmts: list
    global_vars: dict
    functions: dict
    all_syms: dict

def analyze(stmts: list) -> SemResult:
    id_counter = defaultdict(int)
    global_vars = {}
    functions = {}
    all_symbols = {}

    def add_symbol(node,table:dict,scope_type:str):
        id = node.id + str(id_counter[node.id])
        if node.id == "G": id = f"_{node.id}"
        id_counter[node.id] += 1
        table[node.id] = all_symbols[id] = Symbol(id,node.type,scope_type)

    def validate_refs(node, scope):
        for child, _ in bfs(node):
            if isinstance(child, Ref) and not (scope.find_var(child) or child.id in global_vars): raise Undeclared(child.id)
            if isinstance(child, Call):
                if child.id not in functions: raise Undeclared(child.id)
                callee = functions[child.id]
                if len(child.args) != len(callee.args): raise ArgsMiscount(child.id,len(callee.args),len(child.args))
                if len(child.args) > 7 or len(callee.args) > 7: raise Exception("Support stack args")
                #TODO: type checks and stack args

    def analyze_scope(scope:Scope):
        for node in scope.stmts:
            match node: 
                case Fn(): raise DefUnallowed(node.id)
                case While(): 
                    node.body.parent_scope = scope
                    validate_refs(node.test,scope)
                    analyze_scope(node.body)
                case If(): 
                    node.body.parent_scope = scope
                    if node.else_:node.else_.parent_scope = scope
                    validate_refs(node.test,scope)
                    analyze_scope(node.body)
                    if (node.else_): analyze_scope(node.else_)
                case Scope(): 
                    node.parent_scope = scope
                    analyze_scope(node)
                case Var():
                    validate_refs(node,scope)
                    if node.id in scope.sym: raise Redefinition(node.id)
                    add_symbol(node,scope.sym,"local")
                case _: validate_refs(node,scope)

    for node in stmts:
        match node:
            case Scope(): raise GlobalScope()
            case Ref(): 
                if node.id not in global_vars: raise Undeclared(node.id)
            case Fn(): 
                if node.id in global_vars or node.id in functions: raise Redefinition(node.id)
                functions[node.id] = node
                [add_symbol(arg, node.scope.sym, "arg") for arg in node.args]
                analyze_scope(node.scope)
            case Var():
                if node.id in global_vars or node.id in functions: raise Redefinition(node.id)
                add_symbol(node,global_vars,"global")

    return SemResult(stmts,global_vars,functions,all_symbols)