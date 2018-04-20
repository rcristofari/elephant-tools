import string
from ete3 import Tree, TreeStyle, TextFace, add_face_to_node
from datetime import datetime
import difflib as df
from eletools.Utilities import *
from eletools.DataClasses import *
import numpy as np
import math
import re
import csv
import collections
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from matplotlib import pyplot as plt
import pylab

####################################################################################
##  matriline_tree() function builds a Newick tree string around an individual    ##
####################################################################################

def matriline_tree(id, db, as_list=False):
    offspring = id
    e = db.get_elephant(id=id)
    if e:
        central_ind = e[1]
    else:
        return(None)

    # Start upwards to the oldest existing maternal ancestor
    direct_mothers = []
    mother = str

    while mother is not None:
        mother = db.get_mother(id=offspring)
        direct_mothers.append(mother)
        offspring = mother

        if direct_mothers[-1] is None:
            direct_mothers.pop()

    # Find the oldest known female in the line
    if direct_mothers != []:
        oldest_mother = direct_mothers.pop()
    else:
        oldest_mother = id

    # Go back down. The criterion to stop is that no female of generation 'n' has any offspring.
    mothers = [oldest_mother]
    generation_n = [1]
    oldest_mother_num = db.get_elephant(id=oldest_mother)[1]
    newick = "('" + str(oldest_mother_num) + "_\u2640')"
    branch_length = [[oldest_mother_num, 2]]

    ############################
    # Exporation in list form
    if as_list is True:
        # at each generation, we will make two objects: an unstructured list giving all individuals,
        # and a structured list keeping track of paths

        # We make a first pass to create the unstructured list:
        tree_list_unstructured = [oldest_mother_num]

        g = 0
        generation_n = [0]
        while generation_n.__len__() != 0:
            generation_n = []
            # these_off = None

            if type(tree_list_unstructured[g]) is list:
                for i in tree_list_unstructured[g]:
                    these_off = db.get_offsprings(num=i)
                    if these_off:
                        for o in these_off:
                            generation_n.append(o)

            else:
                these_off = db.get_offsprings(num=tree_list_unstructured[g])
                if these_off:
                    for o in these_off:
                        generation_n.append(o)
            g += 1
            tree_list_unstructured.append(generation_n)

        if tree_list_unstructured[-1] == []:
            tree_list_unstructured.pop()

        # Now the genealogy is explored, we go through it and structure it:
        tree_list_structured = [oldest_mother_num]

        for generation in tree_list_unstructured:
            next_generation = []
            these_off = None

            if type(generation) is not list:
                these_off = db.get_offsprings(num=generation)
                if these_off:
                    next_generation = these_off
                else:
                    next_generation = []

            elif type(generation) is list and generation != []:
                for g in generation:
                    these_off = db.get_offsprings(num=g)
                    if these_off:
                        next_generation.append(these_off)
                    else:
                        next_generation.append([])

            if not all(x==[] for x in next_generation):
                tree_list_structured.append(next_generation)

        return([tree_list_structured, tree_list_unstructured])


    ############################
    # Exploration in Newick form
    while generation_n.__len__() != 0:
        generation_n = []

        for m in mothers:
            m_num = db.get_elephant(id=m)[1]
            m_birth = db.get_elephant(id=m)[5]
            o = db.get_offsprings(id=m)

            if o is not None:
                taxon = []

                for i in o:
                    generation_n.append(i)
                    info = db.get_elephant(id=i)
                    num = info[1]
                    if not num:
                        num = info[3]
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

                newick = newick.replace(("'" + str(m_num) + "_\u2640'"),
                                        (str(taxon).replace('[', '(').replace(']', ')').replace(' ', '')
                                         + str(m_num) + '_\u2640'))
        mothers = generation_n
    newick = newick.replace("'", "")+';'

    # Now formatting for the actual plotting in ete3:
    t = Tree(newick, format=8)
    # print(t.get_ascii(attributes=['name'], show_internal=True))
    ts = TreeStyle()
    ts.show_leaf_name = False
    ts.rotation = 90
    ts.show_scale = False
    ts.min_leaf_separation = 50

    def my_layout(node):
        F = TextFace(node.name, tight_text=True)
        F.fsize = 6
        F.margin_left = 5
        F.margin_right = 5
        F.margin_top = 0
        F.margin_bottom = 15
        F.rotation = -90
        add_face_to_node(F, node, column=0, position="branch-right")
    ts.layout_fn = my_layout
    ts.margin_left = 10
    ts.margin_right = 10
    ts.margin_top = 10
    ts.margin_bottom = 10

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

    return(t.write(format=1), taxa)

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
##  relatedness_matrix() builds an empirical relatedness matrix from a list       ##
####################################################################################
#
def relatedness_matrix(numlist, db, bifurcating=True):  # Need to extend it to incude known paternal links

    # bifurcating: here, trees are matrilines, so we consider only one path through genealogy
    # We use the definition of Wright 1922 (sum of the path lengths, both ways)

    # We create a square matrix of the same order as the number of individuals in the list

    nInd = numlist.__len__()
    tree_matrix = np.zeros(shape=(nInd, nInd))

    # For each individual in the list, we make a direct matriline vector (same as matriline_tree first step)
    matrilines = []
    for id in numlist:
        offspring = id
        direct_mothers = [str(offspring)]
        mother = []

        while mother is not None:

            if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', str(offspring)):  # then it's a calf
                mother = db.get_mother(calf_num=offspring)
            else:
                mother = db.get_mother(num=offspring)

            direct_mothers.append(str(mother))
            offspring = mother

            if direct_mothers[-1] is None or direct_mothers[-1] == '' or direct_mothers[-1] == 'None':
                direct_mothers.pop()

        matrilines.append(direct_mothers)


    # Now, the matriline list contains direct lines for each elephant in list. We can calculate pairwise coefficients.
    for x, ind_1 in enumerate(matrilines):
        for y, ind_2 in enumerate(matrilines):
            i = list(ind_1)
            j = list(ind_2)

            if i == j:
                coef = 1  # This populates the diagonal and eventual redundancies in the list
            else:
                # We use the fact that if any ancestor is shared, the oldest known common ancestor is also shared
                if i[-1] != j[-1]:  # No contact between the lines
                    coef = 0
                else:
                    while i.__len__() > 0 and j.__len__() > 0 and i[-1] == j[-1]:
                        i.pop()
                        j.pop()
                    # This leaves us with only the non-shared nodes/tips between the lineages (excluding the MRCA)
                    coef = math.pow(.5, ((i + j).__len__()))

            tree_matrix[x, y] = coef
            tree_matrix[y, x] = coef

    return(tree_matrix)

