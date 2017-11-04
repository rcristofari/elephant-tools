import string
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node

####################################################################################
##  matriline_tree() function builds a Newick tree string around an individual    ##
####################################################################################

def matriline_tree(id, db):
    offspring = id
    central_ind = db.get_elephant(id = id)[1]
    #Start upwards to the oldest existing maternal ancestor
    direct_mothers = []
    mother = int
    while mother is not None:
        mother = db.get_mother(id=offspring)
        direct_mothers.append(mother)
        offspring = mother

        if direct_mothers[-1] is None:
            direct_mothers.pop()
    #Find the oldest known female in the line
    if direct_mothers != []:
        oldest_mother = direct_mothers.pop()
    else:
        oldest_mother = id
    #Go back down. The criterion to stop is that no female of generation 'n'
    #has any offspring.

    mothers = [oldest_mother]
    generation_n = [1]
    oldest_mother_num = db.get_elephant(id = oldest_mother)[1]
    newick="('"+str(oldest_mother_num)+"_\u2640')"
    branch_length = [[oldest_mother_num,2]]

    while generation_n.__len__() != 0:
        generation_n = []

        for m in mothers:
            m_num = db.get_elephant(id = m)[1]
            m_birth = db.get_elephant(id = m)[5]
            o = db.get_offsprings(id = m)
            if o is not None:
                taxon = []

                for i in o:
                    generation_n.append(i)
                    info = db.get_elephant(id = i)
                    num = info[1]
                    sex = info[4]
                    birth = info[5]
                    age_of_mother_at_birth = round((birth - m_birth).days / 365.25)
                    branch_length.append([num,age_of_mother_at_birth])
                    if sex == 'F':
                        u = '\u2640'
                    elif sex == 'M':
                        u = '\u2642'
                    else:
                        u = '?'
                    taxon.append(str(num)+'_'+u)

                #Could be refined so that branch length equals age of mother at childbirth
                newick = newick.replace(("'"+str(m_num)+"_\u2640'"), (str(taxon).replace('[','(').replace(']',')').replace(' ','')+str(m_num)+'_\u2640'))
        mothers = generation_n
    newick = newick.replace("'","")+';'

    #Now formatting for the actual plotting in ete3:
    t = Tree(newick , format=8)
    # print(t.get_ascii(attributes=['name'], show_internal=True))
    ts = TreeStyle()
    ts.show_leaf_name = False
    ts.rotation = 90
    ts.show_scale = False
    ts.min_leaf_separation = 50
    def my_layout(node):
         F = TextFace(node.name, tight_text=True)
         F.fsize=6
         F.margin_left=5
         F.margin_right=5
         F.margin_top=0
         F.margin_bottom=15
         F.rotation=-90
         add_face_to_node(F, node, column=0, position="branch-right")
    ts.layout_fn = my_layout
    ts.margin_left=10
    ts.margin_right=10
    ts.margin_top=10
    ts.margin_bottom=10

    i = 0

    for n in t.traverse():
        if i == 0:
            n.delete()
            n.img_style["size"] = 0.
            n.img_style["vt_line_width"] = 1
            n.img_style["hz_line_width"] = 1
            i += 1
        else:
            if str(n.name[:-2]) == str(central_ind):
                n.img_style["size"] = 10
                n.img_style["vt_line_width"] = 1
                n.img_style["hz_line_width"] = 1
                n.img_style["shape"] = "circle"
                n.img_style["fgcolor"] = "red"
                n.dist = int(branch_length[i-1][1])
            else:
                n.img_style["size"] = 0.
                n.img_style["vt_line_width"] = 1
                n.img_style["hz_line_width"] = 1
                n.dist = int(branch_length[i-1][1])
            i += 1
    t.render('tree.png', w=600, units= 'px', tree_style=ts)

    taxa = []
    for n in t.traverse():
        taxa.append(n.name)
    return(t.write(format=1),taxa)

####################################################################################
##  nexus_tree() function writes a Newick tree as a Nexus file                    ##
####################################################################################

def nexus_tree(newick, file):
    lines = []
    lines.append('#NEXUS')
    lines.append('begin taxa;')
    lines.append('\tdimensions ntax='+str(newick[1].__len__()-1)+';')
    lines.append('\ttaxlabels')
    for n in newick[1][1:]:
        lines.append('\t'+n)
    lines.append(';')
    lines.append('end;')
    lines.append('begin trees;')
    lines.append('\ttree TREE1 = [&R]'+newick[0])
    lines.append('end;')

    with open(file,"w") as f:
        for l in lines:
            f.write(str(l)+'\n')
