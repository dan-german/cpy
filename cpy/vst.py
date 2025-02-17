from cpy.prs import *
from cpy.classes import *

def preorder(node, level=0):
    if not node: return
    yield node, level
    if isinstance(node, Fn):
        yield from preorder(node.body, level+1)
    if isinstance(node, Var):
        yield from preorder(node.value, level+1)
    elif isinstance(node, BOp):
        yield from preorder(node.left, level+1)
        yield from preorder(node.right, level+1)
    elif isinstance(node, UOp):
        yield from preorder(node.operand, level+1)
    elif isinstance(node, Ret): 
        yield from preorder(node.value, level+1)
    elif isinstance(node, list): 
        for item in node: 
            yield from preorder(item, level+1)
    elif isinstance(node, Call): 
        yield from preorder(node.args, level+1)
    elif isinstance(node, Scope): 
        for n in node.body:
            yield from preorder(n, level+1)