from cpy.prs import Prs
import cpy.sem as sem
import cpy.tac as tac
import cpy.arm64 as arm64
from enum import Enum, auto

class Output(Enum): 
    ast = auto()
    sem = auto()
    tac = auto()
    arm64 = auto()

def compile(code:str,*,output:Output=Output.arm64, debug=False): 
    statements = list(Prs(code).parse())
    sem_result = sem.analyze(statements)
    tac_table = tac.to_tac(sem_result)
    arm = arm64.lower(tac_table,debug)
    match output: 
        case Output.ast: return statements
        case Output.sem: return sem_result
        case Output.tac: return tac_table
        case Output.arm64: return arm
    raise Exception()