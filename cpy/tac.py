from cpy.prs import Prs
from cpy.classes import *
from cpy.dbg import pn

code="""
int f() { 
    int a = 1;
    int b = 1;
    return a + b;
}
int main() { return f(); }
"""

class TAC: 
    def __init__(self, type: str):
        self.type = type

class TACGen: 
    def __init__(self, code):
        self.ast_ = Prs(code).parse()
        self.codes = []
        self.i = 0
        print("Generating tac for: ")
        pn(self.ast_)

    def get_name(self, *kwargs): 
        name = f"t{self.i}"
        self.i += 1
        return name

    def generate(self): 
        def dfs(node): 
            if not node: return
            if isinstance(node, Const): return node.value
            elif isinstance(node, BOp):
                left = dfs(node.left)
                right = dfs(node.right)
                op = node.op
                name = self.get_name()
                res = f"{name}={left}{op}{right}"
                self.codes.append(res)
                return name
            elif isinstance(node, Fn): 
                name = node.id
                self.codes.append(f"{name}:")
                for item in node.scope: dfs(item)
            elif isinstance(node, Ret): 
                return_value = dfs(node.value)
                self.codes.append(f"return {return_value}")
            elif isinstance(node, Call): 
                return_value = dfs(node.value)
                self.codes.append(f"return {return_value}")
        for item in self.ast_: 
            dfs(item)
        return self.codes

"""
f:
    param p0
    t0 = p0 * 3
    return t0
main: 
    param 5
    t0 = call f
    ret t0
"""

if __name__ == "__main__": 
    code = """
int f(int a) { return a * 3; }
//int main() { return f(5); }
"""
    # code = """1*2+3"""
    res = TACGen(code).generate()
    for item in res: 
        print(item)