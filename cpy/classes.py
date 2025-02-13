from dataclasses import dataclass

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
    value: BOp | Const
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
    id: str
    args: list[Const | Ref | UOp]
    def __str__(self): return f"{self.__class__.__name__}({str(self.id)},args={",".join([str(x) for x in self.args])})"
    
@dataclass
class Return: 
    value: UOp | BOp | Ref | Const
    def __str__(self): return f"{self.__class__.__name__}({str(self.value)})"

@dataclass
class Func: 
    id: str
    type: str
    args: Arg
    body: list
    def __str__(self): return f"{self.__class__.__name__}(type={self.type},id={self.id},args=[{",".join(str(x) for x in self.args)}],stmts=[{",".join(str(x) for x in self.body)}])"