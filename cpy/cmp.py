from cpy.prs import Prs
import cpy.sem as sem
import cpy.tac as tac
import cpy.arm64 as arm64

def compile(code:str) -> str: 
    statements = list(Prs(code).parse())
    a,b,c = sem.analyze(statements)
    tacs = tac.to_tac((a,b,c))
    return arm64.lower(a,b,c,tacs)