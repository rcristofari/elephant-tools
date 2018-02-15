import string
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from datetime import datetime
import difflib as df
from eletools.Utilities import *
from eletools.DataClasses import *

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
    key = 0 # this means that we have no positive info so far about this elephant being dead
    death = None

    # Get the birth date
    try:
        birth = db.get_elephant(id=id)[5]
    except:
        print("Impossible to find that elephant in the database")

    # Do we know a death date for this elephant ?
    death = db.get_date_of_death(id = id)
    if death is not None:
        key = 1

    else:
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

        # identify the maximum age in the curve (when survival falls to 0)
        for i,s in enumerate(survival):
            if s == 0:
                break
        max_age = i
        age_last_seen = int((last_seen - birth).days // 365.25)

        p, i = 1, age_last_seen # probability of being alive when last seen is 1
        while p > cutoff:
            p *= survival[i]
            i += 1
            # now, i is the age you should hope to reach

        age_now = int((datetime.now().date() - birth).days // 365.25)
        if age_now >= max_age:
            p_alive_now = 0
        else:
            p_alive_now = 1
            for a in range(age_last_seen, age_now+1):
                p_alive_now *= survival[a]

        # print("\nBirth date: ", birth.strftime('%Y-%m-%d'),
        #     "\nLast seen on:", last_seen.strftime('%Y-%m-%d'),
        #     "\nExpected death year:", add_years(birth, i).strftime('%Y'), "(at", i, "years)"
        #     "\nProbability that it is alive today:", round(p_alive_now,3))

    if key == 0:
        out = (key, birth, last_seen, add_years(birth, i), i, p_alive_now)
    elif key == 1:
        out = (key, birth, death)

    return(out)


####################################################################################
## fuzzy_match_measure() checks whether a similar measure exitst                  ##
####################################################################################

def fuzzy_match_measure(db, type, cutoff=0.6):
    all_types = db.get_measure_list()

    matches = []
    for t in all_types:
        d = df.SequenceMatcher(None, type, t[1])
        if d.ratio() >= cutoff:
            matches.append(t)
    return(matches)

####################################################################################
## analyse_calf() examines a composite row defining a calf                        ##
####################################################################################


def analyse_calf(calf_num, birth, mother_num, db, calf_name=None, sex=None, cw=None, caught=None, camp=None, alive=None,
                 research=None, mother_name=None, solved=False, flag=0, limit_age=28):

    total_flag = flag
    wmother = None
    wcalf = None
    wrelationship = None
    message = []
    duplicates = None

    # Local flag system: starts by default at 0, or at 1 if the row is excluded (in which case we break)
    # Add 1 if there is a prohibitive error
    # Add 2 if the mother doesn't pose a problem
    # Add 4 if the calf doesn't pose a problem
    # Add 8 if the relationship doesn't pose a problem
    # Add 16 if there is nothing to be added to the database
    # Add 32 if the pedigree itself is already known
    # To be written out, the flag must contain 2, 4, and 8
    # Details of the problems are contained in the respective flags

    if 0 not in break_flag(total_flag):

        ##################################################################################
        # Identify the mother
        # Either she doesn't exist (2^1), or she exists with a different name (2^2), or she exists as-is (2^3).

        mother = elephant(num=mother_num, name=mother_name, solved=solved, flag=flag)
        mother.source(db)
        mother.check()
        wmother = mother.write(db)

        # If the mother is known (eventually under an alias name)
        if 2 in break_flag(wmother[10]):
            total_flag = total_flag + 2
            message.append("The mother is known under a different name, the database will be updated")
        elif 3 in break_flag(wmother[10]):
            total_flag = total_flag + 2
            message.append("The mother is known, nothing to change")
        else:
            total_flag = total_flag + 1
            message.append("This mother is not valid:")
            if type(wmother[11]) is list:
                message = message + wmother[11]
            elif type(wmother[11]) is str:
                message.append(wmother[11])

        ##################################################################################
        # Identify the calf

        calf = elephant(name=calf_name, calf_num=calf_num, sex=sex, birth=birth, cw=cw, caught=caught, camp=camp,
                        alive=alive, research=research, flag=flag, solved=solved)
        calf.source(db)
        calf.check()
        wcalf = calf.write(db)

        if 1 in break_flag(wcalf[10]):
            total_flag = total_flag + 4
            message.append("This calf is unknown.")

            # In this case we need to check if a similar calf already exists:

            duplicates = db.get_all_offsprings(num=mother_num, candidate=calf, limit_age=limit_age)
            if duplicates is not None:
                total_flag = total_flag + 1
                dup_message = "This mother already has a calf around that age in the database("
                for d in duplicates:
                    dup_message = dup_message + d[1] + ' '
                dup_message = dup_message.strip(' ') + ')'
                message.append(dup_message)

        elif 2 in break_flag(wcalf[10]):
            message.append("This calf will be updated.")
            total_flag = total_flag + 4

        elif 3 in break_flag(wcalf[10]):  # The calf is already known
            message.append("This calf is already known")
            if 3 in break_flag(wmother[10]):
                total_flag = total_flag + 16  # Means that nothing will be done here

        else:
            message.append("This calf is not valid:")
            if type(wcalf[11]) is list:
                message = message + wcalf[11]
            elif type(wcalf[11]) is str:
                message.append(wcalf[11])

        if 0 not in break_flag(total_flag):  # Check again that no error has arisen in the meantime

            ##################################################################################
            # Extract the relationship
            relationship = None
            wrelationship = None

            if all(x in break_flag(total_flag) for x in [1, 2]):

                # Distinguish the case where the calf exists in the DB (as-is, or to be updated)
                # and the case where it is not present yet

                # Calf is unknown yet, shall be written in
                if 1 in break_flag(wcalf[10]):
                    relationship = pedigree(eleph_1=mother_num, eleph_2=calf, rel='mother', eleph_2_is_calf=True,
                                            flag=flag)

                # Calf exists but needs to be updated
                elif 2 in break_flag(wcalf[10]):
                    relationship = pedigree(eleph_1=mother_num, eleph_2=calf_num, rel='mother',
                                            eleph_2_is_calf=True, flag=flag)


                if relationship is not None:
                    relationship.source(db)
                    relationship.check()
                    wrelationship = relationship.write(db)

                    if any(x in [1, 2] for x in break_flag(wrelationship[4])):
                        total_flag = total_flag + 8
                        message.append("The relationship is valid: the calf can be registered")
                    elif 3 in break_flag(wcalf[10]) and 3 in break_flag(wrelationship[4]):
                        message.append("Nothing to do here, the database is already up to date")
                        total_flag = total_flag + 32
                    elif 3 in break_flag(wcalf[10]) and 3 not in break_flag(wrelationship[4]):
                        message.append("The calf is known, but you should still register the pedigree information.")
                    elif all(x not in [1, 2, 3] for x in break_flag(wrelationship[4])):
                        message.append("The relationship is not valid:")
                        if type(wrelationship[5]) is list:
                            message = message + wrelationship[5]
                        elif type(wrelationship[5]) is str:
                            message.append(wrelationship[5])
                    else:
                        message.append("This is an unhandled case, look into it.")

        ##################################################################################
        # Parse out the results
        out = [wcalf, wmother, wrelationship, message, duplicates, total_flag]
        return(out)