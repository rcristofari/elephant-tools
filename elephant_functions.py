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

def read_eleph(elefile):
    num = []
    name = []
    sex = []
    birth = []
    cw = []
    caught = []
    camp = []
    alive = []

    with open("../elephants_gap.csv") as elefile:
        eleread = csv.reader(elefile, delimiter = ",", quotechar="'")
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

    for x in ax:
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

    print(alive[0:10])

    # Check data types
    reject = 0
    
#Change NA, na, N/A to None
#try to fix case and easy developments

    ########## Num
    for n in num:
        if re.search(r"^[0-9]+$", n):
            pass
        elif n == '':
            print("Missing number at line", num.index(n), ". You need one.")
            reject = 1
        else:
            print("Format problem with number:", n, "at line", num.index(n))
            reject = 1

    ########## Name
    for n in name:
        if re.search(r"^[a-zA-Z ]+$", n):
            pass
        elif n =='':
            print("Missing name at line", name.index(n))
        else:
            print("Format problem with name:", n, "at line", name.index(n))
            
    ########## Sex
    for s in sex:
        if s in ('M','F','UKN'):
            pass
        elif sex == None:
            print("Missing sex at line", sex.index(s))
        else:
            print("Sex must be M, F or UKN at line ", sex.index(s), " (here: ", s, ")", sep="")
            reject = 1
        
    ########## Birth
    for b in birth:
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", b):
            pass
        elif b == '':
            print("Missing date at line", birth.index(b))
        else:
            print("Format problem with date:", b, "at line", birth.index(b))
            reject = 1

    ########## CW
    for c in cw:
        if c in ('captive','wild','UKN'):
            pass
        elif c == '':
            print("Missing origin at line", cw.index(c))
        else:
            print("Origin pust be captive, wild or UKN at line ", cw.index(c), " (here: ", c, ")", sep="")
            reject = 1
            
    ########## Caught
    for c in caught:
        if re.search(r"^[0-9]+$", c):
            pass
        elif c =='':
            print("Missing age at capture at line", caught.index(c))
        else:
            print("Format problem with age at capture:", c, "at line", caught.index(c))
            reject = 1

    ########## Camp
    for c in camp:
        if re.search(r"^[a-zA-Z ]+$", c):
            pass
        elif c =='':
            print("Missing camp at line", camp.index(c))
        else:
            print("Format problem with camp:", c, "at line", camp.index(c))
            
    ########## Alive
    for a in alive:
        if a in ('Y','N','UKN'):
            pass
        elif a =='':
            print("Missing information whether alive or not at line", alive.index(a))
        else:
            print("Format problem with living status:", a, "at line", alive.index(a))

####################################################################################
##  read_pedigree() READ PEDIGREE RELATIONSHIP FILE                               ##                             
####################################################################################


####################################################################################
##  read_event() READ EVENT LIST FILE                                             ##                             
####################################################################################


####################################################################################
##  read_measure() READ MEASURE DATA FILE                                         ##                             
####################################################################################
