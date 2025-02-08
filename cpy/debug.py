from cpy.classes import *

# https://github.com/tinygrad/tinygrad/blob/d5183e158441145c3bc2c50615f989dc6a658895/tinygrad/helpers.py#L28
def colored(st, color, background=False): return f"\u001b[{10*background+60*(color.upper() == color)+30+['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'].index(color.lower())}m{st}\u001b[0m" if color is not None else st  # replace the termcolor library with one line  # noqa: E501

color_map = { 
    VarDecl: "BLUE",
    BinOp: "CYAN",
    UOp: "red",
    Const: "GREEN"
}

def get_colored(instance, val): 
    color = color_map[type(instance)]
    return colored(instance.__class__.__name__ + "(", color) + val + colored(")", color)

def dfs(node, lvl=0, res=None):
    if res is None:
        res = []

    if not node: return res
    indent = " "*lvl * 4
    if isinstance(node, VarDecl):
        res.append(indent + get_colored(node, node.id))
        dfs(node.value, lvl + 1, res)
    elif isinstance(node, BinOp):
        res.append(indent + get_colored(node, node.op))
        dfs(node.left, lvl + 1, res)
        dfs(node.right, lvl + 1, res)
    elif isinstance(node, Const):
        res.append(indent + get_colored(node, node.value))
    elif isinstance(node, UOp):
        res.append(indent + get_colored(node, node.op))
        dfs(node.operand, lvl + 1, res)

    return res

def print_node(node): 
    res = dfs(node)
    return "\n".join(res)

import sys

def attach_repr():
    current_module = sys.modules[__name__]
    classes = [cls for cls in vars(current_module).values() if isinstance(cls, type)]
    for cls in classes: cls.__repr__ = print_node
attach_repr()