from cpy.tac import *
from dataclasses import dataclass
from cpy.prs import Prs

@dataclass
class BasicBlock: 
    code: list[tuple[int,TAC]]
    id: int
    targets: list
    def __repr__(self): 
        code = ""
        for line in self.code:
            code += f"\n{line[0]:<2}) {str(line[1]):<30} next_use: {line[1].next_use}"
        return f"BB: {self.id}, targets: {self.targets}\n{"-"*60}{code}\n{"-"*60}\n"

@dataclass 
class Blocks:
    blocks: list[BasicBlock] = field(default_factory=list)
    def __repr__(self):
        return "implement"
    def __len__(self): return len(self.blocks)
    def __getitem__(self, idx) -> BasicBlock: return self.blocks[idx]
    def __setitem__(self, idx, item) -> BasicBlock: self.blocks[idx] = item
    def __repr__(self): 
        res = ""
        for block in self.blocks:
            res += f"BasicBlock {block.id}, targets: {block.targets}:\n"
            for code in block.code: 
                res += f"{code[0]}) {code[1]}"
                if code[1].next_use: 
                    res += f" uses: {code[1].next_use}"
                res += "\n"
        return res

# 8.4.1 Basic blocks
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
    count = 0
    for i in range(len(sorted_idxs)):
        start = sorted_idxs[i]
        end = sorted_idxs[i+1] if i+1 < len(sorted_idxs) else len(code)
        blocks.blocks.append(BasicBlock(code[start:end],count,None))
        count += 1

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

    nodes = [x.id for x in blocks]
    for block in blocks:
        if not block.targets: continue
        for target in block.targets:
            dot.edge(str(block.id),str(target))

    for n in nodes:
        block = [block for block in blocks if block.id == n][0]
        lines = ""
        for line in block.code:
            lines += f"{line[0]}) {line[1]}\n"
        dot.node(name=str(n),label=lines, shape="box")

    dot.render(view=True)

def show_dag(dag:dict): 
    from graphviz import Digraph
    dot = Digraph(filename="temp",format="svg")
    for item in dag.values():
        print(item.op)
        dot.node(name=str(item),label=item.gvrepr())
    for item in dag.values():
        for operand in item.operands:
            dot.edge(str(item), str(operand))
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
def analyze_next_uses(blocks: Blocks): 
    unused_lines = []
    uses: dict[str, tuple[int,int]] = {}# tuple = block id, line
    for block in reversed(blocks):
        print("id", block.id)
        for line, inst in reversed(block.code): 
            left_side,operands = get_operand_refs(inst)
            for op in operands: uses[op] = (block.id, line)
            if left_side and left_side not in uses: unused_lines.append(line)
            if left_side in uses and uses[left_side][0] == block.id and left_side not in operands: 
                print("DELETING: ", uses[left_side][0])
                del uses[left_side]
            inst.next_use = uses.copy()
    return unused_lines

def fold(blocks: Blocks):
    def apply(left:Const,right:Const,op):
        match op: 
            case "+": return int(left.value) + int(right.value)
            case "*": return int(left.value) * int(right.value)
            case "/": return int(left.value) / int(right.value)
            case "-": return int(left.value) - int(right.value)
            case "==": return int(left.value) == int(right.value)
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

from cpy.dag import *
def to_dag(block: BasicBlock):
    graph: dict[DNode,DNode] = {}
    defs = {}
    def get_op(operand):
        res = None
        match operand: 
            case str(): 
                suffix = str(defs[operand]) if operand in defs else ""
                res = DNode(op=DOp.Ref, value=operand + "_" + suffix)
            case Const(): res = DNode(op=DOp.ConstInt, value=operand.value)
        if res in graph: return graph[res]
        graph[res] = res
        return res

    for line,tac in block.code:
        print(line,tac)
        match tac:
            case TACAssign():
                defs[tac.id] = line
                ref_node = DNode(op=DOp.Ref,value=tac.id)
                graph[str(ref_node)] = ref_node
                match tac.value:
                    case Const():
                        dnode = DNode(op=DOp.ConstInt, value=tac.value.value)
                        graph[str(dnode)] = dnode
                        graph[str(ref_node)].value = tac.id
                        graph[str(ref_node)].operands = [dnode]
            case TACOp():
                defs[tac.id] = line
                operands = [get_op(tac.left), get_op(tac.right)]
                bop_node = DNode(op=tac.op,operands=operands)
                graph[str(bop_node)] = bop_node
                ref_node = DNode(op=DOp.Ref, value=tac.id)
                ref_node.operands = [bop_node]
                graph[str(ref_node)] = ref_node
    # print(graph)
    return graph

if __name__ == "__main__":
    code=\
    """
    int f(int b, int c, int d) { 
        int a = b + c;
        b = b - d;
        c = c + d;
        int e = b + c;
        return e;
    }
    """

    # code=\
    # """
    # int f() { 
    #     int a = 1;
    #     a = 2;
    #     return a;
    # }
    # """

    ast = list(Prs(code).parse())
    sem_res = sem.analyze(ast) 
    tac = to_tac(sem_res)
    blocks = blockify_fn(tac.functions[0])
    dag = to_dag(blocks[0])
    for item in dag.values(): 
        print(item.op)
    # show_dag(dag)