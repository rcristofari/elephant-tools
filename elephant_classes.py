import pymysql as pms
from datetime import datetime
import string
import numpy as np
import re

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                               CLASS "MYSQLCONNECT"                         ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class mysqlconnect:

    def __init__(self, usr, pwd, host, db):
        self.__usr=usr
        self.__pwd=pwd
        self.__host=host
        self.__db=db    
        self.__db = pms.connect(self.__host, self.__usr, self.__pwd, self.__db)
        self.__cursor = self.__db.cursor()

    def __del__(self):
        self.__db.close()
        print("Connexion closed")

    def stamp(self, details=''):
    # will make a timestamp for all the operations of the sessions and return an entry for the commit table
        # Make the stamp
        sql = "SELECT NOW();"
        self.__cursor.execute(sql)
        t = str(self.__cursor.fetchall()[0][0])
        self.__stamp = re.sub('\ |\-|\:', '', t)

        #Check the latest commit ID
        sql = "SELECT max(id) FROM commits;"
        self.__cursor.execute(sql)
        last_id = self.__cursor.fetchall()[0][0]
        self.__i = last_id + 1
        statement = "INSERT INTO commits (stamp, user, details) VALUES (%s, %s, %s);" % (self.__stamp, "'"+self.__usr+"'", "'"+details+"'")
        return(statement)

    def fulleleph(self, num):
        self.__num=num
        sql = "SELECT * FROM elephants WHERE num = %s;" % (self.__num)
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            if results:
                return(results[0])
        except Exception as ex: ##MAKE THIS MORE GENERAL (every exception?)
            print(ex)
            print ("Error: unable to fetch data")


    def coreleph(self, num):
        self.__num=num
        sql = "SELECT id, sex, birth, alive FROM elephants WHERE num = %s;" % (self.__num)
        try:
            self.__cursor.execute(sql)
            return(self.__cursor.fetchall()[0])
        except:
            print ("Error: unable to fetch elephant data.")


    def pedigree(self, id_1, id_2):     
        self.__db_id1 = id_1
        self.__db_id2 = id_2
        sql_1 = "SELECT * FROM pedigree WHERE elephant_1_id = %s AND elephant_2_id = %s;" % (self.__db_id1, self.__db_id2) #__rel_1 : eleph 1 first
        sql_2 = "SELECT * FROM pedigree WHERE elephant_1_id = %s AND elephant_2_id = %s;" % (self.__db_id2, self.__db_id1) #__rel_2 : eleph 2 first
        
        try:
            self.__cursor.execute(sql_1)
            self.__rel_1 = self.__cursor.fetchall()[0]
            self.__cursor.execute(sql_2)
            self.__rel_2 = self.__cursor.fetchall()[0]
            return(self.__rel_1, self.__rel_2)
        except:
            pass  

    def mother(self, num):
        self.__num=num
        sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
        self.__cursor.execute(sql)
        id1 = self.__cursor.fetchall()[0][0]
        sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_2_id WHERE pedigree.elephant_1_id = %s AND rel = 'mother';" % (id1)
        self.__cursor.execute(sql)
        return(self.__cursor.fetchall()[0][0])

    def insert_eleph(self,num,name,sex,birth,cw,caught,camp,alive):
        if self.__i == None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
            break
        
        q = "'"
        if name == None:
            name = 'null'
        else:
            name = q+name+q
        if sex == None:
            sex = "'UKN'"
        else:
            sex = q+sex+q
        if birth == None:
            birth = 'null'
        else:
            birth = q+str(birth)+q
        if cw == None:
            cw = "'UKN'"
        else:
            cw = q+cw+q
        if caught == None:
            caught = 'null'
        else:
            caught = q+caught+q 
        if camp == None:
            camp = 'null'
        else:
            camp = q+camp+q
            
        if alive == None:
            alive = "'UKN'"
        else:
            alive = q+alive+q
        statement = "INSERT INTO elephants (num, name, sex, birth, cw, age_capture, camp, alive, commits) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);" % (self.__num, name, sex, birth, cw, caught, camp, alive, self.__i)
        return(statement)

    def update_eleph(self, name, sex, birth, cw, caught, camp, alive, commits, id):
        if self.__i == None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
            break

        q = "'"
        if name == None:
            name = 'null'
        else:
            name = q+name+q
        if sex == None:
            sex = "'UKN'"
        else:
            sex = q+sex+q
        if birth == None:
            birth = 'null'
        else:
            birth = q+str(birth)+q
        if cw == None:
            cw = "'UKN'"
        else:
            cw = q+cw+q
        if caught == None:
            caught = 'null'
        else:
            caught = q+caught+q 
        if camp == None:
            camp = 'null'
        else:
            camp = q+camp+q
            
        if alive == None:
            alive = "'UKN'"
        else:
            alive = q+alive+q
        if commits != 'null':
            newcommits = (q+commits+','+str(self.__i)+q)
        else:
            newcommits = (q+str(self.__i)+q)

        statement = "UPDATE elephants SET name=%s, sex=%s, birth=%s, cw=%s, age_capture=%s, camp=%s, alive=%s, commits=%s WHERE id=%s;" % (name, sex, birth, cw, caught, camp, alive, newcommits, id)
        print(statement)
        return(statement)                

    def insert_pedigree(pedigree):
        

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "ELEPHANT"                              ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class elephant:

    def __init__(self, num, name=None, sex=None, birth=None, cw=None, caught=None, camp=None, alive=None, solved='N'):

