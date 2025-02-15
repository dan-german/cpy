import ast
import graphviz
ast.FunctionDef

def print_graph(code):
    tree = ast.parse(code)
    print(ast.dump(tree, indent=4))

def draw_graph(code):
    tree = ast.parse(code)
    dot = graphviz.Digraph()
    for node in ast.walk(tree):
        dot.node(str(id(node)), node.__class__.__name__)
        for child in ast.iter_child_nodes(node):
            dot.edge(str(id(node)), str(id(child)))
    dot.render("ast", format="png", view=True) 

if __name__ == '__main__': 
    code = """
if 1:
    pass
elif 2 and 3: 
    pass
# elif 3: 
#     pass
# else: 
#     pass"""

    print_graph(code)