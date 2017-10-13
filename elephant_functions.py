import csv
import string
import re
import numpy as np
from datetime import datetime


# Write a "crawler" function to work the pedigrees up and down from one individual
# Write a "consolidate_alive" function to assess who is alive / dead now from data

####################################################################################
##  read_elephant() READ ELEPHANTS DEFINTION FILE                                 ##                             
####################################################################################

# A model elephant file is made up of 10 fields:
# num, name, calf_num, sex, birth, cw, caught, camp, alive, research
# field names irrelevant, but order necessary

def read_elephant(elefile, sep=';'):
    num = []
    name = []
    calf_num = []
    sex = []
    birth = []
    cw = []
    caught = []
    camp = []
    alive = []
    research = []

    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
        fields = next(eleread)[0:8]
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

    # Lowercase Name and Camp
    lcname = []
    lccamp = []
    for n in name:
        lcname.append(string.capwords(n))
    for c in camp:
        lccamp.append(string.capwords(c))
    name = lcname
    camp = lccamp
    del lcname
    del lccamp

    # Try to guess sex, origin, alive and research
    sx = []
    cwx = []
    ax = []
    rx = []
    for x in sex:
        if x.casefold() in ('male','m','males'):
            sx.append('M')
        elif x.casefold() in ('female','f','females'):
            sx.append('F')
        elif x.casefold() in ('','none','na','null','unknown','ukn','n/a'):
            sx.append('UKN')
        else:
            sx.append(x)

    for x in cw:
        if x.casefold() in ('c','captive'):
            cwx.append('captive')
        elif x.casefold() in ('w','wild'):
            cwx.append('wild')
        elif x.casefold() in ('','none','na','null','unknown','ukn','n/a'):
            cwx.append('UKN')
        else:
            cwx.append(x)

    for x in alive:
        if x.casefold() in ('y','yes','alive'):
            ax.append('Y')
        elif x.casefold() in ('n','no','dead'):
            ax.append('N')
        elif x.casefold() in ('','none','na','null','unknown','ukn','n/a'):
            ax.append('UKN')
        else:
            ax.append(x)

    for x in research:
        if x.casefold() in ('y','yes'):
            rx.append('Y')
        elif x.casefold() in ('n','no','','none','na','null','unknown','ukn','n/a'):
            rx.append('N')
        else:
            rx.append(x)

    sex = sx
    cw = cwx
    alive = ax
    research = rx
    del sx
    del cwx
    del ax
    del rx

    # Check data types
    reject = 0
    warnings = []

    ########## num
    for i,x in enumerate(num):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x == '' and calf_num[i] != '':
            print("calf", calf_num[i])
            warnings.append("Missing number at line " + str(i+1))
        elif x == '' and calf_num[i] == '':
            warnings.append("Missing number at line " + str(i+1) + ", and no calf number. You need at least one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## name
    for i,x in enumerate(name):
        if re.search(r"^[a-zA-Z ]+$", x):
            pass
        elif x =='':
            warnings.append("Missing name at line " + str(i+1))
        else:
            warnings.append("Format problem with name: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## calf_num
    for i,x in enumerate(calf_num):
        if re.search(r"^[0-9a-zA-Z]+$", x):
            pass
        elif x == '' and num[i] == '':
            warnings.append("Missing calf number at line " + str(i+1) + ". You need at least one number.")
            reject = 1
        elif x == '' and num[i] != '':
            pass        
        else:
            warnings.append("Format problem with calf number: " + str(x) + " at line " + str(i+1))
            reject = 1
            
    ########## sex
    for i,x in enumerate(sex):
        if x in ('M','F','UKN'):
            pass
        elif x == None:
            warnings.append("Missing sex at line " + str(i+1))
        else:
            warnings.append("Sex must be M, F or UKN at line " + str(i+1) +" (here: " + str(x) + ")")
            reject = 1
        
    ########## birth
    for i,x in enumerate(birth):
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x):
            pass
        elif x == '':
            warnings.append("Missing birth date at line " + str(i+1))
            reject = 1
        else:
            warnings.append("Format problem with birth date: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## CW
    for i,x in enumerate(cw):
        if x in ('captive','wild','UKN'):
            pass
        elif x == '':
            warnings.append("Missing origin at line " + str(i+1))
        else:
            warnings.append("Origin pust be captive, wild or UKN at line " + str(i+1) +" (here: " + str(x) + ")")
            reject = 1
            
    ########## caught
    for i,x in enumerate(caught):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x =='' and cw[i] == 'wild':
            warnings.append("Missing age at capture at line " + str(i+1) + " fo a wild-born elephant.")
            pass
        elif x =='' and cw[i] != 'wild':
            pass
        else:
            warnings.append("Format problem with age at capture: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## camp
            
    for i,x in enumerate(camp):
        if re.search(r"^[a-zA-Z ]+$", x):
            pass
        elif x =='':
            warnings.append("Missing camp at line " + str(i+1))
        else:
            warnings.append("Format problem with camp: " + str(x) + " at line " + str(i+1))
            reject = 1
  
    ########## alive
    for i,x in enumerate(alive):
        if x in ('Y','N','UKN'):
            pass
        elif x =='':
            warnings.append("Missing information whether alive or not at line " + str(i+1))
        else:
            warnings.append("Format problem with living status: " + str(x) + " at line " + str(i+1))
            reject = 1
            
    ########## research
    for i,x in enumerate(research):
        if x in ('Y','N'):
            pass
        else:
            warnings.append("Format problem with living status: " + str(x) + " at line " + str(i+1))
            reject = 1

    for w in warnings:
        print(w)

    lines = []
    lines.append(tuple(fields))
    if reject == 0:
        for i,x in enumerate(num):
            line = (num[i],name[i],calf_num[i],sex[i],birth[i],cw[i],caught[i],camp[i],alive[i],research[i])
            lines.append(line)
        
        return(lines)
    else:
       return(warnings)

####################################################################################
##  read_pedigree() READ PEDIGREE RELATIONSHIP FILE                               ##                             
####################################################################################
# A pedigree file is made of four columns:
# elephant_1_id, elephant_2_id, rel, coef

def read_pedigree(elefile, sep=';'):
    elephant_1_id = []
    elephant_2_id = []
    rel = []
    coef = []
    
    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
        fields = next(eleread)[0:4]
        for row in eleread:
            elephant_1_id.append(row[0])
            elephant_2_id.append(row[1])
            rel.append(row[2])
            coef.append(row[3])
            
    # Try to guess the rel and coef fields (the latter, only if it's been assigned "NA" or the like)
    rx = []
    cx = []
    for x in rel:
        if x.casefold() in ('mother','m'):
            rx.append('mother')
        elif x.casefold() in ('father','f'):
            rx.append('father')
        elif x.casefold() in ('offspring','o'):
            rx.append('offspring')
        elif x.casefold() in ('none','na','null','unknown','ukn','n/a'):
            rx.append('unknown')
        else:
            rx.append(x)
    for x in coef:
        if x.casefold() in ('none','na','null','unknown','ukn','n/a'):
            cx.append('')
        else:
            cx.append(x)
    rel = rx
    coef = cx
    del rx
    del cx

    # Check data types
    reject = 0
    warnings = []

    ########## elephant_1_id
    for i,x in enumerate(elephant_1_id):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x == '':
            warnings.append("Missing elephant ID-1 at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with elephant ID-1: " + str(x) + " at line " + str(i+1))
            reject = 1

    for i,x in enumerate(elephant_2_id):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x == '':
            warnings.append("Missing elephant ID-2 at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with elephant ID-2: " + str(x) + " at line " + str(i+1))
            reject = 1

    for i,x in enumerate(rel):
        if x in ('mother','father','offspring','unknown'):
            pass
        elif x == '':
            warnings.append("Missing relationship definition at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with relationship at line " + str(i+1))
            reject = 1

    for i,x in enumerate(coef):
        if re.search(r"^[0-9]+.[0-9]+$",x):
            pass
        elif x== '':
            warnings.append("Missing kinship coefficient at line " + str(i+1))
        else:
            warnings.append("Format problem with kinship coefficient at line " + str(i+1))
            reject = 1

    for w in warnings:
        print(w)

    if reject == 0:
        return(fields,elephant_1_id,elephant_2_id,rel,coef)
    else:
        return(warnings)

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
                if v.casefold() in ('', 'na','none','null','n/a','unknown','ukn'):
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
##  read_event() READ EVENT LIST FILE                                             ##                             
####################################################################################

# an event datafile is composed of elephant num|calf_num, date, loc, event_type, code
# here, code is entered as a alphanumeric shorthand. It will be checked later on against database.

def read_events(elefile, sep=';', solved='N'):
    num = []
    calf_num = []
    date = []
    loc = []
    event_type = []
    code = []

    reject = 0
    warnings = []
    
    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter=sep, quotechar="'")
        fields = next(eleread)
        for row in eleread:
            if row != []:
                num.append(row[0])
                calf_num.append(row[1])
                date.append(row[2])
                loc.append(row[3])
                event_type.append(row[4])
                code.append(row[5])

    # No good guessing here I think. Better enter the types properly.

    ########## num [COMPLUSORY or calf_num]
    for i,x in enumerate(num):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x == '' and calf_num[i] != '':
            warnings.append("Missing number at line " + str(i+1))
        elif x == '' and calf_num[i] == '':
            warnings.append("Missing number at line " + str(i+1) + ", and no calf number. You need at least one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## calf_num
    for i,x in enumerate(calf_num):
        if re.search(r"^[0-9a-zA-Z]+$", x):
            pass
        elif x == '' and num[i] == '':
            warnings.append("Missing calf number at line " + str(i+1) + ". You need at least one number.")
            reject = 1
        elif x == '' and num[i] != '':
            pass        
        else:
            warnings.append("Format problem with calf number: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## date
    for i,x in enumerate(date):
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x):
            pass
        elif x == '':
            warnings.append("Missing event date at line " + str(i+1))
            reject = 1
        else:
            warnings.append("Format problem with event date: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## loc
    for i,x in enumerate(loc):
        if re.search(r"^[a-zA-Z ]+$", x):
            loc[i] = string.capwords(x)
        elif x == '':
            warnings.append("Missing location at line " + str(i+1))
        else:
            warnings.append("Format problem with location: " + str(x) + " at line " + str(i+1))
            reject = 1
            
    ########## event_type [COMPLUSORY]
    for i,x in enumerate(event_type):
        if x.casefold() in ('capture','accident','disease','death','alive'):
            event_type[i] = x.casefold()
        elif x == '':
            warnings.append("Missing event type at line " + str(i+1))
            reject = 1
        else:
            warnings.append("Invalid event type: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## code
    for i,x in enumerate(code):
        if re.search(r"^[0-9a-zA-Z ]+$", x):
            code[i] = x.casefold()
        elif x == '':
            warnings.append("Missing event code at line " + str(i+1))
        else:
            warnings.append("Format problem with event code: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## output
    for w in warnings:
        print(w)

    lines = []
    lines.append(tuple(fields))
    if reject == 0:
        for i,x in enumerate(event_type):
            line = (num[i],calf_num[i],date[i],loc[i],event_type[i],code[i])
            lines.append(line)
        
        return(lines)
    else:
       return(warnings)