# Some execution parameters
        #Is the input file a conflict resolution (Y/N)? If Y, name and camp will be appended.
        self.__solved=solved
        self.__interactive=1 # Not implemented so far
        
# Non-prefixed parameters describe user input
        self.__num=num #kept private since it is the primary key for the input. Has a getter function.
        if name != None:
            self.name=string.capwords(name)
        else:
            self.name=name
        self.sex=sex
        if birth != None:
            self.birth=datetime.strptime(birth, '%Y-%m-%d').date()
        else:
            self.birth=birth
        self.cw=cw
        if caught == '':
            self.caught = None
        else:
            self.caught=caught
        if camp != None:
            self.camp=string.capwords(camp)
        else:
            self.camp=camp
        self.alive=alive

# Prefixed parameters describe database content. They are private and are not modified (declared here for reference only)
        self.__db_id = None
        self.__db_num = None
        self.__db_name = None
        self.__db_sex = None
        self.__db_birth = None
        self.__db_cw = None
        self.__db_caught = None
        self.__db_camp = None
        self.__db_alive = None
        self.__db_commits = None
        
# These variables pass the state of each operation to the next
        self.__sourced=0
        self.__checked=0
        self.status=None #Result of the check() function
        self.statement=None #SQL statement issued by the write() function
        
# __x variables describe state of the comparison db/input
        self.__xname=0
        self.__xsex=0
        self.__xbirth=0
        self.__xcw=0
        self.__xcaught=0
        self.__xcamp=0
        self.__xalive=0

#Getter function for some private variables that could be useful in scripting
    def get_num(self):
        return(self.__num)
    def get_solved(self):
        return(self.__solved)
    def set_solved(solved):
        self.__solved=solved

################################################################################
## 'source' function reads the elephant from the database if it exists        ##
################################################################################

    def source(self,db):
        self.__db=db #db is a database connection object of class elephant.mysqlconnect()
        self.__sourced = 0
        results = self.__db.fulleleph(self.__num)
            
        if results == None:
            self.__sourced = 2
            print("Elephant number", self.__num, "is absent from the database.")

        else:
            self.__sourced = 1

            self.__db_id = results[0]
            self.__db_num = results[1]
            if results[2] != None:
                self.__db_name = string.capwords(results[2])
            self.__db_sex = results[3]
            self.__db_birth = results[4]
            self.__db_cw = results[5]
            self.__db_caught = results[6]
            if results[7] != None:
                self.__db_camp = string.capwords(results[7])
            self.__db_alive = results[8]
            self.__db_commits = results[9]
            if self.__db_commits == None:
                self.__db_commits = 'null'
            
            print ("\nThis elephant is present in the database as:\nIndex:\t\t", self.__db_id, "\nNumber:\t\t", self.__db_num, "\nName:\t\t",  self.__db_name, "\nSex:\t\t",  self.__db_sex, "\nBirth date:\t",  self.__db_birth, ", ",  self.__db_cw, "\nAge at capture:\t",  self.__db_caught, "\nCamp:\t\t", self.__db_camp,"\nAlive:\t\t", self.__db_alive, sep='')
            return(self.__db_id, self.__db_num, self.__db_name, self.__db_sex, self.__db_birth, self.__db_cw, self.__db_caught, self.__db_camp, self.__db_alive, self.__db_commits)

