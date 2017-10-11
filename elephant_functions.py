import csv
import string
import re
import numpy as np
from datetime import datetime


#Write a "crawler" function to work the pedigrees up and down from one individual

####################################################################################
##  read_elephant() READ ELEPHANTS DEFINTION FILE                                 ##                             
####################################################################################

# A model elephant file is made up of 8 fields:
# num, name, sex, birth, cw, caught, camp, alive
# field names irrelevant, but order necessary

def read_elephant(elefile, sep):
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

    ########## Num
    for i,n in enumerate(num):
        if re.search(r"^[0-9]+$", n):
            pass
        elif n == '':
            warnings.append("Missing number at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with number: " + str(n) + " at line " + str(i+1))
            reject = 1

    ########## Name
    for i,n in enumerate(name):
        if re.search(r"^[a-zA-Z ]+$", n):
            pass
        elif n =='':
            warnings.append("Missing name at line " + str(i+1))
        else:
            warnings.append("Format problem with name: " + str(n) + " at line " + str(i+1))
            reject = 1
            
    ########## Sex
    for i,s in enumerate(sex):
        if s in ('M','F','UKN'):
            pass
        elif sex == None:
            warnings.append("Missing sex at line " + str(i+1))
        else:
            warnings.append("Sex must be M, F or UKN at line " + str(i+1) +" (here: " + str(s) + ")")
            reject = 1
        
    ########## Birth
    for i,b in enumerate(birth):
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", b):
            pass
        elif b == '':
            warnings.append("Missing birth date at line " + str(i+1))
            reject = 1
        else:
            warnings.append("Format problem with birth date: " + str(b) + " at line " + str(i+1))
            reject = 1

    ########## CW
    for i,c in enumerate(cw):
        if c in ('captive','wild','UKN'):
            pass
        elif c == '':
            warnings.append("Missing origin at line " + str(i+1))
        else:
            warnings.append("Origin pust be captive, wild or UKN at line " + str(i+1) +" (here: " + str(c) + ")")
            reject = 1
            
    ########## Caught
    for i,c in enumerate(caught):
        if re.search(r"^[0-9]+$", c):
            pass
        elif c =='':
            warnings.append("Missing age at capture at line" + str(i+1))
            pass
        else:
            warnings.append("Format problem with age at capture:", c, "at line" + str(i+1))
            reject = 1

    ########## Camp
            
    for i,c in enumerate(camp):
        if re.search(r"^[a-zA-Z ]+$", c):
            pass
        elif c =='':
            warnings.append("Missing camp at line " + str(i+1))
        else:
            warnings.append("Format problem with camp: " + str(c) + " at line " + str(i+1))
            reject = 1
  
    ########## Alive
    for i,a in enumerate(alive):
        if a in ('Y','N','UKN'):
            pass
        elif a =='':
            warnings.append("Missing information whether alive or not at line " + str(i+1))
        else:
            warnings.append("Format problem with living status: " + str(a) + " at line " + str(i+1))
            reject = 1

    for w in warnings:
        print(w)

    if reject == 0:
        return(fields,num,name,sex,birth,cw,caught,camp,alive)
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
##  read_event() READ EVENT LIST FILE                                             ##                             
####################################################################################


####################################################################################
##  read_measure() READ MEASURE DATA FILE                                         ##                             
####################################################################################
