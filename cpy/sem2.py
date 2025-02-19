from cpy.prs import Prs
from cpy.classes import *
from cpy.sem import SymbolTable
from cpy.vst import bfs,dfs
import cpy.dbg as dbg

code = """
void a() {
    int b = 1;
    { 
        b += 3;
    }
}
void k() {
    int b = 1;
    { 
        b += 3;
    }
}
"""

v = 0

def analyze(ast_):
    def find_ref(scope:Scope,id:str): 
        """
        Climb the scopes tree to find the ref's declaration
        """
        if id in scope.sym: return scope.sym[id]
        if scope.parent: return find_ref(scope.parent, id)
        raise Exception(f"undeclared var {id}")

    def bfs(scope):
        for node in scope.stmts:
            if isinstance(node, Fn):
                bfs(node.scope)
            elif isinstance(node, Scope):
                node.parent = scope
                bfs(node)
            elif isinstance(node, Var):
                scope.sym[node.id] = (f"v{v}",node.type)
            elif isinstance(node, BOp):
                for child,_ in dfs(node):
                    print(child)
                    if isinstance(child,Ref):
                        ref_id = find_ref(scope,child.id)
                        print(ref_id)
            elif isinstance(node,Ref):
                ref_id = find_ref(scope,child.id)
                print(ref_id)
    for node in ast_:
        if isinstance(node, Fn):
            bfs(node.scope)


if __name__ == "__main__": 
    ast_ = list(Prs(code).parse())
    analyze(ast_)
    print("hey")