####################################################################################
## censor_elephant() function builds a Newick tree string around an individual    ##
####################################################################################
# Database id of the elephant, yearly survival probability curve, probability cutoff
# Could be extended to include more cues

def censor_elephant(db, id, survival=None, cutoff=0.05):
    key = 0 # this means that we have no positive info so far about this elephant being dead
    eleph = None
    sex = None
    cw = None
    birth = None
    death = None

    try:
        eleph = db.get_elephant(id=id)
    except:
        print("Impossible to connect to the database.")

    if eleph is not None:
        id = eleph[0]
        sex = eleph[4]
        birth = eleph[5]
        cw = eleph[6]

    # Loading the survival curves and choosing the right model:
    Sx = []
    categories = ['SxFC','SxMC','SxFW','SxMW']
    descript = ['captive female','captive male','wild female','wild male']
    with open(survival) as sxfile:
        sx = csv.reader(sxfile, delimiter = ',')
        for s in sx:
            Sx.append(list(s))
    for i,s in enumerate(Sx):
        if s[0] == categories[i]:
            s.pop(0)
            for j,x in enumerate(s):
                s[j] = float(x)
    SxFC = Sx[0]
    SxMC = Sx[1]
    SxFW = Sx[2]
    SxMW = Sx[3]

    if sex == 'F' and (cw == 'captive'):
        survival = SxFC
        descript = descript[0]
    elif sex == 'F' and (cw == 'wild'):
        survival = SxFW
        descript = descript[2]
    elif sex == 'F' and (cw == 'UKN'):
        survival = SxFC # Need a special curve here
        descript = descript[0]
    elif sex == 'M' and (cw == 'captive'):
        survival = SxMC
        descript = descript[1]
    elif sex == 'M' and (cw == 'wild'):
        survival = SxMW
        descript = descript[3]
    elif sex == 'M' and (cw == 'UKN'):
        survival = SxFC # Need a special curve here
        descript = descript[1]
    else:
        survival = SxMC # Need a "common" Sx model here instead
        descript = descript[1]

    # Do we know a death date for this elephant ?
    death_type = db.get_date_of_death(id=id, with_type=True)
    if death_type is not None:
        key = 1
        death = death_type[0]
        dtype = death_type[1]

    else:
        # Start by getting the last date we have data about that elephant
        by_event = None
        by_breeding = None
        by_event_type = db.get_last_alive(id, with_type=True)
        by_event = by_event_type[0]
        etype = by_event_type[1]
        by_breeding = db.get_last_breeding(id)

        if by_event and by_breeding:
            if by_event < by_breeding:
                last_seen = by_breeding
                etype = 'breeding'
            else:
                last_seen = by_event
        elif by_event:
            last_seen = by_event
        elif by_breeding:
            last_seen = by_breeding
            etype = 'breeding'
        else:
            last_seen = birth
            etype = 'birth'

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
        out = (key, birth, last_seen, add_years(birth, i), i, p_alive_now, etype, descript)
    elif key == 1:
        out = (key, birth, death, dtype, descript)

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
    mother = None

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

        if mother_num is not None:

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

        else:
            total_flag = total_flag + 64
            message.append("No mother declared, this calf will be anonymous")

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

            ##################################################################################
            # In this case we need to check if a similar calf already exists:
            duplicates = None
            if mother_num is not None:
                duplicates = db.get_all_offsprings(num=mother_num, candidate=calf, limit_age=limit_age)
            if duplicates:
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

        if all(x not in [0, 6] for x in break_flag(total_flag)):  # Check again that no error has arisen in the meantime

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
        if mother:
            out = [wcalf, wmother, wrelationship, message, duplicates, total_flag, mother.in_db, mother.in_input]
        else:
            out = [wcalf, wmother, wrelationship, message, duplicates, total_flag, 'No known mother', 'No known mother']

        return(out)

