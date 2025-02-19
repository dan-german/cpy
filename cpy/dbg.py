from cpy.classes import *
from cpy.vst import dfs
from cpy.lex import Lex

# https://github.com/tinygrad/tinygrad/blob/d5183e158441145c3bc2c50615f989dc6a658895/tinygrad/helpers.py#L28
def colored(st, color, background=False): 
    return f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m" if color is not None else st  

color_map = { 
    Fn: "MAGENTA",
    Var: "BLUE",
    BOp: "CYAN",
    UOp: "RED",
    Call: "RED",
    Const: "GREEN",
    Ret: "RED",
    Scope: "YELLOW"
}

def get_colored(instance, val=""): 
    color = color_map[type(instance)] if type(instance) in color_map else "white"
    return colored(instance.__class__.__name__ + f"({val})", color)

def pn(node): 
    def visit_with_formatting(node, lvl=0, res=None):
        if not node: return [] if res is None else res
    
        res = res or []
        indent = lambda lvl: " " * lvl * 4 if lvl > 0 else ""
    
        format_map = {
            Fn: lambda n: f"{n.id}({','.join(map(str, n.args))})",
            Var: lambda n: f"{n.type} {n.id}",
            BOp: lambda n: n.op,
            Const: lambda n: n.value,
            UOp: lambda n: n.op,
            Ret: lambda _: "",
            Call: lambda n: n.id.id,
            Ref: lambda n: n.id,
            Scope: lambda _: ""
        }
    
        for n, lvl in dfs(node):
            if type(n) in format_map:
                res.append(indent(lvl) + get_colored(n, format_map[type(n)](n)))
    
        return res

    print("\n".join(visit_with_formatting(node)))

def pst(table): 
    def print_vars(table):
        for type,value in table.vars.items():
            print(f"    {value} '({type})'")
            for child in table.children:
                print_vars(child)

    print("fn:")
    for fn,sym_table in table.functions.items():
        print(f"  {fn}:")
        print_vars(sym_table)