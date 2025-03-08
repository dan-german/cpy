"""
Various AST traversal algorithms.
"""

from collections import deque
from cpy.prs import *
from cpy.ast_models import *
from dataclasses import fields

IGNORE_TYPES = (int,str,dict)

def _get_children(node,level:int): 
    if not node: return []
    if isinstance(node,list): return [(n,level) for n in node]
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
            if not isinstance(top,list): yield top
            continue
        stack.append((top,True))
        stack.extend([(n,False) for n,_ in reversed(_get_children(top,0))])

def preorder(node):
    stack = [(node, 0)]
    while stack: 
        top,level=stack.pop()
        if not isinstance(top, list): yield top, level
        stack.extend(reversed(_get_children(top,level)))

def bfs(node):
    q = deque([(node,0)])
    while q:
        top,level = q.popleft()
        if not isinstance(top, list): yield top, level
        q.extend(_get_children(top,level))