####################################################################################
## generate_calf_names() generate calf names for adults that need it              ##
####################################################################################

def regularise_calf_names(db, true_twin_list=None):
    # true_twin_list is a list with three columns: mother number and twin birth
    # dates, and gender, which will be 'MM', 'FF', or 'FM'/'MF'

    # List to be populated with the sql update queries
    operations = []
    operations.append(db.stamp())

    # Extract the list and data for the elephants which do not have a calf number
    anonymous_calves = db.get_anonymous_calves(anonymous=True)
    named_calves = db.get_anonymous_calves(anonymous=False)

    # Get the ID of unnumbered calves, and make up their new calf_num
    new_calf_names = []
    new_ids = []
    for a in anonymous_calves:
        new_calf_names.append(str(a[1].year)+'B'+str(a[2]))
        new_ids.append(a[0])

    # Get the ID and calf_num of already numbered calves
    known_calf_names = []
    known_ids = []
    for a in named_calves:
        known_calf_names.append(a[4])
        known_ids.append(a[0])

    all_calf_names = known_calf_names + new_calf_names
    all_ids = known_ids + new_ids

    duplicate_calves = [item for item, count in collections.Counter(all_calf_names).items() if count > 1]
    duplicate_calves.sort()

    # We make a list of the indices of the duplicate calves in the full list (each element is a pair of indices):
    duplicate_index = []
    calves_array = np.array(all_calf_names)
    for d in duplicate_calves:
        duplicate_index.append(list(np.where(calves_array == d)[0]))


    # We can already generate sql updates for all non-duplicate calves.
    for i, n in enumerate(new_calf_names):
        if n not in duplicate_calves:
            commits = db.get_elephant(id=new_ids[i])[11]
            operations.append(db.update_elephant(calf_num=n, id=new_ids[i], commits=commits))

    # Some talking:
    print("The following calves are either twins or duplicates:")
    for d in duplicate_calves:
        print(d)


    # Now we proceed to verifying the authenticity of these double calves.
    twin_mothers, twin_births, twin_sex, twin_names = [], [], [], []

    # If we have a validated list, we can check if these calves are authentic twins
    if true_twin_list is not None:
        with open(true_twin_list) as twinfile:
            twinread = csv.reader(twinfile, delimiter=',', quotechar="'")
            next(twinread)
            for t in twinread:
                twin_mothers.append(t[0])
                twin_births.append(datetime.strptime(format_date(t[1]), '%Y-%m-%d'))
                twin_sex.append(t[2])
                twin_names.append(format_date(t[1])[0:4] + 'B' + t[0])

    # This should never happen, but it would be a bad thing indeed if it did.
    if duplicate_calves.__len__() != duplicate_index.__len__():
        print("There is some unexplained error in the list lengths - get back to work.")
        return(None)

    # We make one pass to identify the duplicate calves that are in our trusted list:
    untrusted_twins = []
    twin_names_array = np.array(twin_names)
    for i, d in enumerate(duplicate_calves):
        if d in twin_names:
            d_index = int(np.where(twin_names_array == d)[0])
            twin_indices = duplicate_index[i]
            twin_1_newname = str(twin_births[d_index].year) + 'A' + str(twin_mothers[d_index])
            twin_2_newname = str(twin_births[d_index].year) + 'B' + str(twin_mothers[d_index])
            twin_1_commits = db.get_elephant(id=all_ids[twin_indices[0]])[11]
            twin_2_commits = db.get_elephant(id=all_ids[twin_indices[1]])[11]
            operations.append(db.update_elephant(calf_num=twin_1_newname, id=all_ids[twin_indices[0]], commits=twin_1_commits))
            operations.append(db.update_elephant(calf_num=twin_2_newname, id=all_ids[twin_indices[1]], commits=twin_2_commits))

        else:
            untrusted_twins.append([d, duplicate_index[i]])

    # We make a second pass to identify the authentic twins we did not know about already:
    # the fact that they are not in the dup list doesn't mean we don't know them: they can also already have regularly
    # differentiated names
    missing_twins = []
    for i, d in enumerate(twin_names):
        reject = False
        if d not in duplicate_calves:
            missing_twins.append(d)
            # Do we already know about one (or two) of the twins?
            twin_1, twin_2 = None, None
            twin_1 = db.get_elephant(calf_num=str(twin_births[i].year) + 'A' + str(twin_mothers[i]))
            twin_2 = db.get_elephant(calf_num=str(twin_births[i].year) + 'B' + str(twin_mothers[i]))
            if twin_1 and twin_2:
                print("Already reguarised in the DB")
            elif twin_2 and not twin_1:
                # Determine the correct sex:
                pair_sex = twin_sex[i]
                twin_2_sex = twin_2[4]
                if pair_sex == 'MM' and twin_2_sex in ('M', 'UKN'):
                    twin_1_sex = 'M'
                elif pair_sex == 'FF' and twin_2_sex in ('F', 'UKN'):
                    twin_1_sex = 'F'
                elif pair_sex in ('MF', 'FM') and twin_2_sex == 'M':
                    twin_1_sex = 'F'
                elif pair_sex in ('MF', 'FM') and twin_2_sex == 'F':
                    twin_1_sex = 'M'
                elif pair_sex in ('MF', 'FM') and twin_2_sex == 'UKN':
                    twin_1_sex = 'UKN'
                else:
                    print("There seems to be incompatibilities in sex determination between list and database")
                    untrusted_twins.append([d, [None, None]])
                    reject = True

                if not reject:
                    operations.append(db.insert_elephant(num=None, name=None, calf_num=(str(twin_births[i].year) + 'A' + str(twin_mothers[i])),
                                                     sex=twin_1_sex, birth=twin_2[5], cw=twin_2[6], caught=twin_2[7],
                                                     camp=twin_2[8], alive=None, research=None))


    return(operations, untrusted_twins)

