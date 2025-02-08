from dataclasses import dataclass

@dataclass
class BinOp: 
    op: str
    left: str
    right: str

@dataclass
class Const: value: str

@dataclass
class VarDecl: 
    id: str
    type: str
    value: BinOp | Const

@dataclass
class Ref: 
    id: str
    type: str

@dataclass 
class UOp: 
    op: str
    operand: "Const | Ref | UOp"

@dataclass
class FuncDecl: 
    id: str
    type: str
    body: list