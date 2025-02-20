"""
Various AST traversal algorithms.
"""

from collections import deque
from cpy.prs import *
from cpy.classes import *
import cpy.dbg as dbg

bad_types = [int,str,dict,Sym]
bad_ids = ["parent"]

def postorder(node):
    stack = [(node,False)]
    while stack: 
        top,processed=stack.pop()
        if type(top) == list:
            stack.extend([(node,False) for node in reversed(top)])
        elif processed: 
            yield top
        else: 
            stack.append((top,True))
            for name in reversed(vars(top)):
                if name in bad_ids: continue
                val = getattr(top, name)
                if val and type(val) not in bad_types:
                    stack.append((val,False)) 

def preorder(node):
    stack = [(node, 0)]
    while stack: 
        curr,level=stack.pop()
        if type(curr) == list:
            stack.extend(reversed([(item,level) for item in curr]))
        else: 
            yield curr,level
            for name in reversed(vars(curr)):
                if name in bad_ids: continue
                val = getattr(curr, name)
                if val and type(val) not in bad_types:
                    stack.append((val,level+1))

def bfs(node, ignore_types=()):
    q = deque([node])
    while q:
        top = q.popleft()
        if isinstance(top, ignore_types):
            continue
        elif isinstance(top, list):
            q.extend(top)
        else:
            yield top
            q.extend(
                val for name, val in vars(top).items()
                if name not in bad_ids and not isinstance(val, (*bad_types, *ignore_types)) and val
            )