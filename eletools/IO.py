from datetime import datetime
import string
import random
import numpy as np
import re
import os
import csv
from eletools.Utilities import *

####################################################################################
##  read_elephants() READ ELEPHANTS DEFINTION FILE                                 ##
####################################################################################

# A model elephant file is made up of 10 fields:
# num, name, calf_num, sex, birth, cw, caught, camp, alive, research
# field names irrelevant, but order necessary

def read_elephants(elefile, sep=';', is_file=True):
    # Prepare empty list for column-wise parsing
    num, name, calf_num, sex, birth, cw, caught, camp, alive, research = [], [], [], [], [], [], [], [], [], []

    if is_file == True:
    ########## Store the header in a list, and then each variable in its own column
        with open(elefile) as elefile:
            eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
            fields = next(eleread)[0:10]
            for row in eleread:
                num.append(row[0])
                name.append(row[1])
                calf_num.append(row[2])
                sex.append(row[3])
                birth.append(row[4])
                cw.append(row[5])
                caught.append(row[6])
                camp.append(row[7])
                alive.append(row[8])
                research.append(row[9])
    elif is_file == False:
        fields = ['num', 'name', 'calf_num', 'sex', 'birth', 'cw', 'caught', 'camp', 'alive', 'research']
        for row in elefile:
            num.append(row[0])
            name.append(row[1])
            calf_num.append(row[2])
            sex.append(row[3])
            birth.append(row[4])
            cw.append(row[5])
            caught.append(row[6])
            camp.append(row[7])
            alive.append(row[8])
            research.append(row[9])
    ########## Format to lowercase Name and Camp
    lcname, lccamp = [], []
    for n in name:
        lcname.append(string.capwords(n))
    for c in camp:
        lccamp.append(string.capwords(c))
    name, camp = lcname, lccamp
    del lcname, lccamp

    ########## Try to guess sex, origin, alive and research
    sx, cwx, ax, rx = [], [], [], []
    for x in sex:
        if x.casefold().strip() in ('male','m','males'):
            sx.append('M')
        elif x.casefold().strip() in ('female','f','females'):
            sx.append('F')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            sx.append('UKN')
        else:
            sx.append(x)
    for x in cw:
        if x.casefold().strip() in ('c','captive'):
            cwx.append('captive')
        elif x.casefold().strip() in ('w','wild'):
            cwx.append('wild')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            cwx.append('UKN')
        else:
            cwx.append(x)
    for x in alive:
        if x.casefold().strip() in ('y','yes','alive'):
            ax.append('Y')
        elif x.casefold().strip() in ('n','no','dead'):
            ax.append('N')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            ax.append('UKN')
        else:
            ax.append(x)
    for x in research:
        if x.casefold().strip() in ('y','yes'):
            rx.append('Y')
        elif x.casefold().strip() in ('n','no','','none','na','null','unknown','ukn','n/a'):
            rx.append('N')
        else:
            rx.append(x)
    sex, cw, alive, research = sx, cwx, ax, rx
    del sx, cwx, ax, rx

    ########## Reformat as rows
    rows=[]
    for i,r in enumerate(num):
        row=[num[i],name[i],calf_num[i],sex[i],birth[i],cw[i],caught[i],camp[i],alive[i],research[i]]
        rows.append(row)

    ########## Check data types row by row
    valid, remarks, rejected, issues = [], [], [], []

    for i,row in enumerate(rows):
        reject = 0
        warnings = []

        ########## Sort out missing values
        for j,x in enumerate(row):
            if x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
                row[j] = None
            else:
                pass

    ########## num
        if re.search(r"^[0-9a-zA-Z]+$", str(row[0])):
            pass
        elif row[0] is None and row[2] is not None:
            warnings.append("Missing number at line " + str(i+1))
        elif row[0] is None and row[2] is None:
            warnings.append("Missing number at line " + str(i+1) + ", and no calf number. You need at least one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(row[0]) + " at line " + str(i+1))
            reject = 1

    ########## name
        if re.search(r"^[a-zA-Z ]+$", str(row[1])):
            pass
        elif row[1] is None:
            warnings.append("Missing name at line " + str(i+1))
        else:
            warnings.append("Format problem with name: " + str(row[1]) + " at line " + str(i+1))
            reject = 1

    ########## calf_num
        print(row[2], type(row[2]))
        if re.search(r"^[a-zA-Z0-9]+$",row[2]):
            pass
        elif row[2] is None and row[0] is None:
            warnings.append("Missing calf number at line " + str(i+1) + ". You need at least one number.")
            reject = 1
        elif row[2] is None and row[0] is not None:
            pass
        else:
            warnings.append("Format problem with calf number: " + str(row[2]) + " at line " + str(i+1))
            reject = 1

    ########## sex
        if row[3] in ('M','F','UKN'):
            pass
        elif row[3] == None:
            warnings.append("Missing sex at line " + str(i+1))
        else:
            warnings.append("Sex must be M, F or UKN at line " + str(i+1) +" (here: " + str(row[3]) + ")")
            reject = 1

    ########## birth
        date = format_date(str(row[4]))
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            try:
                row[4] = date
            except ValueError:
                reject = 1
                warnings.append("Invalid date " + str(date) + " at line " + str(i+1))
        elif date is None:
            warnings.append("Missing birth date at line " + str(i+1))
        else:
            warnings.append("Format problem with birth date: " + str(date) + " at line " + str(i+1))
            reject = 1

    ########## CW
        if row[5] in ('captive','wild','UKN'):
            pass
        elif row[5] is None:
            warnings.append("Missing origin at line " + str(i+1))
        else:
            warnings.append("Origin must be captive, wild or UKN at line " + str(i+1) +" (here: " + str(row[5]) + ")")
            reject = 1

    ########## caught
        if re.search(r"^[0-9]+$", str(row[6])):
            pass
        elif row[6] is None and cw[i] == 'wild':
            warnings.append("Missing age at capture at line " + str(i+1) + " fo a wild-born elephant.")
            pass
        elif row[6] is None and cw[i] != 'wild':
            pass
        else:
            warnings.append("Format problem with age at capture: " + str(row[6]) + " at line " + str(i+1))
            reject = 1

    ########## camp
        if re.search(r"^[a-zA-Z ]+$", str(row[7])):
            pass
        elif row[7] is None:
            warnings.append("Missing camp at line " + str(i+1))
        else:
            warnings.append("Format problem with camp: " + str(row[7]) + " at line " + str(i+1))
            reject = 1

    ########## alive
        if row[8] in ('Y','N','UKN'):
            pass
        elif row[8] is None:
            warnings.append("Missing information whether alive or not at line " + str(i+1))
        else:
            warnings.append("Format problem with living status: " + str(row[8]) + " at line " + str(i+1))
            reject = 1

    ########## research
        if row[9] in ('Y','N'):
            pass
        else:
            warnings.append("Format problem with living status: " + str(row[9]) + " at line " + str(i+1))
            reject = 1

    ######### Send out to the correct lists for writing to file
    ######### Set the Flag field (1 if the row is rejected, 0 if it can go further)

        # allwarnings.append(warnings)
        if reject == 0:
            row.append(0)
            if warnings != []:
                remarks.append(warnings)
            valid.append(row)
        elif reject == 1:
            row.append(1)
            issues.append(warnings)
            rejected.append(row)

    ######### In all cases, append the warnings to the row.
        row.append(warnings)

    return[fields, valid, remarks, rejected, issues, rows]

####################################################################################
##  read_calves() READ CALF DEFINTION FILE                                 ##
####################################################################################

# A model elephant file is made up of 10 fields:
# calf_name, sex, birth, cw, caught, camp, alive, research, mother_num, mother_name
# field names irrelevant, but order necessary

def read_calves(elefile, sep=';', is_file=True):
    # Prepare empty list for column-wise parsing
    calf_name, calf_num, sex, birth, cw, caught, camp, alive, research, mother_num, mother_name = [], [], [], [], [], [], [], [], [], [], []

    if is_file == True:
    ########## Store the header in a list, and then each variable in its own column
        with open(elefile) as elefile:
            eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
            fields = next(eleread)[0:10]
            for row in eleread:
                calf_name.append(row[0])
                sex.append(row[1])
                birth.append(row[2])
                cw.append(row[3])
                caught.append(row[4])
                camp.append(row[5])
                alive.append(row[6])
                research.append(row[7])
                mother_num.append(row[8])
                mother_name.append(row[9])
                calf_num.append('')

    elif is_file == False:
        fields = ['calf_name', 'calf_num', 'sex', 'birth', 'cw', 'caught', 'camp', 'alive', 'research', 'mother_num', 'mother_name']
        for row in elefile:
            calf_name.append(row[0])
            calf_num.append('')
            sex.append(row[1])
            birth.append(row[2])
            cw.append(row[3])
            caught.append(row[4])
            camp.append(row[5])
            alive.append(row[6])
            research.append(row[7])
            mother_num.append(row[8])
            mother_name.append(row[9])

    ########## Format to lowercase Name and Camp
    lcname, lccamp = [], []
    for n in calf_name:
        lcname.append(string.capwords(n))
    for c in camp:
        lccamp.append(string.capwords(c))
    calf_name, camp = lcname, lccamp
    del lcname, lccamp

    ########## Try to guess sex, origin, alive and research
    sx, cwx, ax, rx = [], [], [], []
    for x in sex:
        if x.casefold().strip() in ('male','m','males'):
            sx.append('M')
        elif x.casefold().strip() in ('female','f','females'):
            sx.append('F')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            sx.append('UKN')
        else:
            sx.append(x)
    for x in cw:
        if x.casefold().strip() in ('c','captive'):
            cwx.append('captive')
        elif x.casefold().strip() in ('w','wild'):
            cwx.append('wild')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            cwx.append('UKN')
        else:
            cwx.append(x)
    for x in alive:
        if x.casefold().strip() in ('y','yes','alive'):
            ax.append('Y')
        elif x.casefold().strip() in ('n','no','dead'):
            ax.append('N')
        elif x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
            ax.append('UKN')
        else:
            ax.append(x)
    for x in research:
        if x.casefold().strip() in ('y','yes'):
            rx.append('Y')
        elif x.casefold().strip() in ('n','no','','none','na','null','unknown','ukn','n/a'):
            rx.append('N')
        else:
            rx.append(x)
    sex, cw, alive, research = sx, cwx, ax, rx
    del sx, cwx, ax, rx

    ########## Reformat as rows
    rows=[]
    for i,r in enumerate(num):
        row=[calf_name[i],calf_num[i],sex[i],birth[i],cw[i],caught[i],camp[i],alive[i],research[i],mother_num[i],mother_name[i]]
        rows.append(row)

    ########## Check data types row by row
    valid, remarks, rejected, issues = [], [], [], []

    for i,row in enumerate(rows):
        reject = 0
        warnings = []

        ########## Sort out missing values
        for j,x in enumerate(row):
            if x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
                row[j] = None
            else:
                pass

        ########## calf_name
        if re.search(r"^[a-zA-Z ]+$", str(row[0])):
            pass
        elif row[0] is None:
            warnings.append("Missing calf name at line " + str(i+1))
        else:
            warnings.append("Format problem with calf name: " + str(row[0]) + " at line " + str(i+1))
            reject = 1

        ########## sex
        if row[2] in ('M','F','UKN'):
            pass
        elif row[2] == None:
            warnings.append("Missing sex at line " + str(i+1))
        else:
            warnings.append("Sex must be M, F or UKN at line " + str(i+1) +" (here: " + str(row[2]) + ")")
            reject = 1

        ########## birth
        date = format_date(str(row[3]))
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            try:
                row[3] = date
            except ValueError:
                reject = 1
                warnings.append("Invalid date " + str(date) + " at line " + str(i+1))
        elif date is None:
            warnings.append("Missing birth date at line " + str(i+1))
        else:
            warnings.append("Format problem with birth date: " + str(date) + " at line " + str(i+1))
            reject = 1

        ########## CW
        if row[4] in ('captive','wild','UKN'):
            pass
        elif row[4] is None:
            warnings.append("Missing origin at line " + str(i+1))
        else:
            warnings.append("Origin must be captive, wild or UKN at line " + str(i+1) +" (here: " + str(row[4]) + ")")
            reject = 1

        ########## caught
        if re.search(r"^[0-9]+$", str(row[5])):
            pass
        elif row[5] is None and cw[i] == 'wild':
            warnings.append("Missing age at capture at line " + str(i+1) + " fo a wild-born elephant.")
            pass
        elif row[5] is None and cw[i] != 'wild':
            pass
        else:
            warnings.append("Format problem with age at capture: " + str(row[5]) + " at line " + str(i+1))
            reject = 1

        ########## camp
        if re.search(r"^[a-zA-Z ]+$", str(row[6])):
            pass
        elif row[6] is None:
            warnings.append("Missing camp at line " + str(i+1))
        else:
            warnings.append("Format problem with camp: " + str(row[6]) + " at line " + str(i+1))
            reject = 1

        ########## alive
        if row[7] in ('Y','N','UKN'):
            pass
        elif row[7] is None:
            warnings.append("Missing information whether alive or not at line " + str(i+1))
        else:
            warnings.append("Format problem with living status: " + str(row[7]) + " at line " + str(i+1))
            reject = 1

    ########## research
        if row[8] in ('Y','N'):
            pass
        else:
            warnings.append("Format problem with living status: " + str(row[8]) + " at line " + str(i+1))
            reject = 1

        ########## mother_num
        if re.search(r"^[0-9a-zA-Z]+$", str(row[9])):
            pass
        elif row[9] is None:
            warnings.append("Missing mother number at line " + str(i+1))
        else:
            warnings.append("Format problem with mother number: " + str(row[9]) + " at line " + str(i+1))
            reject = 1

        ########## mother_name
        if re.search(r"^[a-zA-Z ]+$", str(row[10])):
            pass
        elif row[10] is None:
            warnings.append("Missing calf name at line " + str(i+1))
        else:
            warnings.append("Format problem with calf name: " + str(row[1]) + " at line " + str(i+1))
            reject = 1

    ########## calf_num (synthetic number):
        [calf_name[i],sex[i],birth[i],cw[i],caught[i],camp[i],alive[i],research[i],mother_num[i],mother_name[i]]
        if row[2] is not None and row[8] is not None:
            row[1] = str(str.split(row[3])[0])+'B'+str(row[9])
        elif row[2] is not None and row[8] is None:
            row[1] = str(str.split(row[3])[0])+'U'+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26])+random.choice(string.ascii_letters[0:26]))

    ######### Send out to the correct lists for writing to file
    ######### Set the Flag field (1 if the row is rejected, 0 if it can go further)

        # allwarnings.append(warnings)
        if reject == 0:
            row.append(0)
            if warnings != []:
                remarks.append(warnings)
            valid.append(row)
        elif reject == 1:
            row.append(1)
            issues.append(warnings)
            rejected.append(row)

    ######### In all cases, append the warnings to the row.
        row.append(warnings)

    return[fields, valid, remarks, rejected, issues, rows]


