from cpy.classes import *

# https://github.com/tinygrad/tinygrad/blob/d5183e158441145c3bc2c50615f989dc6a658895/tinygrad/helpers.py#L28
def colored(st, color, background=False): 
    return f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m" if color is not None else st  

color_map = { 
    Fn: "magenta",
    Var: "BLUE",
    BOp: "CYAN",
    UOp: "red",
    Call: "red",
    Const: "GREEN",
    Ret: "red"
}

def get_colored(instance, val=""): 
    color = color_map[type(instance)] if type(instance) in color_map else "white"
    return colored(instance.__class__.__name__ + "(", color) + val + colored(")", color)

def dfs(node, lvl=0, res=[]):
    if not node: return res
    indent = " "*lvl * 4
    if isinstance(node, Fn):
        res.append(indent + get_colored(node, f"{node.id}({",".join(str(x) for x in node.args)})"))
        for n in node.body:
            dfs(n, lvl + 1)
    if isinstance(node, Var):
        res.append(indent + get_colored(node, f"{node.type} {node.id}"))
        dfs(node.value, lvl + 1, res)
    elif isinstance(node, BOp):
        res.append(indent + get_colored(node, node.op))
        dfs(node.left, lvl + 1, res)
        dfs(node.right, lvl + 1, res)
    elif isinstance(node, Const):
        res.append(indent + get_colored(node, node.value))
    elif isinstance(node, UOp):
        res.append(indent + get_colored(node, node.op))
        dfs(node.operand, lvl + 1, res)
    elif isinstance(node, Ret): 
        res.append(indent + get_colored(node))
        dfs(node.value, lvl + 1, res)
    elif isinstance(node, list): 
        for item in node: 
            dfs(item, lvl + 1, res)
    elif isinstance(node, Call): 
        res.append(indent + get_colored(node, node.id.id))
        dfs(node.args, lvl + 1, res)
    elif isinstance(node, Ref): 
        res.append(indent + get_colored(node, node.id))

    return res

def pn(node): print("\n".join(dfs(node)))