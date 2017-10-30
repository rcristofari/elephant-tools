from ete3 import Tree, TreeStyle, Tree, TextFace, add_face_to_node
t = Tree( "((a,b)d,c)h;" , format=1) 

ts = TreeStyle()
ts.show_leaf_name = False

def my_layout(node):
        F = TextFace(node.name, tight_text=True)
        add_face_to_node(F, node, column=0, position="branch-right")
ts.layout_fn = my_layout
t.show(tree_style=ts)
