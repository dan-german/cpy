import cpy.dbg as dbg
from cpy.prs import Prs
from cpy.classes import *
from cpy.vst import dfs,bfs

class GlobalCall(Exception): 
    def __init__(self,msg): super().__init__(f"Global scope call '{msg}'")
    
class Redef(Exception): 
    def __init__(self,msg): super().__init__(f"Redefinition of '{msg}'")

class Undeclared(Exception): 
    def __init__(self,msg): super().__init__(f"Use of undeclared id '{msg}'")

class SymbolTable: 
    @dataclass 
    class Entry: 
        type: str
        value: str
        def __repr__(self): return f"{self.type} {self.value}"

    f = v = 0

    def __init__(self,parent=None): 
        self.functions = {}
        self.vars = {}
        self.functions = {}

    def add_var(self,type,id):
        if id in self: raise Redef(id)
        self.vars[id] = SymbolTable.Entry(type,f"v{SymbolTable.v}")
        SymbolTable.v += 1

    def add_fn(self,type,id):
        if id in self: raise Redef(id)
        self.vars[id] = SymbolTable.Entry(type,f"f{SymbolTable.f}")
        SymbolTable.f += 1

    def has_var(self,id): 
        if id in self: return self.vars[id]
        return self.parent.has_var(id) if self.parent else None

    # def add_child(self, table): 
    #     self.children.append(table)
        
    def add_fn(self, table,id): 
        self.functions[id] = table

    def __contains__(self, item):
        return item in [*self.functions,*self.vars] 

    def __repr__(self): 
        return f"vars: {self.vars}"

class Sem: 
    def __init__(self, code: str): 
        self.prs = Prs(code).parse()

    def get_refs(self,stmt): 
        res = []
        if isinstance(stmt, BOp):
            res += [x for x,_ in dfs(stmt) if isinstance(x,Ref)]
        elif isinstance(stmt, Var):
            res += self.get_refs(stmt.value)
        elif isinstance(stmt, Ref): 
            res.append(stmt)
        return res

    def check_refs(self,root,table:SymbolTable):
        for node,_ in dfs(root): 
            if isinstance(node, Ref) and not table.has_var(node.id):  
                raise Undeclared(node.id)

    def analyze(self,node,table:SymbolTable,parent=None):
        for node in node:
            if isinstance(node, (Var,Scope,BOp)): self.check_refs(node,table)
            if isinstance(node, Fn):
                SymbolTable.v = 0
                SymbolTable.f = 0
                if node.id in table: raise Redef(node.id)
                table.add_fn(self.analyze(node.scope.stmts,table),node.id)
            if isinstance(node, Scope):
                self.analyze(node.stmts,table)
                # table.add_child(self.analyze(node.stmts,table))
            elif isinstance(node, Var):
                table.add_var(node.type, node.id)
            elif isinstance(node, Ref):
                print(f"found ref: {node}")
        return table

    def run(self): 
        table = SymbolTable()
        return self.analyze(self.prs,table)

if __name__ == "__main__": 
    code = """
    void f(){
        int a=1; 
        {
            int a=2;
            {
                a=3;
            }
            int b=4;
        }
    }
    """

    dbg.pn(list(Prs(code).parse()))
    # void a(){int b=1;{int b=2;{int b=3;}}}
    # res = Sem(code).run()
    # dbg.pst(res)

"""
*****tree******

fn:
  c: 
    int 

*****flattend*****

fn: 
  c: 
    vars: 
      int v0 ('a')
      int v1 ('a')
      int v2 ('a')

"""