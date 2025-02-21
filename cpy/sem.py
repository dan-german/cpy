from cpy.ast_models import *
from cpy.prs import Prs
from cpy.vst import *
import cpy.dbg as dbg
from collections import defaultdict
from dataclasses import fields

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

    def add_symbol(node,table:SymbolTable,scope_type:str):
        id = node.id + str(id_counter[node.id])
        id_counter[node.id] += 1
        table[node.id] = Symbol(id,node.type,scope_type)

    def validate_refs(node,scope:Scope):
        var_refs = []
        fn_refs = []
        if isinstance(node,Ref): node = [node]
        for child,_ in preorder(node):
            if isinstance(child,Call):
                pass
            elif isinstance(child,Ref):
                var_refs.append(child)

        for ref in [*var_refs,*fn_refs]: 
            if not scope.sym_for_ref(ref): raise Undeclared(ref.id)

    def analyze_scope(scope:Scope,v=0):
        for node in scope.stmts:
            validate_refs(node,scope)
            if isinstance(node, Fn): raise DefUnallowed(node.id)
            elif isinstance(node, Scope):
                node.parent_scope = scope
                analyze_scope(node,v)
            elif isinstance(node, Var):
                if node.id in scope.sym: raise Redefinition(node.id)
                add_symbol(node,scope.sym,"local")
                # scope.sym.vars[node.id] = get_id(node)

    global_vars = SymbolTable()
    functions = {}

    def add_args_symbols(fn:Fn):
        for arg in fn.args: 
            add_symbol(arg,fn.scope.sym,"arg")

    for node in stmts:
        if isinstance(node, Fn):
            if node.id in global_vars or node.id in functions: raise Redefinition(node.id)
            functions[node.id] = node.type
            add_args_symbols(node)
            analyze_scope(node.scope)
        elif isinstance(node, Ref):
            if node.id not in global_vars: raise Undeclared(node.id)
        elif isinstance(node, Scope):
            raise GlobalScope()
        elif isinstance(node, Var):
            if node.id in global_vars or node.id in functions: raise Redefinition(node.id)
            add_symbol(node,global_vars,"global")

    return stmts,global_vars,functions

if __name__ == "__main__":
    code = """
    """
    tree = list(Prs(code).parse())
    _,globals,fn=analyze(tree)
    print(globals)
    # dbg.pn(tree)
    # print(globals)    
    # print("\n".join([str(x) for x in globals]))    