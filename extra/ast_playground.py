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
    code = """\
a = 1\n
a + a\n
"""
    # code = "a + b + c"
    print_graph(code)


#     If(
#         test=Constant(value=1),
#         body=[
#             Pass()],
#         orelse=[
#             If(
#                 test=BoolOp(
#                     op=And(),
#                     values=[
#                         Constant(value=2),
#                         Constant(value=3)]),
#                 body=[
#                     Pass()],
#                 orelse=[
#                     If(
#                         test=Constant(value=3),
#                         body=[
#                             Pass()],
#                         orelse=[
#                             Pass()])])])