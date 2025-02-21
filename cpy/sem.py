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

    def get_id(node:Var):
        temp = (node.type, f"{node.id}{id_counter[node.id]}")
        id_counter[node.id] += 1 
        return temp

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

    def collect_symbols_for_scope(scope:Scope,v=0):
        for node in scope.stmts:
            validate_refs(node,scope)
            if isinstance(node, Fn): raise DefUnallowed(node.id)
            elif isinstance(node, Scope):
                node.parent_scope = scope
                collect_symbols_for_scope(node,v)
            elif isinstance(node, Var):
                if node.id in scope.sym: raise Redefinition(node.id)
                scope.sym.vars[node.id] = get_id(node)

    global_vars = {}
    functions = {}

    for node in stmts:
        if isinstance(node, Fn):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            functions[node.id] = node.type
            collect_symbols_for_scope(node.scope)
        elif isinstance(node, Ref):
            if node.id not in global_vars: raise Undeclared(node.id)
        elif isinstance(node, Scope):
            raise GlobalScope()
        elif isinstance(node, Var):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            global_vars[node.id] = get_id(node)
            id_counter[node.id] += 1
    
    return stmts,global_vars,functions

if __name__ == "__main__":
    code = """
    int f(int a) { return a; }
    int main() { return f(2); }
    """
    code = "int f(){a;}"
    tree = list(Prs(code).parse())
    # dbg.pn(tree)
    # print(analyze(tree))
    a,b,c=analyze(tree)
    print(b,c)
    dbg.pn(tree)
