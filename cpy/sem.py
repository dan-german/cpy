from prs import Prs
from debug import pn
from classes import *
# class Sem: 
#     def __init__(self, code: str): 


if __name__ == "__main__": 
    code="""
    int f(int a) { int b = 3; return a * b; }
    int main() { return f(5); }
    """

    ast_ = list(Prs(code).parse())

    functions = {}    

    # for item in ast_: 
    #     if isinstance(item, Fn):
    #     pn(item)


    # pn(ast_)

    # print(ast_)
"""
ast: 

Func(f(Arg(int a)))
    Return()
        BOp(*)
            Ref(a)
            Const(3)
Func(main())
    Return()
        Call(f)
                Const(5)

sym_tables: 

functions: 
    f: 
        params: {(int,a)}
        locals: {(int,b)}
    main: 
        params: {}
        locals: {}
"""