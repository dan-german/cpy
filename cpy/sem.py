from cpy.prs import Prs
from cpy.debug import pn
from cpy.classes import *

if __name__ == "__main__": 
    code="""
    int f(int a) { int b = 3; return a * b; }
    int main() { return f(5); }
    """

    ast_ = list(Prs(code).parse())

    pn(ast_)

    functions = {}    

    def get_scope_locals(): 
        pass

    def inspect_fn(fn: Fn):
        args = {}
        locals = {}

        for arg in fn.args: 
            if arg.id in args: raise Exception(f"Duplicate args: {item.id}")
            args[arg.id] = arg.type

        # for local in fn.: 
        #     if arg.id in args: raise Exception(f"Duplicate args: {item.id}")
        #     args[arg.id] = arg.type

        functions[fn.id] = { "args": args, "locals": locals }

    for item in ast_:
        if isinstance(item, Fn):
            if item.id in functions: raise Exception(f"Duplicate identifier: {item.id}")
            inspect_fn(item)

    print(functions)

"""
***** ast *****


Func(f(Arg(int a)))
    Return()
        BOp(*)
            Ref(a)
            Const(3)
Func(main())
    Return()
        Call(f)
                Const(5)

***** sym_tables *****


functions: 
    f: 
        params: {(int,a)}
        locals: {(int,b)}
    main: 
        params: {}
        locals: {}
"""