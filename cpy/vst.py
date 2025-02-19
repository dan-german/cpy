from collections import deque
from cpy.prs import *
from cpy.classes import *

def dfs(node):
    stack = [(node, 0)]
    while stack: 
        curr,level=stack.pop()
        if type(curr) == list:
            stack.extend(reversed([(item,level+1) for item in curr]))
        else: 
            yield curr,level
            for name in reversed(vars(curr)):
                val = getattr(curr, name)
                if val and type(val) not in [int,str]:
                    stack.append((val,level+1))

def bfs(node, ignore_types=()):
    q = deque([node])
    while q:
        top = q.popleft()
        if isinstance(top, ignore_types): continue
        elif isinstance(top, list): q.extend(top)
        else:
            yield top
            q.extend(
                val for val in vars(top).values()
                if not isinstance(val, (int, str, dict,ignore_types))
            )

if __name__ == "__main__":
    code = """
        int f(int a) { 
            int b = a;
            return b * 2;
        }"""
    import cpy.dbg as dbg
    ast_ = list(Prs(code).parse())
    dbg.pn(ast_)
    print()
    # for node in preorder(ast_):
    #     print(type(node))