####################################################################################
## create_lifeline() generates the core plot for the lifeline plot class          ##
####################################################################################

def create_lifeline(db, id=None, num=None, logs=True, taming=True, breeding=True, censoring=True, events=True, measures=True):
    # Start by retrieving the elephant data:
    elephant = None
    if id is not None:
        elephant = db.get_elephant(id = id)
    elif num is not None:
        elephant = db.get_elephant(num = num)
        id = elephant[0]

    if not elephant:
        print("This id does not correspond to any elephant in the database")
    else:

        birth = elephant[5]
        censor_list = censor_elephant(db, id, survival='./__resources/Sx_curves', cutoff=0.05)
        if censor_list[0] == 0: # elephant not known dead yet
            last_seen = censor_list[2]
            likely_death = censor_list[3]
        else: # elephant known dead
            death = censor_list[2]

        ########################################################################
        # Determine the type of plot:
        plttype = None
        # Probably dead
        if censor_list[0] == 0 and (datetime.now().date() - likely_death).days >= 0:
            linelim = [birth, likely_death]
            etype = censor_list[6]
            plttype = 0
        # Probably alive
        elif censor_list[0] == 0 and (datetime.now().date() - likely_death).days < 0:
            linelim = [birth, datetime.now().date()]
            plttype = 1
        # Dead
        else:
            linelim = [birth, death]
            dtype = censor_list[3]
            plttype = 2

        ########################################################################
        # We can now initiate the plot:
        if plttype in [1,2]:
            plt.plot_date(np.array(linelim), np.array([0,0]), marker = 'x', linestyle = '-', color = 'k')
        else:
            plt.plot_date(np.array([birth, last_seen]), np.array([0,0]), marker = 'x', linestyle = '-', color = 'k')
            plt.plot_date(np.array([last_seen, likely_death]), np.array([0,0]), marker = 'x', linestyle = ':', color = 'k')
        plt.grid(b=True, which='major', color='k', linestyle='-', alpha=0.5)
        plt.ylim(ymax = 2, ymin = -2)

        ########################################################################
        # Adding censoring landmarks:
        if censoring is True:
            plt.annotate(datetime.strftime(birth, '%Y-%m-%d'), xy=(birth, 0.15), verticalalignment='bottom', rotation=90, ha='center', fontsize=8)
            if plttype == 1:
                plt.annotate(('aged ' + str(round((datetime.now().date() - birth).days / 365.25))), xy=(datetime.now().date(), 0.15), verticalalignment='bottom', rotation=90, ha='center', fontsize=8)
            elif plttype == 2:
                plt.annotate(datetime.strftime(death, '%Y-%m-%d') + ' (aged ' + str(round((death - birth).days / 365.25)) + ', ' + dtype.replace('_', ' ') + ')', xy=(death, 0.15), verticalalignment='bottom', rotation=90, ha='center', fontsize=8)
            elif plttype == 0:
                plt.annotate(datetime.strftime(likely_death, '%Y-%m-%d') + ' (aged ' + str(round((likely_death - birth).days / 365.25)) + ')', xy=(likely_death, 0.15), verticalalignment='bottom', rotation=90, ha='center', fontsize=8)
                plt.annotate(datetime.strftime(last_seen, '%Y-%m-%d') + ' (' + etype + ')', xy=(last_seen, 0.15), verticalalignment='bottom', rotation=90, ha='center', fontsize=8)

        ########################################################################
        # Adding calves:
        if breeding is True:
            offspring_id = db.get_offsprings(id=id)
            if offspring_id:

                offsprings = []
                for o in offspring_id:
                    offsprings.append(db.get_elephant(id = o))

                for i, x in enumerate(offsprings):
                    plt.plot_date(np.array([x[5], x[5]]), np.array([-0.75,0]), marker=None, linestyle = '--', color = 'r')
                    #plt.axvline(x=x[5], ymin=0.35, ymax=0.5, linestyle = '--', color = 'r')
                    if x[1] is not None:
                        plt.annotate(str(x[1]) + ' (' + str(x[4]) + ')', xy = (x[5], -0.85), verticalalignment='top', rotation=90, ha='center', backgroundcolor='w', fontsize=8)
                    else:
                        plt.annotate(str(x[3]) + ' (' + str(x[4]) + ')', xy = (x[5], -0.85), verticalalignment='top', rotation=90, ha='center', fontsize=8)

        ########################################################################
        # Adding the logbook periods:
        if logs is True:
            logbooks = db.get_logbook_coordinates(id=id)
            if logbooks:
                for l in logbooks:
                    plt.plot_date(np.array(l[2:4]), np.array([0,0]), marker = '', linestyle = '-', color = 'g', linewidth=10, alpha=0.5, solid_capstyle='butt')

        ########################################################################
        # Adding measurement events:
        if measures is True:
            measure_dates = db.get_measure_events(id=id)
            print(measure_dates)
            if measure_dates:
                for m in measure_dates:
                    # Plot on 6 levels depending on the measure type (morpho, physio, immuno, parasito, behav, genet)
                    if m[0]=='morphology':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.35]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('M', xy = (m[1], 0.36), verticalalignment='bottom', ha='center', fontsize=8)
                    elif m[0]=='physiology':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.45]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('P', xy = (m[1], 0.46), verticalalignment='bottom', ha='center', fontsize=8)
                    elif m[0]=='immunology':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.55]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('I', xy = (m[1], 0.56), verticalalignment='bottom', ha='center', fontsize=8)
                    elif m[0]=='parasitology':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.65]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('Pa', xy = (m[1], 0.66), verticalalignment='bottom', ha='center', fontsize=8)
                    elif m[0]=='behaviour':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.75]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('B', xy = (m[1], 0.76), verticalalignment='bottom', ha='center', fontsize=8)
                    elif m[0]=='genomics':
                        plt.plot_date(np.array([m[1], m[1]]), np.array([0,0.85]), marker=None, linestyle = '-', color = "#E08E45", linewidth=.5)
                        plt.annotate('G', xy = (m[1], 0.86), verticalalignment='bottom', ha='center', fontsize=8)

        ########################################################################
        # Adding the taming period and the events (TO DO)
        #
        # ...




        ########################################################################
        # Re-plotting the life line on top
        if plttype in [1,2]:
            plt.plot_date(np.array(linelim), np.array([0,0]), marker = 'x', linestyle = '-', color = 'k')
        else:
            plt.plot_date(np.array([birth, last_seen]), np.array([0,0]), marker = 'x', linestyle = '-', color = 'k')
            plt.plot_date(np.array([last_seen, likely_death]), np.array([0,0]), marker = 'x', linestyle = ':', color = 'k')

        ########################################################################
        # Final details:
        w = pylab.gcf()
        if elephant[1] is not None:
            w.canvas.set_window_title('Lifeline of ' + str(elephant[2]) + ' (' + str(elephant[1]) + ')')
        else:
            w.canvas.set_window_title('Lifeline of ' + str(elephant[2]) + ' (' + str(elephant[3]) + ')')

        w.set_facecolor("#E08E45")
        plt.axes().get_yaxis().set_visible(False)
        plt.show()

