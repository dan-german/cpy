from cpy.prs import Prs
import cpy.sem as sem
import cpy.tac as tac
import cpy.arm64 as arm64

def compile(code:str,*,debug=False) -> str: 
    statements = list(Prs(code).parse())
    a,b,c,d = sem.analyze(statements)
    tac_table = tac.to_tac((a,b,c,d))
    print(tac_table)
    return arm64.lower(tac_table,debug)