####################################################################################
##  read_pedigree() READ PEDIGREE RELATIONSHIP FILE                               ##
####################################################################################
# A pedigree file is made of four columns:
# elephant_1_id, elephant_2_id, rel, coef

def read_pedigree(elefile, sep=';'):
    elephant_1_id, elephant_2_id, rel, coef = [], [], [], []

    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
        fields = next(eleread)[0:4]
        for row in eleread:
            elephant_1_id.append(row[0])
            elephant_2_id.append(row[1])
            rel.append(row[2])
            coef.append(row[3])

    # Try to guess the rel and coef fields (the latter, only if it's been assigned "NA" or the like)
    rx, cx = [], []
    for x in rel:
        if x.casefold().strip() in ('mother','m'):
            rx.append('mother')
        elif x.casefold().strip() in ('father','f'):
            rx.append('father')
        elif x.casefold().strip() in ('offspring','o'):
            rx.append('offspring')
        elif x.casefold().strip() in ('none','na','null','unknown','ukn','n/a'):
            rx.append('unknown')
        else:
            rx.append(x)
    for x in coef:
        if x.casefold().strip() in ('none','na','null','unknown','ukn','n/a'):
            cx.append('')
        else:
            cx.append(x)
    rel, coef = rx, cx
    del rx, cx

    # Check data types row by row
    valid, remarks, rejected, issues = [], [], [], []

    #reformat as rows
    rows=[]
    for i,r in enumerate(elephant_1_id):
        row=[str(elephant_1_id[i]),str(elephant_2_id[i]),str(rel[i]),str(coef[i])]
        rows.append(row)

        ########## Sort out missing values
        for j,x in enumerate(row):
            if x.casefold().strip() in ('','none','na','null','unknown','ukn','n/a'):
                row[j] = None
            else:
                pass

        # Check data types
        reject = 0
        warnings = []

        ########## elephant_1_id
        if re.search(r"^[0-9a-zA-Z]+$", row[0]):
            pass
        elif row[0] is None:
            warnings.append("Missing elephant ID-1 at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with elephant ID-1: " + row[0] + " at line " + str(i+1))
            reject = 1

        ########## elephant_2_id
        if re.search(r"^[0-9a-zA-Z]+$", row[1]):
            pass
        elif row[1] is None:
            warnings.append("Missing elephant ID-2 at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with elephant ID-2: " + row[1] + " at line " + str(i+1))
            reject = 1
        ########## rel
        if row[2] in ('mother','father','offspring','unknown'):
            pass
        elif row[2] is None:
            warnings.append("Missing relationship definition at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with relationship at line " + str(i+1))
            reject = 1

        ########## coef
        if row[3] is None:
            warnings.append("Missing kinship coefficient at line " + str(i+1))
        else:
            try:
                float(row[3])
            except ValueError:
                    warnings.append("Format problem with kinship coefficient at line " + str(i+1))
                    reject = 1

    ######### send out to the correct list
        if reject == 0:
            row.append(0)
            if warnings != []:
                remarks.append(warnings)
            valid.append(row)
        elif reject == 1:
            row.append(1)
            issues.append(warnings)
            rejected.append(row)
        row.append(warnings)
    return[fields, valid, remarks, rejected, issues, rows]

