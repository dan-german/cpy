from cpy.tac import *
from dataclasses import dataclass
from cpy.prs import Prs

@dataclass
class BasicBlock: 
    code: list[tuple]
    idx: int
    targets: list
    def __repr__(self): 
        code = ""
        for line in self.code: code += f"\n{line[0]}) {line[1]} next_use: {line[1].next_use}"
        return f"BB: {self.idx}, targets: {self.targets}\n{"-"*40}{code}\n{"-"*40}\n"

def blockify(tac_fn:TACFn) -> list[BasicBlock]:
    print(tac_fn.symbols)
    code = [(i,v) for i,v in enumerate(tac_fn.code)]
    label_to_idx = {val.label:idx for idx,val in code if isinstance(val,TACLabel)}
    leader_idxs = {code[0][0]}
    for idx,inst in code:
        if isinstance(inst, (TACJump,TACCondJump)):
            leader_idxs.add(label_to_idx[inst.target])
            if idx + 1 < len(code): leader_idxs.add(idx + 1)
    sorted_idxs = sorted(leader_idxs)
    sorted_idxs.append(-1)

    blocks = []
    for i in range(len(sorted_idxs) - 1):
        start = sorted_idxs[i]
        end = sorted_idxs[i+1]
        blocks.append(BasicBlock(code[start:len(code) if end == -1 else end],start,None))
    print(len(blocks))

    for block in blocks:
        if isinstance(block.code[-1][1],TACJump):
            block.targets = [label_to_idx[block.code[-1][1].target]]
        elif isinstance(block.code[-1][1],TACCondJump):
            block.targets = [label_to_idx[block.code[-1][1].target], block.code[-1][0]+1]
        elif block.code[-1][0]+1 < len(code):
            block.targets = [block.code[-1][0]+1]

    return blocks

def present(blocks: list[BasicBlock]):
    from graphviz import Digraph
    dot = Digraph(filename="temp",format='svg')

    nodes = [x.idx for x in blocks]
    for block in blocks:
        if not block.targets: continue
        for target in block.targets:
            dot.edge(str(block.idx),str(target))

    for n in nodes:
        block = [block for block in blocks if block.idx == n][0]
        lines = ""
        for line in block.code:
            lines += "\n"+str(line[1])
        dot.node(name=str(n),label=lines, shape="box")

    dot.render(view=True)

def get_operand_refs(tac):
    operands = []
    left_side = None
    match tac:
        case TACOp():
            if not isinstance(tac.left, Const): operands.append(tac.left)
            if not isinstance(tac.right, Const): operands.append(tac.right)
            left_side = tac.id
        case TACAssign(): 
            if not isinstance(tac.value, Const): operands.append(tac.value)
            left_side = tac.id
        case TACRet(): 
            if not isinstance(tac.value,Const): operands.append(tac.value)
    return left_side,operands

def analyze_next_use(block: BasicBlock):
    """
    * next-use should be updated only if it's an operand
    * operand is always live
    * kill left side ref if it's not also an operand
    """
    prev: dict[int] = None
    for i in range(len(block.code)-1,-1,-1):
        code = block.code[i]
        curr_info = prev.copy() if prev else {}
        left_side,operands = get_operand_refs(code[1])
        if left_side not in operands and left_side in curr_info: del curr_info[left_side]
        for o in operands: curr_info[o] = i
        prev = code[1].next_use = curr_info
    # return infos
    print(block)

if __name__ == "__main__":
    code =\
    """
    int main() { 
        int x = 8;
        int a = 1;
        int b = a + a;
        int c = a * a;
        a = 3;
        return a+b+c+x; 
    }
    """
    code =\
    """
    int main() {
        int n = 4;
        if (n <= 2) { 
            return n;
        }
        int prev = 1;
        int curr = 2;
        int i = 2;
        while (i < n) { 
            int temp = curr;
            curr = curr + prev;
            prev = temp;
            i += 1;
        }
        return curr;
    }
    """

    ast = list(Prs(code).parse())
    sem_res = sem.analyze(ast) 
    tac_res = to_tac(sem_res)
    # import arm64 from cpy.arm64
    # from cpy.arm64 import arm64
    import cpy.arm64 as arm64
    arm = arm64.lower(tac_res)
    print(arm)
    # print(tac_res)
    blocks = blockify(tac_res.functions[0])
    present(blocks)
    res = analyze_next_use(blocks[0])
    # print(blocks)

"""

0) x0 = Const(8)
1) a0 = Const(1)
2) G0 = a0 + a0
3) b0 = G0
4) G1 = a0 * a0
5) c0 = G1
6) G2 = a0 + b0
7) G3 = G2 + c0
8) G4 = G3 + x0
9) return G4

9) G4
8) G3, x0
7) G2, x0


"""