################################################################################
## 'check' function, checks consistency between database and new data         ##
################################################################################
        
# Outcome code for __x variables: 0= conflict, 1 = matching, 2 = update database,
# 3 = still missing, 4 = already in database, no input.

    def check(self):
        if self.__sourced == 0:
            print("\nCheck: You must source this elephant first using elephant.source().")
        elif self.__sourced == 2:
            print("This elephant is not in the database, you can proceed to write() directly.")
        elif self.__sourced == 1:
            print("\nCONSISTENCY CHECK:")
            print ("This elephant is specified here as:\nNumber:\t\t", self.__num, "\nName:\t\t",  self.name, "\nSex:\t\t",  self.sex, "\nBirth date:\t",  self.birth, ", ",  self.cw, "\nAge at capture:\t",  self.caught, "\nCamp:\t\t", self.camp,"\nAlive:\t\t", self.alive, sep='')

            print("\nOperations for elephant number ", self.__num, ":", sep='')

############ Name
            
            if self.name != None and self.name in self.__db_name: #Partial match since there could be multiple names in the database
                self.__xname = 1
                self.name = self.__db_name #This is in case that name is a subset of database name
                print("Names match.")

            elif self.__db_name == None and self.name != None:
                self.__xname = 2
                print("No known name yet, updating database.")

            elif self.__db_name == None and self.name == None:
                self.__xname = 3
                print("Name is still missing")

            elif self.__db_name != None and self.name == None:
                self.__xname = 4
                self.name = self.__db_name
                print("This elephant is known in database as ", self.__db_name, " - no change.", sep='')

            else :
                self.__xname = 0
                if self.__solved == 'N':
                    print("Different name in database. You need to solve the conflict manually.")
                if self.__solved =='Y':
                    self.name = self.__db_name + ", " + self.name
                    self.__xname = 2   ###JUST CHANGED FROM 1 TO 2
                    print("Alias name appended to database")
 
############ Sex
                    
            if self.sex == self.__db_sex:
                self.__xsex = 1
                print("Sexes match.")

            elif self.__db_sex == 'UKN' and self.sex != None:
                self.__xsex = 2
                print("No known sex yet, updating database.")

            elif self.__db_sex == 'UKN' and self.sex == None:
                self._xsex = 3
                self.sex = self.__db_sex
                print("Sex is still missing")

            elif self.__db_sex != 'UKN' and self.sex == None:
                self.__xsex = 4
                self.sex = self.__db_sex
                if self.__db_sex == 'M':
                    __strsex = 'male'
                elif self.__db_sex == 'F':
                    __strsex = 'female'
                print("It is known in database as a ", __strsex, " - no change.", sep='')

            else :
                self.__xsex = 0
                if self.__interactive == 1:
                    print("Different sex in database. You need to solve the conflict manually.")

