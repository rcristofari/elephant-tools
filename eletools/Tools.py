import string
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from datetime import datetime
from eletools.Utilities import *

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
                n.img_style["fgcolor"] = "#A30B37"
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

####################################################################################
## censor_elephant() function builds a Newick tree string around an individual    ##
####################################################################################
# Database id of the elephant, yearly survival probability curve, probability cutoff
# Could be extended to include more cues

def censor_elephant(db, id, survival=None, cutoff=0.05):

    # Get the birth date
    try:
        birth = db.get_elephant(id=id)[5]
    except:
        print("Impossible to find that elephant in the database")

    # Start by getting the last date we have data about that elephant
    by_event = None
    by_breeding = None

    by_event = db.get_last_alive(id)
    by_breeding = db.get_last_breeding(id)

    if by_event and by_breeding:
        if by_event < by_breeding:
            last_seen = by_breeding
        else:
            last_seen = by_event
    elif by_event:
        last_seen = by_event
    elif by_breeding:
        last_seen = by_breeding
    else:
        last_seen = birth

    ## THIS IS IN THE "SUM" CASE    # If we provide no survival curve, we assume a completely unrealistic flat probability
    # suddendly truncated at 100 years old. With a cutoff of 5%, this makes elephants live to 95.
    # if survival is None:
    #     survival = []
    #     for s in range(100):
    #         survival.append(1/100)
    #     survival.append(0)
    ##

    # identify the maximum age in the curve (when survival falls to 0)
    for i,s in enumerate(survival):
        if s == 0:
            break
    max_age = i

    age_last_seen = int((last_seen - birth).days // 365.25)

    ## THIS IS IN THE "SUM" CASE
    # p_forward = survival[age_last_seen+1:] # starting the next year (we assume you survive the year you're already engaged in)
    # p_sum = sum(p_forward)
    # scaling_given_seen = 1 / p_sum
    # p_given_seen = []
    # for p in p_forward:
    #     p_given_seen.append(p * scaling_given_seen)
    # p_given_seen is the probability of dying each year starting from the last_seen date.
    # i = 0
    # while sum(p_given_seen[i:]) > cutoff: # if i stays at zero, you should in fact die this year. Sorry.
    #     i += 1
    # now, i is the number of years you should survive from last_seen onwards.
    ##

    ## IN THE Sx CASE:
    p, i = 1, age_last_seen # probability of being alive when last seen is 1
    while p > cutoff:
        p *= survival[i]
        i += 1
    # print(i,p)
        # now, i is the age you should hope to reach

    age_now = int((datetime.now().date() - birth).days // 365.25)
    if age_now >= max_age:
        p_alive_now = 0

    else:
        p_alive_now = 1
        for a in range(age_last_seen, age_now+1):
            p_alive_now *= survival[a]

        ## THIS IS IN THE "SUM" CASE
        # p_alive_now is the probability that the elephant is still alive at the time of request:
        # years_since_last_seen = int((datetime.now().date() - last_seen).days // 365.25)
        # by definition, if the difference is zero, probability is 1 (full sum of p_forward)
        # p_alive_now = round(sum(p_forward[years_since_last_seen:]),2)
        ##

    print("\nBirth date: ", birth.strftime('%Y-%m-%d'),
        "\nLast seen on:", last_seen.strftime('%Y-%m-%d'),
        "\nExpected death year:", add_years(birth, i).strftime('%Y'), "(at", i, "years)"
        "\nProbability that it is alive today:", round(p_alive_now,3))

    out = ("\nBirth date: "+birth.strftime('%Y-%m-%d')+
            "\nLast seen on: "+last_seen.strftime('%Y-%m-%d')+
            "\nExpected final bow: "+add_years(birth, i).strftime('%Y')+" (at "+str(i)+" years)"
            "\nProbability that it is alive today: "+str(round(p_alive_now,3)))
    return(out)