####################################################################################
##  read_measures() READ MEASURE DATA FILE                                        ##
####################################################################################

# read_measures() takes a datafile with an arbitrary number of columns.
# The only restriction is that the first three nums be num, and date.
# Each further column will have a label at the head, and values in the column.
# These will be split into simple units: elephant number, date, measure-line id, measure type, value.
# Thus, eg, mean and variance of a measure are entered as separate inserts.

def read_measures(elefile, sep=';', solved='N'):

    rows = []

    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter=sep, quotechar="'")
        fields = next(eleread)
        for row in eleread:
            if row != []:
                rows.append(row)
    nfields = fields.__len__() - 2

    # Check data types: only numeric values allowed for the measures
    valid, remarks, rejected, issues = [], [], [], []

    # Reformat rows as broken-down values with redundant num and date
    units = []
    for i,row in enumerate(rows):
        ########## other fields
        for f in range(2,nfields+2):
            u = []
            u.append(i+1) # This is the initial row number
            u.append(row[0]) # We start by pasting num and date
            u.append(row[1])
            u.append(fields[f])
            u.append(row[f])
            units.append(u)

    # Now we scan each broken-down row
    units_format = []
    for j,u in enumerate(units):
        w, flag = [], 0

        # Check num format
        if re.search(r"^[0-9]+$", u[1]):
            pass
        elif u[1] == '':
            w.append("Missing elephant number at line " + str(u[0]) + ". You need one.")
            flag = 1
        else:
            w.append("Format problem with elephant number: " + str(u[1]) + " at line " + str(u[0]))
            flag = 1

        # Check date format
        date = format_date(str(u[2]))
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            try:
                u[2] = date
            except ValueError:
                reject = 1
                warnings.append("Invalid date " + str(date) + " at line " + str(u[0]))
        elif date is None:
            warnings.append("Missing date at line " + str(u[0]))
        else:
            warnings.append("Format problem with date: " + str(date) + " at line " + str(u[0]))
            flag = 1

        # Check code format
        if re.search(r"^[a-zA-Z_]+$", u[3]):
            pass
        else:
            w.append("Format problem with code: " + str(u[3]) + " at line " + str(u[0]))
            flag = 1

        # Check value format
        if u[4].casefold().strip() in ('', 'na','none','null','n/a','unknown','ukn'):
            u[4] = None

        if u[4] is not None:
            try:
                u[4] = float(u[4])
            except ValueError:
                flag = 1
                w.append("Format problem with value "+str(u[4])+" at line "+str(i)+".")

        if u[4] is not None:
            u.append(flag)
            u.append(w)
            units_format.append(u)

    units = []
    ubuffer = []
    for b in units_format:
        ubuffer.append(b)

    for u in units_format:
        validvalue = 1
        try:
            float(u[4])
        except:
            validvalue = 0
        if solved == 'N' and validvalue == 1:
            # pull out the values of the same measure and get the median
            input_range = []
            for i,v in enumerate(ubuffer):
                # print(i)
                # print(u,v)
                if v[3] == u[3]:
                    # print(u,v)
                    try:
                        input_range.append(float(v[4]))
                    except ValueError:
                        pass
            v_array = np.array(input_range)
            vm = np.median(v_array)

            if u[4] != 0 and (u[4] > 5*vm or u[4] < vm/5):
                u[5] = 1
                u[6].append(str(u[3])+": value "+str(u[4])+" seems out of range for elephant "+str(u[1])+" at line "+str(u[0])+" (median = "+str(vm)+").")
        units.append(u)


    for u in units:
        if u[5] == 0:
            if u[6] != []:
                remarks.append(u[6])
            valid.append(u[0:5])
        elif u[5] == 1:
            if u[6] != []:
                issues.append(u[6])
            rejected.append(u[0:5])

    return[fields, valid, remarks, rejected, issues, units]

