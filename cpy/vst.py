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

def bfs(node):
    q = deque([node])
    while q: 
        top = q.popleft()
        if type(top) == list: 
            q += top
        else:
            yield top
            for name in vars(top): 
                val = getattr(top,name)
                if type(val) not in [int,str]:
                    q.append(val)

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
