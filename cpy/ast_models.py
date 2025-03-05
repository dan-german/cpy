from dataclasses import dataclass, field

class FieldMetadata: 
    TRAVERSABLE = "TRAVERSABLE"

@dataclass
class Symbol: 
    id: str
    type: str
    scope: str
    def __str__(self): return f"{self.type},{self.id},{self.scope}"

@dataclass
class SymbolTable: 
    symbols: dict[Symbol] = field(default_factory=dict)
    def __str__(self): return ",".join(f"{k}:({str(v)})" for k,v in self.symbols.items())
    def __setitem__(self,k,v): self.symbols[k]=v
    def __getitem__(self,k): return self.symbols[k]
    def __contains__(self,v): return v in self.symbols
    def __len__(self): return len(self.symbols)

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
    id: str
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
    parent_scope: "Scope" = field(default=None,metadata={FieldMetadata.TRAVERSABLE:False})
    sym: SymbolTable = field(default_factory=SymbolTable,metadata={FieldMetadata.TRAVERSABLE:False})
    def __str__(self): return f"{self.__class__.__name__}([{",".join(str(x) for x in self.stmts)}])"

    def find_var(self,ref:Ref): 
        """
        Climb the scopes tree to find the ref's declaration
        """
        if ref.id in self.sym: return self.sym[ref.id]
        if self.parent_scope: return self.parent_scope.find_var(ref)
        return None