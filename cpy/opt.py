from cpy.tac import *
from dataclasses import dataclass
from cpy.prs import Prs

@dataclass
class BasicBlock: 
    code: list[tuple[int,TAC]]
    idx: int
    targets: list
    def __repr__(self): 
        code = ""
        for line in self.code:
            code += f"\n{line[0]:<2}) {str(line[1]):<30} next_use: {line[1].next_use}"
        return f"BB: {self.idx}, targets: {self.targets}\n{"-"*60}{code}\n{"-"*60}\n"

@dataclass 
class Blocks:
    blocks: list[BasicBlock] = field(default_factory=list)
    def __repr__(self):
        pass
    def __len__(self): return len(self.blocks)
    def __getitem__(self, idx) -> BasicBlock: return self.blocks[idx]
    def __setitem__(self, idx, item) -> BasicBlock: self.blocks[idx] = item
    def __repr__(self): 
        res = ""
        for block in self.blocks:
            res += f"BasicBlock {block.idx}, targets: {block.targets}:\n"
            for code in block.code: 
                res += f"{code[0]}) {code[1]}"
                if code[1].next_use: 
                    res += f" uses: {code[1].next_use}"
                res += "\n"
        return res

# 8.4.1 Basic Blocks
def blockify_fn(tac_fn:TACFn) -> list[BasicBlock]:
    code = [(i,v) for i,v in enumerate(tac_fn.code)]
    label_to_idx = {val.label:idx for idx,val in code if isinstance(val,TACLabel)}
    leader_idxs = {code[0][0]}
    for idx,inst in code:
        if isinstance(inst, (TACJump,TACCondJump)):
            leader_idxs.add(label_to_idx[inst.target])
            if isinstance(inst,TACCondJump) and idx + 1 < len(code):
                leader_idxs.add(idx + 1)
    sorted_idxs = sorted(leader_idxs)

    blocks = Blocks()
    for i in range(len(sorted_idxs)):
        start = sorted_idxs[i]
        end = sorted_idxs[i+1] if i+1 < len(sorted_idxs) else len(code)
        blocks.blocks.append(BasicBlock(code[start:end],start,None))

    for block in blocks.blocks:
        if isinstance(block.code[-1][1],TACJump):
            block.targets = [label_to_idx[block.code[-1][1].target]]
        elif isinstance(block.code[-1][1],TACCondJump):
            block.targets = [label_to_idx[block.code[-1][1].target], block.code[-1][0]+1]
        elif block.code[-1][0]+1 < len(code):
            block.targets = [block.code[-1][0]+1]
    return blocks

# 8.4.3 Flow Graphs
def show_cfg(blocks: list[BasicBlock]):
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

def get_operand_refs(tac:TAC):
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

# 8.4.2 Next-Use Information
def analyze_next_uses(blocks: Blocks, eliminate_dead_code=False): 
    uses: dict[str, int] = {}
    unused_lines = []
    for block in reversed(blocks):
        for line, inst in reversed(block.code):
            left_side,operands = get_operand_refs(inst)
            for op in operands: uses[op] = line
            if left_side and left_side not in uses and eliminate_dead_code: unused_lines.append(line)
            if left_side in uses and left_side not in operands: del uses[left_side]
            inst.next_use = uses.copy()
    return unused_lines

def fold(blocks: Blocks):
    def apply(left:Const,right:Const,op):
        match op: 
            case "+": return int(left.value) + int(right.value)
            case "*": return int(left.value) * int(right.value)
            case "/": return int(left.value) / int(right.value)
            case "-": return int(left.value) - int(right.value)
        raise Exception(f"no matching op: {op}")

    def get_const(operand):
        match operand:
            case Const(): return operand
            case str(): return const_dict[operand] if operand in const_dict else None
    
    const_dict = {}
    for i, line_tac_pair in enumerate(blocks[0].code):
        tac = line_tac_pair[1]
        match tac: 
            case TACAssign():
                match tac.value: 
                    case Const():
                        const_dict[tac.id] = tac.value
                    case str():
                        const_dict[tac.id] = const_dict[tac.value]
                        blocks.blocks[0].code[i] = (line_tac_pair[0], TACAssign(tac.id, const_dict[tac.value],"="))
            case TACOp():
                left = get_const(tac.left)
                right = get_const(tac.right)
                if left and right: 
                    const_dict[tac.id] = Const(apply(left,right,tac.op))
                    blocks.blocks[0].code[i] = (line_tac_pair[0], TACAssign(tac.id, const_dict[tac.id] ,"="))

if __name__ == "__main__":
    code =\
    """
    int main() { 
        int a = 1;
        int b = 2;
        return a*b;
    }
    """
    ast = list(Prs(code).parse())
    sem_res = sem.analyze(ast) 
    tac_res = to_tac(sem_res)
    blocks = blockify_fn(tac_res.functions[0])
    fold(blocks)
    unused_lines = analyze_next_uses(blocks,True)
    for line in unused_lines: 
        blocks[0].code.pop(line)
    print(blocks)