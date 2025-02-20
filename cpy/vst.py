"""
Various AST traversal algorithms.
"""

from collections import deque
from cpy.prs import *
from cpy.classes import *
import cpy.dbg as dbg

bad_types = [int,str,dict,Sym]
bad_ids = ["parent"]

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
    q = deque([(node,0)])
    while q:
        top,level = q.popleft()
        if isinstance(top, ignore_types):
            continue
        elif isinstance(top, list):
            q.extend((node,level) for node in top)
        else:
            yield top,level
            q.extend(
                (val,level+1) for name, val in vars(top).items()
                if name not in bad_ids and not isinstance(val, (*bad_types, *ignore_types)) and val
            )