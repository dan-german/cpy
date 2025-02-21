"""
Various AST traversal algorithms.
"""

from collections import deque
from cpy.prs import *
from cpy.ast_models import *
import cpy.dbg as dbg
from dataclasses import fields

IGNORE_TYPES = (int,str,dict,Sym)

def get_next_level(node,level:int): 
    nodes = []
    for f in fields(node):
        if f.type in IGNORE_TYPES: continue
        if f.metadata.get(FieldMetadata.TRAVERSABLE) is False: continue
        nodes.append((getattr(node, f.name), level + 1))
    return nodes

def postorder(node): 
    stack = [(node,False)] 
    while stack: 
        top,processed=stack.pop()
        if processed: 
            yield top
        elif type(top) == list: 
            stack.extend([item,False] for item in reversed(top))
        else: 
            stack.append((top,True))
            stack.extend([(n,False) for n,_ in reversed(get_next_level(top,0))])

def preorder(node):
    stack = [(node, 0)]
    while stack: 
        top,level=stack.pop()
        if type(top) == list:
            stack.extend(reversed([(item,level) for item in top]))
        else: 
            yield top,level
            stack.extend(reversed(get_next_level(top,level)))

def bfs(node):
    q = deque([(node,0)])
    while q:
        top,level = q.popleft()
        if isinstance(top, list):
            q.extend((node,level) for node in top)
        else:
            yield top,level
            q.extend(get_next_level(top,level))

if __name__ == "__main__":
    ast = list(Prs("1*2").parse())

    for node in postorder(ast):
        print(node)