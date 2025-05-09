from cpy.prs import Prs
import cpy.sem as sem
import cpy.tac as tac
import cpy.arm64 as arm64

def compile(code:str,*,debug=False) -> str: 
    statements = list(Prs(code).parse())
    sem_result = sem.analyze(statements)
    tac_table = tac.to_tac(sem_result)
    print(tac_table)
    return arm64.lower(tac_table,debug)