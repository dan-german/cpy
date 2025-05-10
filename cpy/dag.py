from enum import Enum, auto

class DOp(Enum):
    ConstInt = auto()
    # Add = auto()
    # Sub = auto()
    # Mul = auto()
    # Div = auto()
    Ref = auto()

class DNode: 
    def __init__(self,*,op:DOp,operands=[],value=None):
        self.op = op
        self.operands = operands
        self.value = value
    
    def __repr__(self): 
        res = f"({self.op}"
        if self.operands: res += f" {self.operands}"
        if self.value: res += f"({self.value})"
        return res + ")"
    
    def gvrepr(self): 
        match self.op:
            case DOp.ConstInt: return self.value
            case DOp.Ref: return self.value
        print('shabobr')
        return str(self.op)
    
    def __hash__(self): return hash((self.op, tuple(self.operands), self.value))
    def __eq__(self,other): return str(self) == str(other)

# def to_dag(tac_table: TACTable):
#     print(tac_table)
#     dict = {}
#     fn = tac_table.functions[0]
#     for code in fn.code: 
#         pass

# if __name__ == "__main__":
#     print("hi")
#     code =\
#     """
#     int f() { 
#         int b = 1;
#         int c = 2;
#         int d = 3;
#         int a = b + c;
#         b = b - d;
#         c = c + d;
#         int e = b + c;
#     }
#     """
#     from cpy import compiler 
#     tac = compiler.compile(code,output=compiler.Output.tac)
#     # print(tac)
#     to_dag(tac)