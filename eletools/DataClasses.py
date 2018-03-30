from datetime import datetime
import string
import numpy as np
from eletools.Utilities import *

# General flagging system:
    # - A 'flag' field works on a 2-power basis.
    #    - 0 means there is nothing to say about the data (initial state)
    #    - 1 means the line has been rejected at "read"
    #    - 2 means the data can go into the database (INSERT)
    #    - 4 means the database will be updated (UPDATE)
    #    - 8 means the data is already known
    #    - 16,32,64... means the data is conflicting and rejected (code henceforth depending on the class)
    # - A 'Output' field gives additional information (warnings and/or SQL statements)

# For the elephant class, the specific conflict flags are:
    # 16: 'num',
    # 32: 'name',
    # 64: 'calf_num'
    # 128: 'sex',
    # 256: 'birth',
    # 512: 'cw',
    # 1024: 'age of capture',
    # 2048: 'camp',
    # 4096: 'alive',
    # 8192: 'research'

# For the pedigree class:
    # 16 : sex
    # 32 : birth
    # 64 : missing elephant

# For the event class:
    # 16 : age
    # 32 : captive/wild
    # 64 : missing elephant
    # 128 : missing event type


# For the measure class:
    # 16 : value out of range
    # 32 : replicate
    # 64 : missing elephant
    # 128 : missing measure code

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "ELEPHANT"                              ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class elephant:

    def __init__(self, num=None, name=None, calf_num=None, sex=None, birth=None, cw=None, caught=None, camp=None, alive=None, research=None, solved='N', flag=0):

        # Some execution parameters
        #Is the input file a conflict resolution (Y/N)? If Y, name and camp will be appended.
        if solved in ('Y','y','YES','yes'):
            self.__solved='Y'
        else:
            self.__solved='N'
        self.__interactive=1 # Not implemented so far

        # Non-prefixed parameters describe user input
        if num is not None:
            self.__num=str(num) #kept private since it is the primary key for the input. Has a getter function.
        else:
            self.__num = None
        if calf_num is not None:
            self.calf_num = str(calf_num)
        else:
            self.calf_num=calf_num
        if name is not None:
            self.name=string.capwords(name)
        else:
            self.name=name
        self.sex=sex
        if birth is not None:
            self.birth=datetime.strptime(birth, '%Y-%m-%d').date()
        else:
            self.birth=birth
        self.cw=cw
        if caught is not None:
            self.caught=float(caught)
        else:
            self.caught = caught
        if camp is not None:
            self.camp=string.capwords(camp)
        else:
            self.camp=camp
        self.alive=alive
        self.research=research
        self.flag = flag


        # Prefixed parameters describe database content. They are private and are not modified (declared here for reference only)
        self.__db_id = None
        self.__db_num = None
        self.__db_calf_num = None
        self.__db_name = None
        self.__db_sex = None
        self.__db_birth = None
        self.__db_cw = None
        self.__db_caught = None
        self.__db_camp = None
        self.__db_alive = None
        self.__db_research = None
        self.__db_commits = None

        # These variables pass the state of each operation to the next
        self.__sourced=0
        self.__checked=0
        self.status=None #Result of the check() function
        self.statement=None #SQL statement issued by the write() function
        self.__toggle_write_flag=0

        # __x variables describe state of the comparison db/input
        self.__xnum=0
        self.__xcalf_num=0
        self.__xname=0
        self.__xsex=0
        self.__xbirth=0
        self.__xcw=0
        self.__xcaught=0
        self.__xcamp=0
        self.__xalive=0
        self.__xresearch=0

        # A list to gather warnings for each line:
        self.warnings = []
        self.in_db = ("Index:\t\t-"
            +"\n-----------------------------------------"
            +"\nNumber:\t\t-"
            +"\nName:\t\t-"
            +"\nCalf number:\t\t-"
            +"\nSex:\t\t-"
            +"\nBirth date:\t\t-"
            +"\nAge at capture:\t-"
            +"\nCamp:\t\t-"
            +"\nAlive:\t\t-"
            +"\n-----------------------------------------"
            +"\nResearch:\t\t-")
        self.in_input = ''
        # Getter function for some private variables that could be useful in scripting

    def __repr__(self):
        r = ("\n-----------------------------------------"
                         + "\nNumber:\t\t" + str(self.__num)
                         + "\nName:\t\t" + str(self.name)
                         + "\nCalf number:\t" + str(self.calf_num)
                         + "\nSex:\t\t" + str(self.sex)
                         + "\nBirth date:\t" + str(self.birth) + ", " + str(self.cw)
                         + "\nAge at capture:\t" + str(self.caught)
                         + "\nCamp:\t\t" + str(self.camp)
                         + "\nAlive:\t\t" + str(self.alive)
                         + "\n-----------------------------------------"
                         + "\nResearch:\t" + str(self.research))
        return(r)

    def get_list(self):
        return((0, self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research, None))

    def get_num(self):
        return(self.__num)

    def get_solved(self):
        return(self.__solved)

    def set_solved(solved):
        self.__solved=solved

    ################################################################################
    ## 'source' function reads the elephant from the database if it exists        ##
    ################################3################################################

    def source(self, db):

        self.__db = db
        self.__sourced = 0

        if self.__num is not None:
            results = self.__db.get_elephant(num=self.__num)
            if results is None and self.calf_num is not None:
                results = self.__db.get_elephant(calf_num=self.calf_num)
        elif self.__num is None and self.calf_num is not None:
            results = self.__db.get_elephant(calf_num=self.calf_num)

        else:
            results = None
            print("You need either an elephant number or a calf number to proceed")

        if results is None:
            self.__sourced = 2
            if self.__num is not None:
                print("Elephant number", self.__num, "is absent from the database.")
            elif self.__num is None and self.calf_num is not None:
                print("Calf number", self.calf_num, "is absent from the database.")

        else:
            self.__sourced = 1

            self.__db_id = results[0]
            self.__db_num = results[1]

            if results[2] is not None:
                self.__db_name = string.capwords(results[2])
            self.__db_calf_num = results[3]
            self.__db_sex = results[4]
            self.__db_birth = results[5]
            self.__db_cw = results[6]
            self.__db_caught = results[7]

            if results[8] is not None:
                self.__db_camp = string.capwords(results[8])
            self.__db_alive = results[9]
            self.__db_research = results[10]
            self.__db_commits = results[11]

            self.in_db = ("Index:\t\t"+str(self.__db_id)
                    + "\n-----------------------------------------"
                    + "\nNumber:\t\t"+str(self.__db_num)
                    + "\nName:\t\t"+str(self.__db_name)
                    + "\nCalf number:\t\t"+str(self.__db_calf_num)
                    + "\nSex:\t\t"+str(self.__db_sex)
                    + "\nBirth date:\t\t"+str(self.__db_birth)+", "+str(self.__db_cw)
                    + "\nAge at capture:\t"+str(self.__db_caught)
                    + "\nCamp:\t\t"+str(self.__db_camp)
                    + "\nAlive:\t\t"+str(self.__db_alive)
                    + "\n-----------------------------------------"
                    + "\nResearch:\t\t"+str(self.__db_research))

            print("\nThis elephant is present in the database as:\n", self.in_db, sep='')

            return(self.__db_id, self.__db_num, self.__db_name, self.__db_sex, self.__db_birth, self.__db_cw, self.__db_caught, self.__db_camp, self.__db_alive, self.__db_commits)

    ################################################################################
    ## 'check' function, checks consistency between database and new data         ##
    ################################################################################

    # Outcome code for __x variables: 0= conflict, 1 = matching, 2 = update database,
    # 3 = still missing, 4 = already in database, no input.

    def check(self):
        if self.__sourced == 0:
            os.system('clear')
            print("\nCheck: You must source this elephant first using elephant.source().")
        elif self.__sourced == 2:
            print("This elephant is not in the database, you can proceed to write() directly.")
            self.in_input = ("\n-----------------------------------------"
            +"\nNumber:\t\t"+str(self.__num)
            +"\nName:\t\t"+str(self.name)
            +"\nCalf number:\t\t"+str(self.calf_num)
            +"\nSex:\t\t"+str(self.sex)
            +"\nBirth date:\t\t"+str(self.birth)+", "+str(self.cw)
            +"\nAge at capture:\t"+str(self.caught)
            +"\nCamp:\t\t"+str(self.camp)
            +"\nAlive:\t\t"+str(self.alive)
            +"\n-----------------------------------------"
            +"\nResearch:\t\t"+str(self.research))

        elif self.__sourced == 1:
            print("\nCONSISTENCY CHECK:")
            self.in_input = ("\n-----------------------------------------"
            +"\nNumber:\t\t"+str(self.__num)
            +"\nName:\t\t"+str(self.name)
            +"\nCalf number:\t\t"+str(self.calf_num)
            +"\nSex:\t\t"+str(self.sex)
            +"\nBirth date:\t\t"+str(self.birth)+", "+str(self.cw)
            +"\nAge at capture:\t"+str(self.caught)
            +"\nCamp:\t\t"+str(self.camp)
            +"\nAlive:\t\t"+str(self.alive)
            +"\n-----------------------------------------"
            +"\nResearch:\t\t"+str(self.research))

            print("This elephant is specified here as:\n", self.in_input, sep='')
            # print("\nOperations for elephant number ", self.__num, ":", sep='')

    ############ Num and calf_num checked together (inter-dependent)
            numwarning = None
            if self.__num is not None and self.__num == self.__db_num:
                self.__xnum = 1
                numwarning = ("Numbers match")
                if self.__db_calf_num == self.calf_num and self.calf_num is not None:
                    self.__xcalf_num = 1
                    numwarning = ("Calf numbers match")
                elif self.calf_num is not None and self.__db_calf_num is None:
                    self.__xcalf_num = 2
                    numwarning = ("Calf number was still unknown, updating database.")
                elif self.__db_calf_num is None and self.calf_num is None:
                    self.__xcalf_num = 3
                    numwarning = ("Calf number is still missing.")
                elif self.__db_calf_num is not None and self.calf_num is None:
                    self.__xcalf_num = 4
                    numwarning = ("Calf number entered as"+str(self.__db_calf_num)+"in the database, no change.")
                elif self.__db_calf_num is not None and self.calf_num is not None and self.calf_num != self.__db_calf_num:
                    self.__xcalf_num = 0
                    numwarning = ("> Calf numbers are conflicting. You need to solve that manually.")
            elif self.__num is None and self.__db_num is None:
                if self.calf_num is not None and self.calf_num == self.__db_calf_num:
                    self.__xnum = 3
                    self.__xcalf_num = 1
                    numwarning = ("No adult number, but calf numbers match.")
                elif self.calf_num is not None and self.__db_calf_num is None: #this should not be possible in the present version.
                    self.__xnum = 3
                    self.__xcalf_num = 2
                    numwarning = ("Calf number unknown so far, updating database.")
                elif self.calf_num is None and self.__db_calf_num is not None: #this should not be possible in the present version.
                    self.__xnum = 3
                    self.__xcalf_num = 4
                    numwarning = ("Calf number entered as"+str(self.__db_calf_num)+"in the database, no change.")
                elif self.calf_num is not None and self.calf_num != self.__db_calf_num:
                    self.__xnum = 3
                    self.__xcalf_num = 0
                    numwarning = ("> Calf numbers do not match ("+str(self.calf_num)+" here, "+str(self.__db_calf_num)+" in the db)")
                elif self.calf_num is None and self.__db_calf_num is None: #this should not be possible in the present version.
                    self.__xnum = 0
                    self.__xcalf_num = 0
                    numwarning = ("> You need at least an adult or a calf number.")
            elif self.__num is not None and str(self.__num) != str(self.__db_num): #Impossible in the current version (match priority to num) but if later on: this means the match has been made on calf_num, so the case is clear on that side.
                if self.calf_num == self.__db_calf_num: #just a check so far, but later on there may be research by birth date.
                    self.__xnum = 0
                    self.__xcalf_num = 1
                    numwarning = ("> Adult numbers do not match. Please check the input.")
            #This is a slightly complicated case: we provided a num and a calf num, but fell back on calf num because num was absent. Not possible with the current version yet.
            elif self.calf_num is not None and self.__db_calf_num is None: #this means the match has been made on calf_num, so the case is clear on that side.
                if self.calf_num == self.__db_calf_num: #just a check so far, but later on there may be research by birth date.
                    self.__xnum = 2
                    numwarning = ("Adult number was still unknown, updating database.")
            if numwarning is not None:
                self.warnings.append(numwarning)

            ############ Name
            namewarning = None
            if self.name is not None  and self.__db_name is not None and self.name in self.__db_name: #Partial match since there could be multiple names in the database
                self.__xname = 1
                self.name = self.__db_name #This is in case that name is a subset of database name
                namewarning = ("Names match.")
            elif self.__db_name is None and self.name is not None:
                self.__xname = 2
                namewarning = ("No known name yet, updating database.")
            elif self.__db_name is None and self.name is None:
                self.__xname = 3
                namewarning = ("Name is still missing")
            elif self.__db_name is not None and self.name is None:
                self.__xname = 4
                namewarning = ("This elephant is known in database as "+str(self.__db_name)+" - no change.")
            else :
                self.__xname = 0
                if self.__solved == 'N':
                    namewarning = ("> Different name in database. You need to solve the conflict manually.")
                if self.__solved =='Y':
                    self.name = self.__db_name + ", " + self.name
                    self.__xname = 2
                    namewarning = ("> Alias name appended to database")
            if namewarning is not None:
                self.warnings.append(namewarning)

            ############ Sex
            sexwarning = None
            if self.sex == self.__db_sex:
                self.__xsex = 1
                sexwarning = ("Sexes match.")
            elif self.__db_sex == 'UKN' and self.sex is not None:
                self.__xsex = 2
                sexwarning = ("No known sex yet, updating database.")
            elif self.__db_sex == 'UKN' and self.sex is None:
                self._xsex = 3
                self.sex = self.__db_sex
                sexwarning = ("Sex is still missing")
            elif self.__db_sex != 'UKN' and self.sex is None:
                self.__xsex = 4
                if self.__db_sex == 'M':
                    __strsex = 'male'
                elif self.__db_sex == 'F':
                    __strsex = 'female'
                sexwarning = ("It is known in database as a "+__strsex+" - no change.")
            else :
                self.__xsex = 0
                if self.__interactive == 1:
                    sexwarning = ("> Different sex in database. You need to solve the conflict manually.")
            if sexwarning is not None:
                self.warnings.append(sexwarning)

            ############ Birth date
            birthwarning = None
            if self.birth == self.__db_birth and self.birth is not None:
                self.__xbirth = 1
                birthwarning = ("Birth dates match.")
            elif self.__db_birth is None and self.birth is not None:
                self.__xbirth = 2
                birthwarning = ("No known birth date yet, updating database.")
            elif self.__db_birth is None and self.birth is None:
                self.__xbirth = 3
                birthwarning = ("Birth date is still missing")
            elif self.__db_birth is not None and self.birth is None:
                self.__xbirth = 4
                born = self.__db_birth
                now = datetime.now().date()
                age = round(((now - born).days / 365.25))
                if self.alive == 'Y' or self.__db_alive == 'Y':
                    birthwarning = ("Birth data known as "+str(self.__db_birth)+" ("+str(age)+" years old) - no change.")
                else:
                    birthwarning = ("Birth data known as "+str(self.__db_birth)+" ("+str(age)+" years ago) - no change.")
            else :
                self.__xbirth = 0
                if self.__interactive == 1:
                    birthwarning = ("> Different birth date in database. You need to solve the conflict manually.")
            if birthwarning is not None:
                self.warnings.append(birthwarning)

            ############ Wild or captive
            wildwarning = None
            if self.cw == self.__db_cw:
                self.__xcw = 1
                wildwarning = ("Captive/wild matches.")
            elif self.__db_cw == 'UKN' and self.cw is not None:
                self.__xcw = 2
                wildwarning = ("Unknown whether captive or wild so far, updating database.")
            elif self.__db_cw == 'UKN' and self.cw is None:
                self.__xcw = 3
                self.cw = self.__db_cw
                wildwarning = ("Origin is still missing")
            elif self.__db_cw != 'UKN' and self.cw is None:
                self.__xcw = 4
                wildwarning = ("In the database, it is born "+str(self.__db_cw)+" - no change.")
            else:
                self.__xcw = 0
                if self.__interactive == 1:
                    wildwarning = ("> Different origin in database. You need to solve the conflict manually.")
            if wildwarning  is not None:
                self.warnings.append(wildwarning)

            ############ Age at capture
            caughtwarning = None
            if self.cw == 'captive' or self.cw == 'UKN' or self.__db_cw == 'captive' or self.__db_cw =='UKN':
                if self.caught == self.__db_caught and self.caught is not None:
                    self.__xcaught = 0
                    caughtwarning = ("> Ages at capture match, but this elephant is registered as captive born. Check database and input data.")
                elif self.__db_caught is None and self.caught is not None:
                    self.__xcaught = 0
                    caughtwarning = ("> No known age at capture yet, but this elephant is registered as captive born. Check your data.")
                elif self.__db_caught is None and self.caught is None:
                    self.__xcaught = 1
                    caughtwarning = ("Age at capture is still missing, and this elephant is registered as captive born. All good.")
                elif self.__db_caught is not None and self.caught is None:
                    self.__xcaught = 0
                    self.caught = self.__db_caught
                    caughtwarning = ("> In the database, it was captured at age "+str(self.__db_cw)+" ,  but this elephant is registered as captive born. Check the database.")
                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        caughtwarning = ("> Different age at capture in database. You need to solve the conflict manually.")

            elif self.cw == 'wild' or self.__db_cw == 'wild':
                if self.caught == self.__db_caught and self.caught is not None:
                    self.__xcaught = 1
                    caughtwarning = ("Ages at capture match.")
                elif self.__db_caught is None and self.caught is not None:
                    self.__xcaught = 2
                    caughtwarning = ("No known age at capture yet, updating database.")
                elif self.__db_caught is None and self.caught is None:
                    self.__xcaught = 3
                    caughtwarning = ("Age at capture is still missing")
                elif self.__db_caught is not None and self.caught is None:
                    self.__xcaught = 4
                    caughtwarning = ("In the database, it was captured at age "+str(self.__db_cw)+" - no change.")
                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        caughtwarning = ("> Different age at capture in database. You need to solve the conflict manually.")
                if caughtwarning is not None:
                    self.warnings.append(caughtwarning)

            ############ Camp
            campwarning = None
            if self.camp is not None and self.__db_camp is not None and self.camp in self.__db_camp:
                self.__xcamp = 1
                self.camp = self.__db_camp
                campwarning = ("Camps match.")
            elif self.__db_camp is None and self.camp is not None:
                self.__xcamp = 2
                campwarning = ("No known camp yet, updating database.")
            elif self.__db_camp is None and self.camp is None:
                self.__xcamp = 3
                campwarning = ("Camp is still missing")
            elif self.__db_camp is not None and self.camp is None:
                self.__xcamp = 4
                campwarning = ("In the database, it comes from "+str(self.__db_camp)+" - no change.")
            else :
                self.__xcamp = 0
                if self.__solved == 'N':
                    campwarning = ("> Different camp in database. You need to solve the conflict manually.")
                if self.__solved =='Y':
                    self.camp = self.__db_camp + ", " + self.camp
                    self.__xcamp = 1
                    campwarning = ("> New camp appended to database")
            if campwarning is not None:
                self.warnings.append(campwarning)

            ############ Alive or dead
            alivewarning = None
            if self.alive == self.__db_alive:
                self.__xalive = 1
                alivewarning = ("Living status matches.")
            elif self.__db_alive == 'UKN' and self.alive is not None:
                self.__xalive = 2
                if self.alive == 'Y':
                    alivewarning = ("We were not sure if was alive, updating database.")
                elif self.alive == 'N':
                    alivewarning = ("We didn't know it was dead, updating database & requiescat in pace.")
            elif self.__db_alive == 'UKN' and self.alive is None:
                self.__xalive = 3
                alivewarning = ("Still unknown whether alive or not.")
            elif self.__db_alive != 'UKN' and self.alive is None:
                self.__xalive = 4
                if self.__db_alive == 'Y':
                    alivewarning = ("In the database, it is alive - no change")
                elif self.__db_alive == 'N':
                    alivewarning = ("In the database, it is dead - no change, & requiescat in pace.")
            else :
                self.__xalive = 0
                if self.__interactive == 1:
                    alivewarning = ("> Different living status in database. You need to solve the conflict manually.")
            if alivewarning is not None:
                self.warnings.append(alivewarning)

            ############ Research elephant
            researchwarning = None
            if self.research == self.__db_research and self.research is not None:
                self.__xresearch = 1
                researchwarning = ("Research status matches")
            elif self.research is not None and (self.__db_research is None or self.__db_research == 'N'):
                self.__xresearch = 2
                researchwarning = ("We didn't know that it was a research elephant, updating database.")
            elif self.research is None and self.__db_research is None:
                sef.__xresearch = 2
                self.research = 'N'
                researchwarning = ("No information, setting database to Not a research elephant.")
            elif self.research == 'N' and self.__db_research == 'Y':
                self.__xresearch = 4
                self.research = None
                researchwarning = ("> If you wish to remove this elephant's research status, do it manually.")
            elif self.research == 'Y' and (self.__db_research == 'N' or self.__db_research is None):
                self.__xresearch = 2
                researchwarning = ("Not yet a research elephant in the database, updating database.")
            elif self.research is None and self.__db_research is not None:
                self.__xresearch = 4
                if self.__db_research == 'N':
                    researchwarning = ("In the database, it is not a research elephant - no change")
                elif self.__db_research == 'Y':
                    researchwarning = ("In the database, it is a research elephant - no change")
            if researchwarning is not None:
                self.warnings.append(researchwarning)

            ############ Check the consistency of birth date and living status
            agewarning = None
            if self.birth is not None:
                now = datetime.now().date()
                age = ((now - self.birth).days) / 365.25
                if self.alive == 'Y' and age > 90:
                    agewarning = ("> This elephant is now over 90 years old. Are you sure it is still alive?")
                    self.__xalive = 0
                elif age < 0:
                    agewarning = ("> This elephant is born in the future. We're doing science on the edge here.")
                    self.__xalive = 0
            if agewarning is not None:
                self.warnings.append(agewarning)

        #Here, do the final fusion of data, and give an outcome (write to database or write out for manual conflict resolution)

        self.status = (self.__xnum, self.__xname, self.__xcalf_num, self.__xsex, self.__xbirth, self.__xcw, self.__xcaught, self.__xcamp, self.__xalive, self.__xresearch)
        self.__checked = 1

        return(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research, self.__db_commits)

    ################################################################################
    ## 'write' function writes out an sql statement to insert/update the elephant ##
    ################################################################################

    def write(self, db):

        self.__db = db

        if self.__xnum == 2:
            wnum = self.__num
        else:
            wnum = None
        if self.__xname == 2:
            wname = self.name
        else:
            wname = None
        if self.__xcalf_num == 2:
            wcalf_num = self.calf_num
        else:
            wcalf_num = None
        if self.__xsex == 2:
            wsex = self.sex
        else:
            wsex = None
        if self.__xbirth == 2:
            wbirth = self.birth
        else:
            wbirth = None
        if self.__xcw == 2:
            wcw = self.cw
        else:
            wcw = None
        if self.__xcaught == 2:
            wcaught = self.caught
        else:
            wcaught = None
        if self.__xcamp == 2:
            wcamp = self.camp
        else:
            wcamp = None
        if self.__xalive == 2:
            walive = self.alive
        else:
            walive = None
        if self.__xresearch == 2:
            wresearch = self.research
        else:
            wresearch = None

        ########## The elephant must have been checked in the database
        if self.__sourced == 0:
            print("\nWrite: You must check that the elephant is absent from the database first.")

        ########## If this elephant is not in the database yet,
        # write an insert statement (consistency of data assumed).

        elif self.__sourced == 2:

            if self.__num is not None and self.birth is not None:

                # this is outsourced to mysqlconnect
                self.out = self.__db.insert_elephant(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research)
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 2

            elif self.calf_num is not None and self.birth is not None:

                # this is outsourced to mysqlconnect
                self.out = self.__db.insert_elephant(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research)
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 2

            elif self.birth is None:
                self.out = "[Conflict] Elephant number " + str(self.__num) + " is not in the database yet, but you must provide at least number and birth date"
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 1

        ########## If the elephant has been checked and there is no conflict, write an update statement.

        elif self.__checked == 1 and any(x == 0 for x in self.status) == False:

        ########## All fields are matching, no update (special case as "data already known")
            if all(x in (1,3,4) for x in self.status):
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 8
                self.out = "This elephant is already in the database, nothing to change."
                pass
            else:
                #this is outsourced to mysqlconnect
                self.out = self.__db.update_elephant(wnum, wname, wcalf_num, wsex, wbirth, wcw, wcaught, wcamp, walive, wresearch, self.__db_commits, self.__db_id)
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 4

        ########## If there is a pending conflict, we write out the conflicts and build the corresponding flag

        else:

            # Check which fields are conflicting
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            if self.__toggle_write_flag == 0:
                # Set the 2-power flag:
                for n in i:
                    self.flag = self.flag + 2**(n+4)

            # Make a string of conflict field names for the warning field
            f = ('num','name','calf_num','sex','birth','cw','age of capture','camp','alive','research')
            conflicts = ''
            for x in i:
                conflicts = conflicts+', '+f[x]
            c = conflicts.rstrip(', ')
            conflicts = c[2:]+"."

            self.out = self.warnings

            if self.__sourced != 2 and self.__num is not None:
                self.out.append("[Conflict] Elephant number "+str(self.__num)+": you need to solve conflicts for: "+conflicts)
            elif self.__sourced != 2 and self.__num is None:
                self.out.append("[Conflict] Calf number "+str(self.calf_num)+": you need to solve conflicts for: "+conflicts)

        # In all cases, the output is the input row, the flag, and the result line (warning or SQL operation)
        self.__toggle_write_flag = 1
        output_row = [self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research, self.flag, self.out]
        return(output_row)


            ##Add a light check here to see that a captive elephant has no age at capture.