############ Birth date

            if self.birth == self.__db_birth and self.birth != None:
                self.__xbirth = 1
                print("Birth dates match.")

            elif self.__db_birth == None and self.birth != None:
                self.__xbirth = 2
                print("No known birth date yet, updating database.")

            elif self.__db_birth == None and self.birth == None:
                self.__xbirth = 3
                print("Birth date is still missing")

            elif self.__db_birth != None and self.birth == None:
                self.__xbirth = 4
                self.birth = self.__db_birth
                born = self.__db_birth
                now = datetime.now().date()
                age = round(((now - born).days / 365.25))
                if self.alive == 'Y' or self.__db_alive == 'Y':
                    print("Birth data known as ", self.__db_birth, " (", age, " years old) - no change.", sep='')
                else:
                    print("Birth data known as ", self.__db_birth, " (", age, " years ago) - no change.", sep='')

            else :
                self.__xbirth = 0
                if self.__interactive == 1:
                    print("Different birth date in database. You need to solve the conflict manually.")

##age at capture first check

############ Wild or captive

            if self.cw == self.__db_cw:
                self.__xcw = 1
                print("Captive/wild matches.")

            elif self.__db_cw == 'UKN' and self.cw != None:
                self.__xcw = 2
                print("Unknown whether captive or wild so far, updating database.")

            elif self.__db_cw == 'UKN' and self.cw == None:
                self.__xcw = 3
                self.cw = self.__db_cw
                print("Origin is still missing")

            elif self.__db_cw != 'UKN' and self.cw == None:
                self.__xcw = 4
                self.cw = self.__db_cw
                print("In the database, it is born ", self.__db_cw, " - no change.", sep='')

            else :
                self.__xcw = 0
                if self.__interactive == 1:
                    print("Different origin in database. You need to solve the conflict manually.")

############ Age at capture

            if self.cw == 'captive' or self.cw == 'UKN' or self.__db_cw == 'captive' or self.__db_cw =='UKN':

                if self.caught == self.__db_caught and self.caught != None:
                    self.__xcaught = 0
                    print("Ages at capture match, but this elephant is registered as captive born. Check database and input data.")

                elif self.__db_caught == None and self.caught != None:
                    self.__xcaught = 0                   
                    print("No known age at capture yet, but this elephant is registered as captive born. Check your data.")

                elif self.__db_caught == None and self.caught == None:
                    self.__xcaught = 1
                    print("Age at capture is still missing, and this elephant is registered as captive born. All good.")

                elif self.__db_caught != None and self.caught == None:
                    self.__xcaught = 0
                    self.caught = self.__db_caught
                    print("In the database, it was captured at age ", self.__db_cw, " ,  but this elephant is registered as captive born. Check the database.", sep="")

                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        print("Different age at capture in database. You need to solve the conflict manually.")

            elif self.cw == 'wild' or self.__db_cw == 'wild':
                
                if self.caught == self.__db_caught and self.caught != None:
                    self.__xcaught = 1
                    print("Ages at capture match.")

                elif self.__db_caught == None and self.caught != None:
                    self.__xcaught = 2                   
                    print("No known age at capture yet, updating database.")

                elif self.__db_caught == None and self.caught == None:
                    self.__xcaught = 3
                    print("Age at capture is still missing")

                elif self.__db_caught != None and self.caught == None:
                    self.__xcaught = 4
                    self.caught = self.__db_caught
                    print("In the database, it was captured at age ", self.__db_cw, " - no change.", sep="")

                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        print("Different age at capture in database. You need to solve the conflict manually.")


############ Camp

            if self.camp != None and self.camp in self.__db_camp:
                self.__xcamp = 1
                self.camp = self.__db_camp
                print("Camps match.")

            elif self.__db_camp == None and self.camp != None:
                self.__xcamp = 2
                print("No known camp yet, updating database.")

            elif self.__db_camp == None and self.camp == None:
                self.__xcamp = 3
                print("Camp is still missing")

            elif self.__db_camp != None and self.camp == None:
                self.__xcamp = 4
                self.camp = self.__db_camp
                print("In the database, it comes from ", self.__db_camp, " - no change.", sep='')

            else :
                self.__xcamp = 0
                if self.__solved == 'N':
                    print("Different camp in database. You need to solve the conflict manually.")
                if self.__solved =='Y':
                    self.camp = self.__db_camp + ", " + self.camp
                    self.__xcamp = 1
                    print("New camp appended to database")

