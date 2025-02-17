from cpy.prs import Prs
from cpy.dbg import pn
from cpy.classes import *
from cpy.vst import preorder

if __name__ == "__main__": 
    code = """
    int a() {
        int b = 3;
        {
           {
               int b = 10;
               b += 1; 
           }
        }
        b += 2;
    }
    """

    def get_args(fn: Fn): 
        p = 0
        args = {}
        for arg in fn.args: 
            args[arg.id] = f"p{p}"
            p += 1
        return args

    ast_ = list(Prs(code).parse())

    p = 0
    stack = []

    def resolve(id):
        for frame in reversed(stack):
            if id in frame:
                return 
        raise Exception(f"Undeclared identifier '{id}'")

    def get_refs(stmt): 
        res = []
        if isinstance(stmt, BOp):
            res += [x for x,_ in preorder(stmt) if isinstance(x,Ref)]
        return res

    def analyze_scope(scope: Scope): 
        stack.append({})
        for item in scope.body:
            refs = get_refs(item)
            for ref in refs: resolve(ref.id)
            if isinstance(item, Var):
                global p
                stack[-1][item.id] = f"p{p}"
                p += 1
            elif isinstance(item, Scope):
                analyze_scope(item)
            elif isinstance(item, Ref):
                analyze_scope(item)
        print(stack)
        stack.pop()
    
    for node in ast_: 
        if isinstance(node, Fn):
            analyze_scope(node.body)