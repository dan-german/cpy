from collections import deque
from cpy.prs import *
from cpy.classes import *

bad_types = [int,str,dict,Sym]
bad_ids = ["parent"]

def dfs(node):
    stack = [(node, 0)]
    while stack: 
        curr,level=stack.pop()
        if type(curr) == list:
            stack.extend(reversed([(item,level+1) for item in curr]))
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

if __name__ == "__main__":
    code = "void f(){int a;}"
    ast_ = list(Prs(code).parse())
    for node in bfs(ast_):
        print(node)

    # for node in dfs(ast_):
    #   print(node)
    #   print(type(node))