############ Alive or dead

            if self.alive == self.__db_alive:
                self.__xalive = 1
                print("Living status matches.")

            elif self.__db_alive == 'UKN' and self.alive != None:
                self.__xalive = 2
                if self.alive == 'Y':
                    print("We were not sure if was alive, updating database.")
                elif self.alive == 'N':
                    print("We didn't know it was dead, updating database & requiescat in pace.")

            elif self.__db_alive == 'UKN' and self.alive == None:
                self.__xalive = 3
                self.alive = self.__db_alive
                print("Still unknow whether alive or not.")

            elif self.__db_alive != 'UKN' and self.alive == None:
                self.__xalive = 4
                self.alive = self.__db_alive
                if self.__db_alive == 'Y':
                    print("In the database, it is alive - no change")
                elif self.__db_alive == 'N':
                    print("In the database, it is dead - no change, & requiescat in pace.")

            else :
                self.__xalive = 0
                if self.__interactive == 1:
                    print("Different living status in database. You need to solve the conflict manually.")

############ Check the consistency of birth date and living status

            if self.birth != None:
                now = datetime.now().date()
                age = ((now - self.birth).days) / 365.25
                if self.alive == 'Y' and age > 90:
                    print("This elephant is now over 90 years old. Are you sure it is still alive?")
                    self.__xalive = 0
                elif age < 0:
                    print("This elephant is born in the future. We're doing science on the edge here.")
                    self.__xalive = 0

#Here, do the final fusion of data, and give an outcome (write to database or write out for manual conflict resolution)
        self.status = (self.__xname, self.__xsex, self.__xbirth, self.__xcw, self.__xcaught, self.__xcamp, self.__xalive)
        self.__checked = 1
        
        return(self.__num, self.name, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.__db_commits)

################################################################################
## 'write' function writes out an sql statement to insert/update the elephant ##
################################################################################
    
    def write(self, db):
        self.__db=db

        #The elephant must have been checked in the database
        if self.__sourced == 0:
            print("\nWrite: You must check that the elephant is absent from the database first.")
        
        #If this elephant is not in the database yet, write an insert statement (consistency of data assumed).
        elif self.__sourced == 2:

            #this is outsourced to mysqlconnect
            out = self.__db.insert_eleph(self.__num, self.name, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive)
            return(out)
        
        #If the elephant has been checked and there is no conflict, write an update statement.
        elif self.__checked == 1 and any(x == 0 for x in self.status) == False:
            if all(x == 1 for x in self.status): #All fields are matching, no update
                pass
            else:
                #this is outsourced to mysqlconnect
                out = self.__db.update_eleph(self.name, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.__db_commits, self.__db_id)
                return(out)
        
        #If there is a pending conflict, we write out a csv-type line.
        else:
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            f = ('name','sex','birth','cw','age of capture','camp','alive')
            conflicts = str()
            for x in i:
                conflicts = conflicts+f[x]
            print("\nYou need to solve conflicts for:", conflicts)

            return(self.__num, self.name, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive)


            ##Add a light check here to see that a captive elephant has no age at capture.
            
   ##########################################################################
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

    def __init__(self, eleph_1=None, eleph_2=None, rel=None, coef=None):

# Non-prefixed parameters describe user input       
        self.eleph_1=eleph_1
        self.eleph_2=eleph_2
        self.rel=rel
        self.coef=coef

# Prefixed parameters describe database content
        self.__db_id=None
        self.__db_id1=None
        self.__db_id2=None
        self.__db_eleph_1=None
        self.__db_eleph_2=None
        self.__db_rel_1=None
        self.__db_rel_2=None
        self.__db_coef_1=None
        self.__db_coef_2=None
        self.__db_rel_id=None
        self.__rel_1=None
        self.__rel_2=None
        self.__rel_fwd=None
        self.__rel_rev=None
        
# These variables pass the state of each operation to the next
        self.__sourced=0
        self.__checked=0
        self.status=None #Result of the check() function
        self.statement=None #SQL statement issued by the write() function

