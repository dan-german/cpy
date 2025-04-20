from cpy.tac import *
from dataclasses import dataclass

@dataclass
class BasicBlock: 
    code: list
    idx: int
    targets: list
    def __repr__(self): 
        return f"idx: {self.idx}, targets: {self.targets} code:\n{"\n".join(map(str,self.code))}"

def blockify(tac_table:TACTable) -> list:
    code = [(i,v) for i,v in enumerate(tac_table.functions[0].code)]
    label_to_idx = {val.label:idx for idx,val in code if isinstance(val,TACLabel)}
    leader_idxs = {code[0][0]}
    for idx,inst in code:
        if isinstance(inst, (TACJump,TACCondJump)):
            leader_idxs.add(label_to_idx[inst.target])
            if idx + 1 < len(code): leader_idxs.add(idx + 1)
    print("ldr",leader_idxs)
    sorted_idxs = sorted(leader_idxs)
    sorted_idxs.append(-1)

    blocks = []
    for i in range(len(sorted_idxs) - 1):
        start = sorted_idxs[i]
        end = sorted_idxs[i+1]
        blocks.append(BasicBlock(code[start:len(code) if end == -1 else end],start,None))

    for block in blocks:
        if isinstance(block.code[-1][1],TACJump):
            block.targets = [label_to_idx[block.code[-1][1].target]]
        elif isinstance(block.code[-1][1],TACCondJump):
            block.targets = [label_to_idx[block.code[-1][1].target], block.code[-1][0]+1]
        elif block.code[-1][0]+1 < len(code):
            print("last", block.code[-1][0]+1)
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

if __name__ == "__main__":
    code =\
    """
    int main() { 
        int a = 1;
        int b = a + a;
        return b * 2;
    }
    """

    ast = list(Prs(code).parse())
    a,b,c,d=sem.analyze(ast) 
    res = to_tac((a,b,c,d))

    blocks = blockify(res)
    present(blocks)