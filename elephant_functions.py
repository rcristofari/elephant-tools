import csv
import string
import re
import numpy as np
from datetime import datetime


#Write a "crawler" function to work the pedigrees up and down from one individual

####################################################################################
##  read_eleph() READ ELEPHANTS DEFINTION FILE                                    ##                             
####################################################################################

# A model elephant file is made up of 8 fields:
# num, name, sex, birth, cw, caught, camp, alive
# field names irrelevant, but order necessary

def read_eleph(elefile, sep):
    num = []
    name = []
    sex = []
    birth = []
    cw = []
    caught = []
    camp = []
    alive = []

    with open(elefile) as elefile:
        eleread = csv.reader(elefile, delimiter = sep, quotechar="'")
        fields = next(eleread)[0:8]
        for row in eleread:
            num.append(row[0])
            name.append(row[1])
            sex.append(row[2])
            birth.append(row[3])
            cw.append(row[4])
            caught.append(row[5])
            camp.append(row[6])
            alive.append(row[7])

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

    # Try to guess sex, origin, and alive
    sx = []
    cwx = []
    ax = []
    for x in sex:
        if x.casefold() in ('male','m','males'):
            sx.append('M')
        elif x.casefold() in ('female','f','females'):
            sx.append('F')
        elif x.casefold() in ('none','na','null','unknown','ukn','n/a'):
            sx.append('UKN')
        else:
            sx.append(x)

    for x in cw:
        if x.casefold() in ('c','captive'):
            cwx.append('captive')
        elif x.casefold() in ('w','wild'):
            cwx.append('wild')
        elif x.casefold() in ('none','na','null','unknown','ukn','n/a'):
            cwx.append('UKN')
        else:
            cwx.append(x)

    for x in alive:
        if x.casefold() in ('y','yes','alive'):
            ax.append('Y')
        elif x.casefold() in ('n','no','dead'):
            ax.append('N')
        elif x.casefold() in ('none','na','null','unknown','ukn','n/a'):
            ax.append('UKN')
        else:
            ax.append(x)

    sex = sx
    cw = cwx
    alive = ax
    del sx
    del cwx
    del ax

    # Check data types
    reject = 0
    warnings = []
    
#Change NA, na, N/A to None
#try to fix case and easy developments

    ########## Num
    for i,n in enumerate(num):
        if re.search(r"^[0-9]+$", n):
            pass
        elif n == '':
            warnings.append("Missing number at line " + str(i) +". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(n) + " at line " + str(i))
            reject = 1

    ########## Name
    for i,n in enumerate(name):
        if re.search(r"^[a-zA-Z ]+$", n):
            pass
        elif n =='':
            warnings.append("Missing name at line " + str(i))
        else:
            warnings.append("Format problem with name: " + str(n) + " at line " + str(i))
            reject = 1
            
    ########## Sex
    for i,s in enumerate(sex):
        if s in ('M','F','UKN'):
            pass
        elif sex == None:
            warnings.append("Missing sex at line " + str(i))
        else:
            warnings.append("Sex must be M, F or UKN at line " + str(i) +" (here: " + str(s) + ")")
            reject = 1
        
    ########## Birth
    for i,b in enumerate(birth):
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", b):
            pass
        elif b == '':
            warnings.append("Missing birth date at line " + str(i))
            reject = 1
        else:
            warnings.append("Format problem with birth date: " + str(b) + " at line " + str(i))
            reject = 1

    ########## CW
    for i,c in enumerate(cw):
        if c in ('captive','wild','UKN'):
            pass
        elif c == '':
            warnings.append("Missing origin at line " + str(i))
        else:
            warnings.append("Origin pust be captive, wild or UKN at line " + str(i) +" (here: " + str(c) + ")")
            reject = 1
            
    ########## Caught
    for i,c in enumerate(caught):
        if re.search(r"^[0-9]+$", c):
            pass
        elif c =='':
            warnings.append("Missing age at capture at line" + str(i))
            pass
        else:
            warnings.append("Format problem with age at capture:", c, "at line" + str(i))
            reject = 1

    ########## Camp
            
    for i,c in enumerate(camp):
        if re.search(r"^[a-zA-Z ]+$", c):
            pass
        elif c =='':
            warnings.append("Missing camp at line " + str(i))
        else:
            warnings.append("Format problem with camp: " + str(c) + " at line " + str(i))
            reject = 1
  
    ########## Alive
    for i,a in enumerate(alive):
        if a in ('Y','N','UKN'):
            pass
        elif a =='':
            warnings.append("Missing information whether alive or not at line " + str(i))
        else:
            warnings.append("Format problem with living status: " + str(a) + " at line " + str(i))
            reject = 1

    for w in warnings:
        print(w)

    if reject == 0:
        return(fields,num,name,sex)
    else:
        return(warnings)

####################################################################################
##  read_pedigree() READ PEDIGREE RELATIONSHIP FILE                               ##                             
####################################################################################
# A pedigree file is made of four columns:
# elephant_1_id, elephant_2_id, rel, coef

def read_pedigree(elefile, sep):
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
            
    print(rel)

####################################################################################
##  read_event() READ EVENT LIST FILE                                             ##                             
####################################################################################


####################################################################################
##  read_measure() READ MEASURE DATA FILE                                         ##                             
####################################################################################
