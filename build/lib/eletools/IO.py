from datetime import datetime
import string
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
        if re.search(r"^[0-9a-zA-Z]+$", str(row[2])):
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
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", str(row[4])):
            try:
                datetime.strptime(str(row[4]), '%Y-%m-%d')
            except ValueError:
                reject = 1
                warnings.append("Invalid date " + str(row[4]) + " at line " + str(i+1))
        elif row[4]is None:
            warnings.append("Missing birth date at line " + str(i+1))
        else:
            warnings.append("Format problem with birth date: " + str(row[4]) + " at line " + str(i+1))
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
    nfields = rows[0].__len__() - 2

    #Check data types: only numeric values allowed for the measures
    reject = 0
    warnings = []

    num = []
    date = []
    for row in rows:
        num.append(row[0])
        date.append(row[1])

    if nfields < 3:
        warning.append("You need at least one measure field.")
        reject = 1

        ########## num [COMPLUSORY]
        for i,x in enumerate(num):
            if re.search(r"^[0-9]+$", x):
                pass
            elif x == '':
                warnings.append("Missing elephant number at line " + str(i+1) + ". You need one.")
                reject = 1
            else:
                warnings.append("Format problem with elephant number: " + str(x) + " at line " + str(i+1))
                reject = 1

        ########## date
        for i,x in enumerate(date):
            if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x):
                pass
            elif x == '':
                warnings.append("Missing date at line " + str(i+1))
            else:
                warnings.append("Format problem with date: " + str(x) + " at line " + str(i+1))
                reject = 1

        ########## other fields
        for f in range(nfields):
            current_field = fields[f+2]
            values = []
            for row in rows:
                values.append(row[f+2])
            for i,v in enumerate(values):
                if v.casefold().strip() in ('', 'na','none','null','n/a','unknown','ukn'):
                    v = None
                if v != None:
                    try:
                        float(v)
                    except ValueError:
                        reject = 1
                        warnings.append("Format problem with value "+str(v)+" at line "+str(i)+".")

        # Check the value ranges - isolate each measure as a vector
        # and check whether each point is within a 5x factor of the median

        if reject == 0:

            for f in range(nfields):
                current_field = fields[f+2]
                values = []
                for row in rows:
                    try:
                        values.append(float(row[f+2]))
                    except ValueError:
                        pass #for the purpose of calculating range, we ignore missing values
                v_array = np.array(values)
                vm = np.median(v_array)
                for i,v in enumerate(values):
                    if v != 0 and (v > 5*vm or v < vm/5):
                        if solved == 'N':
                            reject = 1
                            warnings.append(current_field+": value "+str(v)+" seems out of range at line "+str(i)+".")
                        elif solved == 'Y':
                            pass

            if reject == 1 and solved == 'N':
                warnings.append("Please check values are correct and declare the file Solved.")

    # Now parse the output out into small blocks
    # the measure_id field is temporary and needs to be added to the last measure_id in the db
    output = []
    for i,row in enumerate(rows):
        for f in range(nfields):
            line = (num[i], date[i], (i+1), fields[f+2], row[f+2])
            output.append(line)

    for w in warnings:
        print(w)

    if reject == 0:
        return(output)
    else:
       return(warnings)

####################################################################################
##  read_events() READ EVENT LIST FILE                                             ##
####################################################################################

# an event datafile is composed of elephant num|calf_num, date, loc, event_type, code
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
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", row[2]):
            pass
        elif row[2] == '':
            warnings.append("Missing event date at line " + str(i+1))
            reject = 1
        else:
            warnings.append("Format problem with event date: " + str(row[2]) + " at line " + str(i+1))
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
        if re.search(r"^[0-9a-zA-Z ]+$", row[4]):
            row[4] = row[4].casefold().strip()
        elif row[4] == '':
            warnings.append("Missing event code at line " + str(i+1))
        else:
            warnings.append("Format problem with event code: " + str(row[5]) + " at line " + str(i+1))
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

def parse_output(stream, db, folder=None):

    stamp = db.get_stamp()
    statements = []
    warnings = []

    if folder is None:
        statement_name = str(stamp)+"_operations.sql"
        warnings_name = str(stamp)+"_conflicts.out"
    else:
        statement_name = os.path.join(folder, str(stamp)+"_operations.sql")
        warnings_name = os.path.join(folder, str(stamp)+"_conflicts.out")

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