#  ##########################################################################
 ##############################################################################
###                                                                          ###
##                            CLASS "PEDIGREE"                                ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

# As a rule, pedigree relationships can only be inserted. Modification will need to be well
# thought and done by hand in the database (too risky to make them automatic). The only
# automatic modification is the update of the coef field (from null to a coef). So the task here is
# to check if the relationship exists, and to issue a double statement.

class pedigree:

    def __init__(self, eleph_1=None, eleph_2=None, rel=None, coef=None, eleph_2_is_calf=False, flag=0, last_id=None):


        # Non-prefixed parameters describe user input
        self.eleph_1=eleph_1
        self.eleph_2=eleph_2
        self.rel=rel
        self.coef=coef
        self.eleph_2_is_calf=eleph_2_is_calf
        self.last_id = last_id

        # Prefixed parameters describe database content
        self.__db_id = None
        self.__db_id1 = None
        self.__db_id2 = None
        self.__db_eleph_1 = None
        self.__db_eleph_2 = None
        self.__db_rel_1 = None
        self.__db_rel_2 = None
        self.__db_coef_1 = None
        self.__db_coef_2 = None
        self.__db_rel_id = None
        self.__rel_1 = None
        self.__rel_2 = None
        self.__rel_fwd = None
        self.__rel_rev = None
        self.flag = flag

        # Elephant 2 mode:
        if type(self.eleph_2) is elephant:
            self.eleph_2_is_object = True
        else:
            self.eleph_2_is_object = False

        # These variables pass the state of each operation to the next
        self.__sourced=0
        self.__checked=0
        self.status=None #Result of the check() function
        self.statement=None #SQL statement issued by the write() function
        self.flag=0
        self.__toggle_write_flag=0

        # __x variables describe state of the comparison db/input
        self.__x1=None
        self.__x2=None
        self.__xrel=None
        self.__xcoef=None
        self.__xsex=None
        self.__xbirth=None

        # A list to gather warnings for each line:
        self.warnings = []

    ################################################################################
    ## 'source' function reads the pedigree from the database if it exists        ##
    ################################################################################

    def source(self, db):

        self.__db = db
        self.__db_eleph_1 = None
        self.__db_eleph_2 = None
        self.elephant_absent = 0

        # Standard case, both elephants are normally in the database:

        if self.eleph_2_is_object is False:

            try:
                el1 = self.__db.get_elephant(num=self.eleph_1)

                if self.eleph_2_is_calf is False:
                    el2 = self.__db.get_elephant(num=self.eleph_2)
                else:
                    el2 = self.__db.get_elephant(calf_num=self.eleph_2)

                self.__db_eleph_1 = []
                self.__db_eleph_2 = []
                for x in (0,4,5,9):
                    self.__db_eleph_1.append(el1[x])
                    self.__db_eleph_2.append(el2[x])
                self.__db_id1 = self.__db_eleph_1[0]
                self.__db_id2 = self.__db_eleph_2[0]

            except TypeError:
                missing = ''
                if el1 is None and el2 is None:
                    missing = ("Impossible to find elephant " + self.eleph_1 + " nor " + self.eleph_2 + " in the database.")
                elif el1 is None and el2 is not None:
                    missing = ("Impossible to find elephant " + self.eleph_1 + " in the database.")
                elif el1 is not None and el2 is None:
                    missing = ("Impossible to find elephant " + self.eleph_2 + " in the database.")
                self.warnings.append(missing)
                print(missing)
                self.elephant_absent = 1

            if self.__db.get_pedigree(self.__db_id1, self.__db_id2):
                self.__rel_1 = self.__db.get_pedigree(self.__db_id1, self.__db_id2)[0]
                self.__rel_2 = self.__db.get_pedigree(self.__db_id1, self.__db_id2)[1]

            # If the relationship already exists, check exact consistency of the entry:

            if self.__rel_1 is not None and self.__rel_2 is not None:

                delta = (self.__db_eleph_1[2] - self.__db_eleph_2[2]).days / 365.25

                if (self.__rel_1[1] == self.__rel_2[1]
                    and self.__rel_1[5] == self.__rel_2[5]
                    and self.__rel_1[2] == self.__rel_2[3]
                    and self.__rel_1[3] == self.__rel_2[2]
                    and ((self.__rel_1[4] == 'mother' and self.__rel_2[4] == 'offspring')
                         or (self.__rel_1[4] == 'offspring' and self.__rel_2[4] == 'mother')
                         or (self.__rel_1[4] == 'father' and self.__rel_2[4] == 'offspring')
                         or (self.__rel_1[4] == 'offspring' and self.__rel_2[4] == 'father')
                         or (self.__rel_1[4] == 'unknown' or self.__rel_2[4] == 'unknown'))):

                        self.__sourced = 1

                        #Testing the consistency of the relationship as entered in the database.
                        #Testing that the age difference is at least 7 years (should be tuned better).
                        #In case of problem, self.__sourced reverts to 0.
                        agewarning = None
                        if self.__rel_1[4] == 'mother':
                            if delta > -10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Mother too young ("+str(round(abs(delta)))+" years old)")
                            elif delta < -70:
                                self.__sourced = 0
                                agewarning = ("Error in database: Mother too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        if self.__rel_2[4] == 'mother':
                            if delta < 10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Mother too young ("+str(round(abs(delta)))+" years old)")
                            elif delta > 10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Mother too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        elif self.__rel_1[4] == 'father':
                            if delta > -10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Father too young ("+str(round(abs(delta)))+" years old)")
                            elif delta < -70:
                                self.__sourced = 0
                                agewarning = ("Error in database: Father too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        elif self.__rel_2[4] == 'father':
                            if delta < 10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Father too young ("+str(round(abs(delta)))+" years old)")
                            elif delta > 70:
                                self.__sourced = 0
                                agewarning = ("Error in database: Father too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        elif self.__rel_1[4] == 'offspring':
                            if delta < 10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Parent too young ("+str(round(abs(delta)))+" years old)")
                            elif delta > 70:
                                self.__sourced = 0
                                agewarning = ("Error in database: Parent too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        elif self.__rel_2[4] == 'offspring':
                            if delta > -10:
                                self.__sourced = 0
                                agewarning = ("Error in database: Parent too young ("+str(round(abs(delta)))+" years old)")
                            elif delta < -70:
                                self.__sourced = 0
                                agewarning = ("Error in database: Parent too old ("+str(round(abs(delta)))+" years old)")
                            else:
                                pass

                        if agewarning is not None:
                            print(agewarning)
                            self.warnings.append(agewarning)

                if self.elephant_absent == 1:
                    self.__sourced = 0

                if self.__sourced == 1:
                    print("This relationship is already correctly entered in the database, nothing to do.")

                else:
                    print("This relationship is present but incorreclty entered in the database.\nCheck it manually (relationship id: ",
                          self.__rel_1[1], ", elephant ids ", self.__db_eleph_1[0], " and ", self.__db_eleph_2[0], ").", sep="")

            elif self.__rel_1 is None and self.__rel_2 is None and self.elephant_absent != 1:
                self.__sourced = 2
                print("This relationship is not in the database yet. You can proceed to check()")

        # Alternative case, the second elephant is an object:

        elif self.eleph_2_is_object is True:

            try:
                el1 = self.__db.get_elephant(num=self.eleph_1)
                el2 = self.eleph_2.get_list()

                # Reformat the self.eleph_2 variable to match the general case
                if self.eleph_2_is_calf is False:
                    self.eleph_2 = el2[1]
                else:
                    self.eleph_2 = el2[3]

                self.__db_eleph_1 = []
                self.__db_eleph_2 = []

                for x in (0, 4, 5, 9):
                    self.__db_eleph_1.append(el1[x])
                    self.__db_eleph_2.append(el2[x])
                self.__db_id1 = self.__db_eleph_1[0]
                self.__db_id2 = self.__db_eleph_2[0]
                self.__sourced = 2
                print("This relationship is not in the database yet. You can proceed to check()")

            except TypeError:
                if el1 is None and el2 is not None:
                    missing = ("Impossible to find elephant " + self.eleph_1 + " in the database.")
                else:
                    missing = ("Error in the elephant input.")
                self.warnings.append(missing)
                self.elephant_absent = 1
                self.sourced = 0

    ################################################################################
    ## 'check' function, checks consistency between database and new data         ##
    ################################################################################

    def check(self):

        if self.__sourced == 0:
            if self.elephant_absent == 1:
                print("This relationship involves an unknown elephant. Impossible to process it.")
            else:
                print("\nThis relationship is present in the database with an error. Please correct it manually")
            self.__checked = 3

    #####################################

        elif self.__sourced == 1:
            self.__checked = 2
            print("\nThis relationship is already correctly entered in the database, nothing to do.")

        elif self.__sourced == 2:
            self.__checked = 1
            self.__xsex = 1
            self.__xbirth = 1

            delta = (self.__db_eleph_2[2] - self.__db_eleph_1[2]).days / 365.25

            print("\nThe proposed relationship states that elephant ", self.eleph_1, " (", self.__db_eleph_1[1],
                  "), born on ", self.__db_eleph_1[2], ", is the ", self.rel, " of elephant ", self.eleph_2, " (",
                  self.__db_eleph_2[1], "), born on ", self.__db_eleph_2[2], ".\n", sep="")

            # Check that this elephant does not already have a father or mother.
            redundancywarning = None
            if self.eleph_2_is_object is False:

                if self.rel == "mother": # elephant 2 should not already have a mother or a father.
                    if self.__db.get_mother(id=self.__db_id2) is not None:
                        self.__checked = 0
                        redundancywarning = ("Elephant " + self.eleph_2 + " already has a registered mother ("
                                             + self.__db.get_mother(self.eleph_2) + ").")
                elif self.rel == "father":
                    if self.__db.get_father(id=self.__db_id2) is not None:
                        self.__checked = 0
                        redundancywarning = ("Elephant " + self.eleph_2 + " already has a registered father ("
                                             + self.__db.get_father(self.eleph_2) + ").")
                if redundancywarning is not None:
                    print(redundancywarning)
                    self.warnings.append(redundancywarning)

            structurewarning = None
            if self.rel == 'mother':  # eleph_1 must be a female older than self.eleph_2 (10 to 70 years age difference)
                if self.__db_eleph_1[1] != 'F':
                    self.__xsex = 0
                    self.__checked = 0
                    structurewarning = (self.eleph_1 + " is not a female in the database, you cannot declare it as 'mother' here.")
                elif delta < 10:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Mother too young (" + str(round(abs(delta))) + " years old)")
                elif delta > 70:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Mother too old (" + str(round(abs(delta))) + " years old)")
                else:
                    pass

            elif self.rel == 'father':  # eleph_1 must be a male older than self.eleph_2 (10 to 70 years age difference)
                if self.__db_eleph_1[1] != 'M':
                    self.__xsex = 0
                    self.__checked = 0
                    structurewarning = (self.eleph_2+" is not a male in the database, you cannot declare it as 'father' here.")
                elif delta < 10:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Father too young ("+str(round(abs(delta)))+" years old)")
                elif delta > 70:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Father too old ("+str(round(abs(delta)))+" years old)")
                else:
                    pass

            elif self.rel == 'offspring':  # eleph_1 must be younger than self.eleph_2 (10 to 70 years age difference)
                if delta > -10:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Parent too young ("+str(round(abs(delta)))+" years old)")
                elif delta < -70:
                    self.__xbirth = 0
                    self.__checked = 0
                    structurewarning = ("Parent too old ("+str(round(abs(delta)))+" years old)")
                else:
                    pass

            # Check that the parent was alive at the moment of birth:
            if self.rel in ('mother', 'father'):
                if self.__db_eleph_1[3] == 'N':
                    # Get the parent's death date:
                    dod = self.__db.get_date_of_death(id=self.__db_id1)
                    if dod:
                        delta = (dod - self.__db_eleph_2[2]).days
                        if delta < 0: # then the birth is posterior to the parent's death
                            self.__xbirth = 0
                            self.__checked = 0
                            structurewarning = ("Parent died (" + str(round(abs(delta)/365.25)) + " years before this calf's birth)")

            elif self.rel == 'offspring':
                if self.__db_eleph_2[3] == 'N':
                    # Get the parent's death date:
                    dod = self.__db.get_date_of_death(id=self.__db_id2)
                    if dod:
                        delta = (dod - self.__db_eleph_1[2]).days
                        if delta < 0: # then the birth is posterior to the parent's death
                            self.__xbirth = 0
                            self.__checked = 0
                            structurewarning = ("Parent died (" + str(round(abs(delta)/365.25)) + " years before this calf's birth)")

            if structurewarning is not None:
                print(structurewarning)
                self.warnings.append(structurewarning)


            else:
                pass

            if self.__checked == 1:
                print("The proposed relationship is consistent. You can proceed to pedigree.write().")
            else:
                print("There are inconsistencies in the proposed relationship. Check your input.")
                self.status = (self.__xsex, self.__xbirth)
                # The actual writing of error will be done by write()

    ################################################################################
    ## 'write' function writes out two sql instert statements or an error         ##
    ################################################################################

    def write(self, db):
        self.__db = db

        if self.rel == "mother":
            self.__rel_fwd = quote("mother")
            self.__rel_rev = quote("offspring")
        elif self.rel == "father":
            self.__rel_fwd = quote("father")
            self.__rel_rev = quote("offspring")
        elif self.rel == "unknown":
            self.__rel_fwd = quote("unknown")
            self.__rel_rev = quote("unknown")
        elif self.rel == "offspring":
            if self.__db_eleph_2[1] == 'F':
                self.__rel_fwd = quote("offspring")
                self.__rel_rev = quote("mother")
            elif self.__db_eleph_2[1] == 'M':
                self.__rel_fwd = quote("offspring")
                self.__rel_rev = quote("father")
            else:
                self.__rel_fwd = quote("offspring")
                self.__rel_rev = quote("unknown")

        if self.coef is None:
            self.coef = 'null'
        else:
            self.coef = quote(self.coef)

        if self.__checked == 1:
            self.out = self.__db.insert_pedigree(self.__db_id1, self.__db_id2, self.__rel_fwd, self.__rel_rev, self.coef, last_id=self.last_id)
            if self.__toggle_write_flag == 0:
                self.flag = self.flag + 2

        elif self.__checked == 2:
            self.out = "This relationship is already in the database, nothing to change."
            if self.__toggle_write_flag == 0:
                self.flag = self.flag + 8

        elif self.__checked == 3:
            if self.elephant_absent == 0:
                self.out = ("[Conflict] Elephants number " + self.eleph_1 + " and " + self.eleph_2 + ": this relationship exists in the database, but with an error.")
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 2**7

            elif self.elephant_absent == 1:
                self.out = ("[Conflict] Elephants number " + self.eleph_1 + " and " + self.eleph_2 + ": this relationship involves an unknown elephant.")
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag + 2**6

        elif self.__checked == 0:
            if self.__toggle_write_flag == 0:
                self.flag = self.flag + 16
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            if self.__toggle_write_flag == 0:
                # Set the 2-power flag:
                for n in i:
                    self.flag = self.flag + 2**(n+4)

            f = ['sex','birth date']
            conflicts = str()
            for x in i:
                conflicts = conflicts+f[x]
            self.out = ("[Conflict] Elephants number " + self.eleph_1 + " and " + self.eleph_2 + ": you need to solve conflicts for " + conflicts)

        self.__toggle_write_flag = 1
        self.warnings.append(self.out)
        # In all cases, the output is the input row, the flag, and the result line (warning or SQL operation)
        output_row = [self.eleph_1, self.eleph_2, self.rel, self.coef, self.flag, self.warnings]
        return(output_row)

#   ##########################################################################
 ##############################################################################
###                                                                          ###
##                             CLASS "MEASURE"                                ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

#NEED TO ADD A DETECTION FOR REPLICATES IN THE READ MODULE (DON'T KNOW IF WE DO REPLICATES AT ALL?)

class measure:

    def __init__(self, date, measure_id, measure, value, num=None, calf_num=None, replicate='N', solved = 'N', flag=0):
        self.__num=num
        self.__calf_num=calf_num
        self.__date=date
        self.__measure_id=measure_id
        self.__measure=measure
        self.__value = float(value)
        if replicate in ('Y','y','YES','yes'):
            self.__replicate='Y'
        else:
            self.__replicate='N'
        if solved in ('Y','y','YES','yes'):
            self.__solved='Y'
        else:
            self.__solved='N'
        self.__code = None
        self.__xval = 1
        self.__xeleph = 0
        self.__xrep = 1
        self.__sourced = 0
        self.__checked = 0
        self.__xmissval = 1

        self.warnings = []
        self.out = []
        self.flag = flag
        self.__toggle_write_flag = 0

    ################################################################################
    ## 'source' function reads the measure from the database if it exists         ##
    ################################################################################

    #Sees if a similar measure is already in the database
    #Verifies if that measure type is already in the measure_code table.
    #Note that adding a new measure should also be done through python (mysqlconnect module)

    def source(self, db):

        self.__db=db

        # Get the ID of the elephant, or print out an error if the elephant is absent from the database.
        if self.__num is not None:
            self.__elephant = self.__db.get_elephant(num = self.__num)
        elif self.__num is None and self.__calf_num is not None:
            self.__elephant = self.__db.get_elephant(calf_num = self.__calf_num)
        missing = None
        if self.__elephant is None:
            missing = ("This elephant is absent from the database. Impossible to add a measure.")
            self.__sourced = 1
            self.__elephant_id = None
            self.__xeleph = 0
            print(missing)
            if missing is not None:
                self.warnings.append(missing)
        else:
            self.__elephant_id = self.__elephant[0]
            self.__xeleph = 1

            # Check whetherthat measure type is present in the measure_code table:
            self.__code = self.__db.get_measure_code(self.__measure)

            missing = None
            if self.__code is None:
                missing = ("Measure type "+str(self.__measure)+" is not registered yet.\nPlease register it before proceeding (or check for typos)")
                self.__sourced = 1
                self.__xmissval = 0
                print(missing)
                if missing is not None:
                    self.warnings.append(missing)

            else:
                if self.__num is not None:
                    self.__db_line = self.__db.get_measure(self.__num, self.__date, self.__code)
                elif self.__num is None and self.__calf_num is not None:
                    self.__db_line = self.__db.get_measure(self.__calf_num, self.__date, self.__code) # get_measure recognises the calf number format

                #Cases where the measure is already entered in a similar form in the database:
                if self.__db_line is not None:
                    duplicate = None
                    self.__db_value = self.__db_line[5]
                    if float(self.__value) == self.__db_value:
                        self.__sourced = 1
                        duplicate = ("An identical measure is already entered in the database.")
                        self.__xrep = 0
                    else:
                        if self.__replicate == 'N':
                            duplicate = ("There is already a measure for "+str(self.__measure)+" at that date in the database ("+str(self.__value)+")")
                            self.__sourced = 1
                            self.__xrep = 0
                    if duplicate is not None:
                        self.warnings.append(duplicate)
                        print(duplicate)

                #Cases where no similar measure is already in the database (i.e. not same elephant, date and parameter)
                elif self.__db_line is None or (self.__db_line is not None and self.__replicate == 'Y'):
                    print("This measure is not in the database yet.")
                    self.__sourced = 2

    ################################################################################
    ## 'check' function, checks consistency between database and new data         ##
    ################################################################################

    # Checks whether the value is in the range of the whole series (a power of 10 only to check the unit)
    # No check as to chronology since samples may be processed post-mortem (and date may be analysis, not sampling date)

    def check(self,db):
        self.__db=db
        self.__checked = 0
        self.__xval = 0

        if self.__sourced == 0:
            print("You need to source this measure first.")

        elif self.__sourced == 1:
            if self.__xeleph == 1 and self.__xmissval == 1:
                self.__checked = 1
                print("Nothing to do here.")
            else:
                self.__checked = 0
                print("Impossible to go further.")

        # If the measure is not present yet but the measure type is valid
        elif self.__sourced == 2 and self.__xmissval == 1:
            outrange = None
            self.__mean_value = None
            mv = self.__db.get_average_measure(self.__code)
            try:
                self.__mean_value = float(mv)
            except:
                print("No values for that measure in the database yet")
                self.__xval = 1

            if self.__mean_value is not None and (self.__value > 10*self.__mean_value or self.__value < self.__mean_value/10) and self.__solved == 'N':
                outrange = ("The proposed value is out of the mean order of magnitude in the database. Check the input.")
                self.__xval = 0
            else:
                print("This measure is valid. You can proceed to write()")
                self.__xval = 1
                self.__checked = 2

            if outrange is not None:
                self.warnings.append(outrange)

    ################################################################################
    ## 'write' function writes out the sql instert statement or an error          ##
    ################################################################################

    def write(self, db):
        self.__db=db

        if self.__checked == 0:
            if self.__sourced == 0:
                print("This entry must pass through check() first.")
                #### HERE IS THE RUB


            elif self.__sourced == 1:
                # self.warnings.append("[Conflict] This entry is not valid. Please check input before proceeding.")

                #######################
                # Case where the elephant is present in the database
                if self.__xeleph == 1 and self.__xmissval == 1:
                    if self.__xval == 0:
                        if self.__xrep == 1:
                            self.warnings.append("[Conflict] Value out of range for elephant "+str(self.__num)+" (here "+str(self.__measure)+"="+str(self.__value)+" vs. mean "+str(self.__mean_value)+")")
                            if self.__toggle_write_flag == 0:
                                self.flag = self.flag+16
                        elif self.__xrep == 0:
                            self.warnings.append("[Conflict] Value "+str(self.__value)+" ("+str(self.__measure)+") for elephant "+str(self.__num)+" appears to be a duplicate")
                            if self.__toggle_write_flag == 0:
                                self.flag = self.flag+32

                # Case where the elephant is absent from the database
                elif self.__xeleph == 0:
                    self.warnings.append("[Conflict] Elephant number "+str(self.__num)+" is absent from the database")
                    if self.__toggle_write_flag == 0:
                        self.flag = self.flag+64

                # Case where the measure type is not in the db yet:
                elif self.__xmissval == 0:
                    self.warnings.append("[Conflict] The measure type "+str(self.__measure)+" is not registered yet")
                    if self.__toggle_write_flag == 0:
                        self.flag = self.flag+128

        elif self.__checked == 1 and self.__sourced == 1:
            print("This measure is already entered, nothing to do.")
            if self.__toggle_write_flag == 0:
                self.flag = self.flag + 8

        elif self.__checked == 2:
            self.out = self.__db.insert_measure(self.__measure_id, self.__elephant_id, self.__date, self.__code, self.__value)
            if self.__toggle_write_flag == 0:
                self.flag = self.flag + 2

        for w in self.warnings:
            self.out.append(w)

        self.__toggle_write_flag = 1
        # In all cases, the output is the input row, the flag, and the result line (warning or SQL operation)
        output_row = [self.__measure_id, self.__num, self.__date, self.__code, self.__value, self.flag, self.out]
        return(output_row)


#  ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "EVENT"                                 ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class event:

    def __init__(self, date, code, num=None, calf_num=None, loc=None, solved = 'N', flag=0):
        self.__num=num
        self.__calf_num=calf_num
        self.__date=datetime.strptime(date, '%Y-%m-%d').date()
        self.__loc=loc
        self.__code=code
        if solved in ('Y','y','YES','yes'):
            self.__solved='Y'
        else:
            self.__solved='N'
        self.__sourced = 0
        self.__checked = 0
        self.__xevent = 1
        self.__xdate = 1
        self.__xcw = 1
        self.warnings = []
        self.flag = flag
        self.__toggle_write_flag = 0

    ################################################################################
    ## 'source' function reads the event from the database if it exists           ##
    ################################################################################
    # Like a measure, an event is considered redundant if it shares the same individual, date, and type.

    def source(self,db):
        self.__db=db

        #Get the ID of the elephant:
        if self.__num is not None:
            self.__elephant = self.__db.get_elephant(num = self.__num)
        elif self.__num is None and self.__calf_num is not None:
            self.__elephant = self.__db.get_elephant(calf_num = self.__calf_num)
        else:
            print("You need at least one identifying number")
        if self.__elephant is None:
            print("This elephant is absent from the database. Impossible to add an event.")
            self.__xeleph = 0

        else:
            self.__elephant_id = self.__elephant[0]
            self.__db_birth = self.__elephant[5]
            self.__db_alive = self.__elephant[9]
            self.__db_cw = self.__elephant[6]
            self.__xeleph = 1

            #Start by seeing if that measure type is present in the measure_code table:
            try:
                self.__code_id = self.__db.get_event_code(self.__code)[0]
                self.__event_class = self.__db.get_event_code(self.__code)[1]
            except:
                print("Event code", self.__code, "is not registered yet.\nPlease register it before proceeding (or check for typos)")
                self.__xevent = 0

            else:
                self.__db_line = self.__db.get_event(self.__num, self.__date, self.__event_class)
                #Cases where the measure is already entered in a similar form in the database:
                if self.__db_line is not None:

                    redundancy = None
                    self.__db_code = self.__db_line[4]
                    if self.__code_id == self.__db_code:
                        self.__sourced = 1
                        redundancy = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: An identical event is already entered in the database.")
                        self.__xrep = 0
                    else:
                        if self.__solved == 'N':
                            redundancy = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: There is already an event of class '"+self.__event_class+"' for elephant "+str(self.__num)+" at that date in the database.")
                            self.__sourced = 1
                            self.__xrep = 0
                    if redundancy is not None:
                        self.warnings.append(redundancy)

                #Cases where no similar measure is already in the database (i.e. not same elephant, date and parameter)
                elif self.__db_line is None or (self.__db_line is not None and self.__solved == 'Y'):
                    print("This event is not in the database yet.")
                    self.__sourced = 2

    ################################################################################
    ## 'check' function checks consistency between database and new data          ##
    ################################################################################

    # Consistency check on death: a death event prohibits further events, and triggers an update in the elephants table
    # Events over 100 years of age requires a "solved" flag to be allowed
    # Consistency check on birth: no event is allowed prior to birth datetime
    # Possible event types are : 'capture','accident','disease','death','alive'

    def check(self, db):
        if self.__sourced == 0:
            print("You must verify the database first using source()")
        elif self.__sourced == 1:
            print("This event already appears to be in the database. Nothing to do.")

        elif self.__sourced == 2:
            self.__db = db
            self.__xdate = 1
            self.__xcw = 1
            delta = (self.__date - self.__db_birth).days / 365.25
            self.__date_of_death = self.__db.get_date_of_death(self.__elephant_id)
            self.__last_alive = self.__db.get_last_alive(self.__elephant_id)
            self.__last_breeding = self.__db.get_last_breeding(self.__elephant_id)
            self.__update_cw = 0
            self.__update_alive = 0
            print(self.__date, self.__last_breeding)

            deltawarning = None
            if delta < 0:
                deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This event precedes this elephant's birth.")
                self.__xdate = 0
            elif delta > 100 and self.__solved == 'N':
                deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This event occurs when the elephant is over 100 years. Please verify input.")
                self.__xdate = 0

            else:
                if self.__event_class == 'death':
                    if self.__date_of_death is not None:
                        deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This elephant is already died on "+datetime.strftime(date_of_death, "%Y-%m-%d")+". You can't kill what's already dead.")
                        self.__xdate = 0
                    elif (self.__date - self.__last_alive).days < 0:
                        deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This elephant was seen alive later, on "+datetime.strftime(self.__last_alive, "%Y-%m-%d")+", check your input.")
                        self.__xdate = 0
                    elif (self.__date - self.__last_breeding).days < 0:
                        deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This elephant had an offspring on "+datetime.strftime(self.__last_breeding, "%Y-%m-%d")+", check your input.")
                        self.__xdate = 0
                    else:
                        print("Chronologies seem to match - updating database")
                        self.__update_alive = 1
                        self.__xdate = 1

                elif self.__event_class in ('capture','accident','health','alive','metadata'):
                    if self.__date_of_death is not None and (self.__date - self.__date_of_death).days > 0:
                        deltawarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This elephant was already six feet under by then. Please check your input.")
                        self.__xdate = 0
                    elif self.__date_of_death is None and self.__db_alive == 'UKN':
                            #If the event is less than 5 years ago and the elephant is now less than 90 years old, it switches to 'alive'
                            if ((datetime.now().date()-self.__date).days / 365.25) <= 5 and ((datetime.now().date()-self.__db_birth).days / 365.25) <= 90:
                                print("Updating status to 'alive' in the database.")
                                self.__update_alive = 2
                                self.__xdate = 1
                            else:
                                print("Chronologies seem to match.")
                                self.__xdate = 1
                    else:
                        print("Chronologies seem to match.")
                        self.__xdate = 1


            if deltawarning is not None:
                self.warnings.append(deltawarning)

            captwarning = None
            if self.__event_class == 'capture':
                if self.__db_cw == 'captive':
                    captwarning = ("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: You can't register a capture event for a captive-born elephant.")
                    self.__xcw = 0
                elif self.__db_cw == 'UKN':
                    print("We didn't know this was a wild elephant - updating database.")
                    self.__xcw=1
                    self.__update_cw = 1
                elif self.__db_cw == 'wild':
                    print("This elephant is indeed registered as wild-caught. No problem.")
                    self.__xcw = 1
            if captwarning is not None:
                self.warnings.append(captwarning)

            if self.__xdate != 0 and self.__xcw !=0:
                self.__checked = 1

    ################################################################################
    ## 'write' function writes out the sql instert statement or an error          ##
    ################################################################################

    def write(self,db):
        self.__db = db
        self.out = []

        # This is done here to prevent incrementation if source() is repeated by mistake
        if self.__sourced == 0:
            if self.__xeleph == 0:
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+64
                    self.warnings.append("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This elephant could not be found in the database.")
            elif self.__xevent == 0:
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+128
                    self.warnings.append("[Elephant "+str(self.__num)+"/"+str(self.__calf_num)+"]: This event type is not yet registered the database.")

        elif self.__sourced == 1:
            if self.__toggle_write_flag == 0:
                self.flag = self.flag+8

        if self.__checked == 1:
            #If we need to update the "cw" or "alive" flags in the elephants table
            if self.__update_cw == 0:
                wcw = None
            elif self.__update_cw == 1:
                wcw = 'wild'
            if self.__update_alive == 0:
                walive = None
            elif self.__update_alive == 1:
                walive = 'N'
            elif self.__update_alive == 2:
                walive = 'Y'

            out = []
            if wcw is not None or walive is not None:
                update = self.__db.update_elephant(id=self.__elephant_id, cw=wcw, alive=walive)
                self.out.append(update)
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+4

            insert = self.__db.insert_event(self.__elephant_id, self.__date, self.__loc, self.__code_id)
            self.out.append(insert)
            if self.__toggle_write_flag == 0:
                self.flag = self.flag+2

        elif self.__checked == 0 and self.__sourced == 2:
            if self.__xdate == 1 and self.__xcw == 0:
                conflicts = 'origin'
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+32
            elif self.__xdate == 0 and self.__xcw == 1:
                conflicts = 'date'
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+16
            else:
                conflicts = 'date and origin'
                if self.__toggle_write_flag == 0:
                    self.flag = self.flag+48
            out = "[Conflict] You need to solve conflicts for "+conflicts+" for elephant "+str(self.__num)+"/"+str(self.__calf_num)+" before proceeding."
            self.warnings.append(out)

        for w in self.warnings:
            self.out.append(w)

        self.__toggle_write_flag = 1
        # In all cases, the output is the input row, the flag, and the result line (warning or SQL operation)
        output_row = [self.__num, self.__calf_num, self.__date, self.__loc, self.__code, self.flag, self.out]
        return(output_row)