####################################################################################
##  read_events() READ EVENT LIST FILE                                            ##
####################################################################################

# an event datafile is composed of elephant num|calf_num, date, loc, code
# here, code is entered as a alphanumeric shorthand. It will be checked later on against database.

def read_events(elefile, sep=',', solved='N'):
    num, calf_num, date, loc, code = [], [], [], [], []
    valid, remarks, rejected, issues =[], [], [], []

    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter=sep, quotechar="'")
        fields = next(eleread)
        for row in eleread:
            if row != []:
                num.append(row[0])
                calf_num.append(row[1])
                date.append(row[2])
                loc.append(row[3])
                code.append(row[4])

    #reformat as rows
    rows=[]
    for i,n in enumerate(num):
        warnings, reject = [], 0

        row=[str(num[i]),str(calf_num[i]),str(date[i]),str(loc[i]),str(code[i])]
        rows.append(row)

    ########## num [COMPLUSORY or calf_num]
        if re.search(r"^[0-9a-zA-Z]+$", row[0]):
            pass
        elif row[0] == '' and calf_num[i] != '':
            warnings.append("Missing number at line " + str(i+1))
        elif row[0] == '' and calf_num[i] == '':
            warnings.append("Missing number at line " + str(i+1) + ", and no calf number. You need at least one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(row[0]) + " at line " + str(i+1))
            reject = 1

    ########## calf_num
        if re.search(r"^[0-9a-zA-Z]+$", row[1]):
            pass
        elif row[1] == '' and num[i] == '':
            warnings.append("Missing calf number at line " + str(i+1) + ". You need at least one number.")
            reject = 1
        elif row[1] == '' and num[i] != '':
            pass
        else:
            warnings.append("Format problem with calf number: " + str(row[1]) + " at line " + str(i+1))
            reject = 1

    ########## date
        date = format_date(str(row[2]))
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", date):
            try:
                row[2] = date
            except ValueError:
                reject = 1
                warnings.append("Invalid date " + str(date) + " at line " + str(i+1))
        elif date is None:
            warnings.append("Missing birth date at line " + str(i+1))
        else:
            warnings.append("Format problem with birth date: " + str(date) + " at line " + str(i+1))
            reject = 1

    ########## loc
        if re.search(r"^[a-zA-Z ]+$", row[3]):
            row[3] = string.capwords(row[3])
        elif row[3] == '':
            warnings.append("Missing location at line " + str(i+1))
        else:
            warnings.append("Format problem with location: " + str(row[3]) + " at line " + str(i+1))
            reject = 1

    ########## code
        if re.search(r"^[0-9a-zA-Z _]+$", row[4]):
            row[4] = row[4].casefold().strip()
        elif row[4] == '':
            warnings.append("Missing event code at line " + str(i+1))
        else:
            warnings.append("Format problem with event code: " + str(row[4]) + " at line " + str(i+1))
            reject = 1

    ######### send out to the correct list
        if reject == 0:
            row.append(0)
            if warnings != []:
                remarks.append(warnings)
            valid.append(row)
        elif reject == 1:
            row.append(1)
            issues.append(warnings)
            rejected.append(row)
        row.append(warnings)
    return[fields, valid, remarks, rejected, issues, rows]

####################################################################################
##  parse_output() parses the total output into mysql and warings                 ##
####################################################################################

def parse_output(stream, db, folder=None, is_elephant=True):

    stamp = db.get_stamp()
    statements = []
    warnings = []

    if folder is None:
        statement_name = str(stamp)+"_operations.sql"
        warnings_name = str(stamp)+"_conflicts.out"
    else:
        statement_name = os.path.join(folder, str(stamp)+"_operations.sql")
        warnings_name = os.path.join(folder, str(stamp)+"_conflicts.out")

    if is_elephant is True:
        for row in stream:
            if re.search(r"^INSERT", str(row)):
                statements.append(row)
            elif re.search(r"^UPDATE", str(row)):
                statements.append(row)
            elif re.search(r"^\(\"INSERT", str(row)):
                for r in row:
                    statements.append(r)
            else:
                warnings.append(row)

        with open(statement_name,"w") as s:
            for x in statements:
                s.write(str(x)+'\n')

        with open(warnings_name, "w") as w:
            for x in warnings:
                if x != '' and x is not None:
                    w.write((str(x))+'\n')

    else:
        for row in stream:
            if type(row) is list: ##WONT WORK, LENGTH OF THE STRING
                for r in row:
                    if re.search(r"^INSERT", str(r)):
                        statements.append(row)
                    elif re.search(r"^UPDATE", str(r)):
                        statements.append(row)
                    elif re.search(r"^\(\"INSERT", str(r)):
                        for x in r:
                            statements.append(x)
                    else:
                        warnings.append(r)
            else:
                if re.search(r"^INSERT", str(row)):
                    statements.append(row)
                elif re.search(r"^UPDATE", str(row)):
                    statements.append(row)
                elif re.search(r"^\(\"INSERT", str(row)):
                    for r in row:
                        statements.append(r)
                else:
                    warnings.append(row)


        with open(statement_name,"w") as s:
            for x in statements:
                s.write(str(x)+'\n')

        with open(warnings_name, "w") as w:
            for x in warnings:
                if x != '' and x is not None:
                    w.write((str(x))+'\n')


####################################################################################
##  parse_reads() parses the output from a read_ function into warnings etc       ##
####################################################################################
#the argument here is the output from a read_ function (read_elephants, read_pedigree...)

def parse_reads(read_output, prefix='reads_'):
    accepted_name = prefix+'_accepted.reads'
    rejected_name = prefix+'_rejected.reads'
    remark_name = prefix+'_accepted.log'
    issue_name =prefix+'_rejected.log'

    with open(accepted_name, "w") as accepted:
        accepted.write(str(read_output[0])[1:-1]+'\n')
        for x in read_output[1]:
            accepted.write(str(x)[1:-1]+'\n')
    with open(rejected_name, "w") as rejected:
        rejected.write(str(read_output[0])[1:-1]+'\n')
        for x in read_output[3]:
            rejected.write(str(x)[1:-1]+'\n')
    with open(remark_name,"w") as remark:
        for i,x in enumerate(read_output[2]):
            remark.write(str(i)+': '+str(x)[2:-2]+'\n')
    with open(issue_name, "w") as issue:
        for i,x in enumerate(read_output[4]):
            issue.write(str(i)+': '+str(x)[2:-2]+'\n')