# __x variables describe state of the comparison db/input
        self.__x1=None
        self.__x2=None
        self.__xrel=None
        self.__xcoef=None
        self.__xsex=None
        self.__xbirth=None

################################################################################
## 'source' function reads the pedigree from the database if it exists        ##
################################################################################

    def source(self, db):

        self.__db=db

        self.__db_eleph_1 = self.__db.coreleph(self.eleph_1)
        self.__db_eleph_2 = self.__db.coreleph(self.eleph_2)
        self.__db_id1 = self.__db_eleph_1[0]
        self.__db_id2 = self.__db_eleph_2[0]

        self.__rel_1 = self.__db.pedigree(self.__db_id1, self.__db_id2)[0]
        self.__rel_2 = self.__db.pedigree(self.__db_id1, self.__db_id2)[1]

        #If the relationship already exists, check exact consistency of the entry:
            
        if self.__rel_1 != None and self.__rel_2 != None:

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

                    self._sourced = 1  
                    #Testing that the age difference is at least 7 years (should be tuned better).
                    #In case of problem, self.__sourced reverts to 0.
                    #There's probably a more elegant way to do that.
                
                    if self.__rel_1[4] == 'mother':
                        if delta > -7:
                            self._sourced = 0
                            print("Mother too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -90:
                            self._sourced = 0
                            print("Mother too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    if self.__rel_2[4] == 'mother':
                        if delta < 7:
                            self._sourced = 0
                            print("Mother too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 90:
                            self._sourced = 0
                            print("Mother too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_1[4] == 'father':
                        if delta > -7:
                            self._sourced = 0
                            print("Father too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -90:
                            self._sourced = 0
                            print("Father too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_2[4] == 'father':
                        if delta < 7:
                            self._sourced = 0
                            print("Father too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 90:
                            self._sourced = 0
                            print("Father too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_1[4] == 'offspring':
                        if delta < 7:
                            self._sourced = 0
                            print("Parent too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 90:
                            self._sourced = 0
                            print("Parent too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_2[4] == 'offspring':
                        if delta > -7:
                            self._sourced = 0
                            print("Parent too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -90:
                            self._sourced = 0
                            print("Parent too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass      

            if self._sourced == 1:
                print("This relationship is already correctly entered in the database, nothing to do.")
                
            else:
                print("This relationship is present but incorreclty entered in the database.\nCheck it manually (relationship id: ",
                      self.__rel_1[1], ", elephants ", self.__db_eleph_1[0], " and ", self.__db_eleph_2[0], ").", sep="")

        elif self.__rel_1 == None and self.__rel_2 == None:
            self.__sourced = 2
            print("This relationship is not in the database yet. You can proceed to check()")

################################################################################
## 'check' function, checks consistency between database and new data         ##
################################################################################

    def check(self):
        
        delta = (self.__db_eleph_2[2] - self.__db_eleph_1[2]).days / 365.25

        print("\nThe new relationship states that elephant ", self.eleph_1, " (", self.__db_eleph_1[1], "), born on ", self.__db_eleph_1[2],
              ", is the ", self.rel, " of elephant ", self.eleph_2, " (", self.__db_eleph_2[1], "), born on ", self.__db_eleph_2[2], ".\n", sep="")
        
        if self.__sourced == 0:
            print("\nCheck: You must source this relationship first using pedigree.source().")

        elif self.__sourced == 1:
            print("\nCheck: This relationship is already correctly entered in the database, nothing to do.")

        elif self.__sourced == 2:
            self.__checked = 1
            self.__xsex = 1
            self.__xbirth = 1
            
            if self.rel == 'mother': #eleph_1 must be a female, and older than self.eleph_2 (between 7 and 90 years age difference)
                if self.__db_eleph_1[1] != 'F':
                    self.__xsex = 0
                    self.__checked = 0
                    print("Not registered as female in the database, you cannot declare it as 'mother' here.")
                elif delta < 7:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Mother too young (", round(delta), " years old)", sep="")
                elif delta > 90:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Mother too old (", round(abs(delta)), " years old)", sep="")
                else:
                    pass
            
            elif self.rel == 'father': #eleph_1 must be a male, and older than self.eleph_2 (between 7 and 90 years age difference)
                if self.__db_eleph_1[1] != 'M':
                    self.__xsex = 0
                    self.__checked = 0
                    print("Not registered as male in the database, you cannot declare it as 'father' here.")
                elif delta < 7:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Father too young (", round(delta), " years old)", sep="")
                elif delta > 90:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Father too old (", round(abs(delta)), " years old)", sep="")
                else:
                    pass

            elif self.rel == 'offspring': #eleph_1 must be younger than self.eleph_2 (between 7 and 90 years age difference)
                if delta > -7:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Parent too young (", round(abs(delta)), " years old)", sep="")
                elif delta < -90:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Parent too old (", round(abs(delta)), " years old)", sep="")
                else:
                    pass

            else:
                pass

            if self.__checked == 1:
                print("The proposed relationship is consistent. You can proceed to pedigree.write().")
            else:
                print("There are inconsistencies in the proposed relationship. Check your input.")
                self.status = (self.__xsex, self.__xbirth)
                #The actual writing of error will be done by write()
                    

                #### si alive == F vérifier les dates ####

################################################################################
## 'write' function writes out two sql instert statements or an error         ##
################################################################################

    def write(self):

        db = pms.connect(self.__mysql_host, self.__mysql_usr, self.__mysql_pwd, self.__mysql_db)
        cursor = db.cursor()
        sql = "SELECT max(rel_id) FROM pedigree;"
        try:
            cursor.execute(sql)
            self.__last_id = cursor.fetchall()[0][0]+1
        except:
            Print("Unable to connect to database")
        q = "'"    
        if self.rel == "mother":
            self.__rel_fwd = q+"mother"+q
            self.__rel_rev = q+"offspring"+q
        elif self.rel == "father":
            self.__rel_fwd = q+"father"+q
            self.__rel_rev = q+"offspring"+q
        elif self.rel == "unknown":
            self.__rel_fwd = q+"unknown"+q
            self.__rel_rev = q+"unknown"+q
        elif self.rel == "offspring":
            if self.__db_eleph_2[1] == 'F':
                self.__rel_fwd = q+"offspring"+q
                self.__rel_rev = q+"mother"+q
            elif self.__db_eleph_2[1] == 'M':
                self.__rel_fwd = q+"offspring"+q
                self.__rel_rev = q+"father"+q
            else:
                self.__rel_fwd = q+"offspring"+q
                self.__rel_rev = q+"unknown"+q

        if self.coef == None:
            self.coef='null'
        else:
            self.coef=q+self.coef+q
            
        self.statement_1 = "INSERT INTO pedigree (rel_id, elephant_1_id, elephant_2_id, rel) VALUES (%s, %s, %s, %s, %s);" % (self.__last_id, self.__db_id1, self.__db_id2, self.__rel_fwd, self.coef)
        self.statement_2 = "INSERT INTO pedigree (rel_id, elephant_1_id, elephant_2_id, rel) VALUES (%s, %s, %s, %s, %s);" % (self.__last_id, self.__db_id2, self.__db_id1, self.__rel_rev, self.coef)

        if self.__checked == 1:
            return(self.statement_1, self.statement_2)

        elif self.__checked == 0:
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            f = ('sex','birth date')
            conflicts = str()
            for x in i:
                conflicts = conflicts+f[x]
            print("\nYou need to solve conflicts for:", conflicts, "\n")

            return(self.eleph_1, self.__db_eleph_1[1], self.__db_eleph_1[2], self.eleph_2, self.__db_eleph_2[1], self.__db_eleph_2[2])


   ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "EVENT"                                 ##
###                                                                          ###
 ##############################################################################
   ##########################################################################


    ##########################################################################
 ##############################################################################
###                                                                          ###
##                             CLASS "MEASURE"                                ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

# A measure object consists of fields
