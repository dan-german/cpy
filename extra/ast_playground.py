import ast
import graphviz

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

# code = "a = 2"
code = """
1 * 2 + -3
"""
print_graph(code)