from dataclasses import dataclass

@dataclass
class BOp: 
    op: str
    left: "BOp | Const"
    right: "BOp | Const"

    def __str__(self): return f"({ str(self.left) }{ str(self.op) }{ str(self.right) })"

@dataclass
class Const: 
    value: str
    def __str__(self): return self.value

@dataclass
class VarDecl: 
    id: str
    type: str
    value: BOp | Const

@dataclass
class Ref: 
    id: str
    def __str__(self): return self.id

@dataclass 
class UOp: 
    op: str
    operand: "Const | Ref | UOp"
    def __str__(self): 
        return str(self.op) if not self.operand else f"({self.op}{self.operand})"

@dataclass
class FuncDecl: 
    id: str
    type: str
    body: list