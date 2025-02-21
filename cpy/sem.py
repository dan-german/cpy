from cpy.ast_models import *
from cpy.vst import preorder
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
    
class GlobalScope(Exception): 
    def __init__(self): super().__init__(f"Global scopes unallowed")

def analyze(stmts: list) -> tuple:
    id_counter = defaultdict(int)

    def get_id(node:Var):
        temp = (node.type, f"{node.id}{id_counter[node.id]}")
        id_counter[node.id] += 1 
        return temp

    def build_symbol_table(scope:Scope,v=0):
        for node in scope.stmts:
            if isinstance(node, Fn): raise DefUnallowed(node.id)
            elif isinstance(node, Scope):
                node.parent_scope = scope
                build_symbol_table(node,v)
            elif isinstance(node, Var):
                if node.id in scope.sym: raise Redefinition(node.id)
                scope.sym.vars[node.id] = get_id(node)
            elif isinstance(node, BOp):
                for child,_ in preorder(node):
                    if isinstance(child,Ref):
                        if not (ref_id := scope.find_ref(child.id)): raise Undeclared(child.id)
            elif isinstance(node,Ref):
                ref_id = scope.find_ref(node.id)
                if not (ref_id := scope.find_ref(node.id)): raise Undeclared(node.id)

    global_vars = {}
    functions = {}

    for node in stmts:
        if isinstance(node, Fn):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            functions[node.id] = node.type
            build_symbol_table(node.scope)
        elif isinstance(node, Ref):
            if node.id not in global_vars: raise Undeclared(node.id)
        elif isinstance(node, Scope):
            raise GlobalScope()
        elif isinstance(node, Var):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            global_vars[node.id] = get_id(node)
    
    return stmts,global_vars,functions