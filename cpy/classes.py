from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

@dataclass
class Node: sym: dict = field(default_factory=dict,init=False) # scope might be the only node needing a sym table

@dataclass
class BOp(Node): 
    op: str
    left: "BOp | Const"
    right: "BOp | Const"
    def __str__(self): return f"{self.__class__.__name__}({str(self.left)}{str(self.op)}{str(self.right)})"

@dataclass
class Const(Node): 
    value: str
    def __str__(self): return f"{self.__class__.__name__}({self.value})"

@dataclass
class Var(Node):
    id: str
    type: str
    value: BOp | Const
    def __str__(self): return f"{self.__class__.__name__}(type={self.type},id={self.id},value={str(self.value)})"

@dataclass
class Ref(Node):
    id: str
    def __str__(self): return f"{self.__class__.__name__}({self.id})"

@dataclass 
class UOp(Node): 
    op: str
    operand: "Const | Ref | UOp"
    def __str__(self): return f"{self.__class__.__name__}({self.op}{self.operand})"

@dataclass
class Arg(Node): 
    type: str
    id: str
    def __str__(self): return f"{self.__class__.__name__}({self.type} {self.id})"

@dataclass
class Call(Node): 
    id: Ref
    args: list[Const | Ref | UOp]
    def __str__(self): return f"{self.__class__.__name__}({str(self.id)},args={",".join([str(x) for x in self.args])})"
    
@dataclass()
class Ret(Node): 
    value: UOp | BOp | Ref | Const = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}({str(self.value)})"

@dataclass
class Fn(Node): 
    id: str
    type: str
    args: Arg
    scope: "Scope"
    def __str__(self): return f"{self.__class__.__name__}(type={self.type},id={self.id},args=[{",".join(str(x) for x in self.args)}],scope={self.scope})"

@dataclass
class If(Node): 
    test: UOp | BOp | Ref | Const
    body: "Scope"
    else_: "UOp | BOp | Ref | Const | If" = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}(test={str(self.test)},body={str(self.body)},else={str(self.else_)})"

@dataclass
class Scope(Node): 
    stmts: list
    parent: "Scope" = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}([{",".join(str(x) for x in self.stmts)}])"