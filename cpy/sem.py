from cpy.prs import Prs
from cpy.classes import *
from cpy.vst import preorder
import cpy.dbg as dbg

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

def analyze(ast):
    def find_ref(scope:Scope,id:str): 
        """
        Climb the scopes tree to find the ref's declaration
        """
        if id in scope.sym: return scope.sym[id]
        if scope.parent: return find_ref(scope.parent, id)
        raise Undeclared(id)

    id_counter = defaultdict(int)
    def get_id(node:Var):
        temp = (node.type, f"{node.id}{id_counter[node.id]}")
        id_counter[node.id] += 1 
        return temp

    def analyze_function(scope,v=0):
        for node in scope.stmts:
            if isinstance(node, Fn): raise DefUnallowed(node.id)
            elif isinstance(node, Scope):
                node.parent = scope
                analyze_function(node,v)
            elif isinstance(node, Var):
                if node.id in scope.sym: raise Redefinition(node.id)
                scope.sym.vars[node.id] = get_id(node)
            elif isinstance(node, BOp):
                for child,_ in preorder(node):
                    print(child)
                    if isinstance(child,Ref):
                        ref_id = find_ref(scope,child.id)
                        print(ref_id)
            elif isinstance(node,Ref):
                ref_id = find_ref(scope,node.id)

    global_vars = {}
    functions = {}

    for node in ast:
        if isinstance(node, Fn):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            functions[node.id] = node.type
            analyze_function(node.scope)
        elif isinstance(node, Ref):
            if node.id not in global_vars: raise Undeclared(node.id)
        elif isinstance(node, Scope):
            raise GlobalScope()
        elif isinstance(node, Var):
            if node.id in [*global_vars,*functions]: raise Redefinition(node.id)
            global_vars[node.id] = get_id(node)
    
    return ast,global_vars,functions