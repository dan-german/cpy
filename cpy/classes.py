from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict

@dataclass
class Sym:
    vars: dict = field(default_factory=dict)
    functions: dict = field(default_factory=dict)
    def __contains__(self,other): return other in self.vars or other in self.functions
    def __len__(self): return len(self.vars) + len(self.functions)
    def __str__(self): return f"vars: {str(self.vars)} fn: {str(self.functions)}"

@dataclass
class BOp: 
    op: str
    left: "BOp | Const"
    right: "BOp | Const"
    def __str__(self): return f"{self.__class__.__name__}({str(self.left)}{str(self.op)}{str(self.right)})"

@dataclass
class Const: 
    value: str
    def __str__(self): return f"{self.__class__.__name__}({self.value})"

@dataclass
class Var:
    id: str
    type: str
    value: BOp | Const = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}(type={self.type},id={self.id},value={str(self.value)})"

@dataclass
class Ref:
    id: str
    def __str__(self): return f"{self.__class__.__name__}({self.id})"

@dataclass 
class UOp: 
    op: str
    operand: "Const | Ref | UOp"
    def __str__(self): return f"{self.__class__.__name__}({self.op}{self.operand})"

@dataclass
class Arg: 
    type: str
    id: str
    def __str__(self): return f"{self.__class__.__name__}({self.type} {self.id})"

@dataclass
class Call: 
    id: Ref
    args: list[Const | Ref | UOp]
    def __str__(self): return f"{self.__class__.__name__}({str(self.id)},args={",".join([str(x) for x in self.args])})"
    
@dataclass()
class Ret: 
    value: UOp | BOp | Ref | Const = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}({str(self.value)})"

@dataclass
class Fn: 
    id: str
    type: str
    args: Arg
    scope: "Scope"
    def __str__(self): return f"{self.__class__.__name__}(type={self.type},id={self.id},args=[{",".join(str(x) for x in self.args)}],scope={self.scope})"

@dataclass
class If: 
    test: UOp | BOp | Ref | Const
    body: "Scope"
    else_: "UOp | BOp | Ref | Const | If" = field(default=None)
    def __str__(self): return f"{self.__class__.__name__}(test={str(self.test)},body={str(self.body)},else={str(self.else_)})"

@dataclass
class Scope: 
    stmts: list
    parent: "Scope" = field(default=None)
    sym: Sym = field(default_factory=Sym)
    def __str__(self): return f"{self.__class__.__name__}([{",".join(str(x) for x in self.stmts)}])"