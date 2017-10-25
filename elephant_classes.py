import pymysql as pms
from datetime import datetime
import string
import numpy as np
import re
import os

#A simple function for mysql queries:
def quote(string):
    return("'"+str(string)+"'")

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                               CLASS "MYSQLCONNECT"                         ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class mysqlconnect:

    def __init__(self, usr, pwd, host='localhost', db='mep'):
        self.__usr=usr
        self.__pwd=pwd
        self.__host=host
        self.__db=db
        self.__db = pms.connect(self.__host, self.__usr, self.__pwd, self.__db)
        self.__cursor = self.__db.cursor()

    def __del__(self):
        self.__db.close()
        print("Connexion closed")

################################################################################
## 'stamp' function                                                           ##
################################################################################

    def stamp(self, details=''):
    # will make a timestamp for all the operations of the sessions and return an entry for the commit table
        # Make the stamp
        sql = "SELECT NOW();"
        self.__cursor.execute(sql)
        t = str(self.__cursor.fetchall()[0][0])
        self.__stamp = re.sub('\ |\-|\:', '', t)

        #Check the latest commit ID
        sql = "SHOW TABLE STATUS LIKE 'commits';"
        self.__cursor.execute(sql)
        f = self.__cursor.fetchall()
        try:
            self.__i = f[0][10]
        except:
            print("Impossible to connect to database")

        #Get the running ID for measures
        sql = "SELECT MAX(measure_id) FROM measures;"
#        sql = "SHOW TABLE STATUS LIKE 'measures';"
        self.__cursor.execute(sql)
        f = self.__cursor.fetchall()
        try:
#            self.__max_measure_id = f[0][10]-1
            self.__max_measure_id = f[0][0]
        except:
            print("Impossible to connect to database")

        statement = "INSERT INTO commits (stamp, user, details) VALUES (%s, %s, %s);" % (self.__stamp, quote(self.__usr), quote(details))
        return(statement)

################################################################################
## 'get_stamp' function                                                       ##
################################################################################
# A getter function useful for the parse_output function
    def get_stamp(self):
        if self.__i is None:
            print("You must generate a stamp first using stamp()")
        else:
            return(self.__stamp)

################################################################################
## 'get_elephant' function                                                    ##
################################################################################

    def get_elephant(self, num=None, calf_num=None):
        self.__num=num
        self.__calf_num=calf_num
        if self.__num is not None:
            sql = "SELECT * FROM elephants WHERE num = %s;" % (self.__num)
        elif self.__num is None and self.__calf_num is not None:
            sql = "SELECT * FROM elephants WHERE calfnum = %s;" % (self.__calf_num) ##Will open to a problem when several calves have the same ID and no adult ID...fix by matching on dates
        else:
            print("Error: you need at least one identifier")
        try:
            self.__cursor.execute(sql)
            results = self.__cursor.fetchall()
            if results:
                return(results[0])
        except Exception as ex: ##MAKE THIS MORE GENERAL (every exception?)
            print(ex)
            print ("Error: unable to fetch data")

################################################################################
## 'get_pedigree' function                                                        ##
################################################################################

    def get_pedigree(self, id_1, id_2):
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

################################################################################
## 'get_mother' function                                                          ##
################################################################################

    def get_mother(self, num):
        self.__num=num
        sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
        self.__cursor.execute(sql)
        id1 = self.__cursor.fetchall()[0][0]
        sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_1_id WHERE pedigree.elephant_2_id = %s AND rel = 'mother';" % (id1)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return result[0][0]

################################################################################
## 'get_father' function                                                          ##
################################################################################

    def get_father(self, num):
        self.__num=num
        sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
        self.__cursor.execute(sql)
        id1 = self.__cursor.fetchall()[0][0]
        sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_1_id WHERE pedigree.elephant_2_id = %s AND rel = 'father';" % (id1)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return result[0][0]

################################################################################
## 'get_measure_code' function                                                          ##
################################################################################

    def get_measure_code(self, measure):
        self.__measure=measure
        sql = "SELECT id FROM measure_code WHERE code = %s" % (quote(self.__measure))
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'get_measure' function                                                    ##
################################################################################

    def get_measure(self, num, date, code):
        self.__num=num
        self.__date=date
        self.__code=code

        sql = "SELECT id FROM elephants WHERE num = %s;" % (self.__num)
        try:
            self.__cursor.execute(sql)
            self.__eleph_id = self.__cursor.fetchall()[0][0]
        except:
            print("This elephant is absent from the database")

        sql = "SELECT * FROM measures WHERE elephant_id = %s and date = %s and measure = %s;" % (quote(self.__eleph_id), quote(self.__date), self.__code)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            if result.__len__ == 1:
                return(result[0])
            else:
                return(result[0])
                print("More than one line corresponding to that measure. Check what is going on in the database")

################################################################################
## 'get_mean_measure' function                                                    ##
################################################################################

    def get_mean_measure(self, code):
        self.__code = code
        sql = "SELECT ROUND(AVG(value),2) FROM measures WHERE measure = %s;" % (self.__code)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'insert_elephant' function                                                    ##
################################################################################

    def insert_elephant(self,num,name,calf_num,sex,birth,cw,caught,camp,alive,research):
        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            if name is None:
                name = 'null'
            else:
                name = quote(name)
            if calf_num is None:
                calf_num = 'null'
            else:
                calf_num = quote(calf_num)
            if sex is None:
                sex = "'UKN'"
            else:
                sex = quote(sex)
            if birth is None:
                birth = 'null'
            else:
                birth = quote(str(birth))
            if cw is None:
                cw = "'UKN'"
            else:
                cw = quote(cw)
            if caught is None:
                caught = 'null'
            else:
                caught = quote(str(caught))
            if camp is None:
                camp = 'null'
            else:
                camp = quote(camp)
            if alive is None:
                alive = "'UKN'"
            else:
                alive = quote(alive)
            if research is None:
                research = "'N'"
            else:
                research = quote(research)
            statement = "INSERT INTO elephants (num, name, calf_num, sex, birth, cw, age_capture, camp, alive, research, commits) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);" % (self.__num, name, calf_num, sex, birth, cw, caught, camp, alive, research, self.__i)
            return(statement)

################################################################################
## 'update_elephant' function                                                    ##
################################################################################

    def update_elephant(self, num=None, name=None, calf_num=None, sex=None, birth=None, cw=None, caught=None, camp=None, alive=None, research=None, commits=None, id=None):
        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")

        else:
            fields = str()
            values = []
            if num is not None:
                num = quote(num)
                fields=fields+'num=%s, '
                values.append(num)

            if name is not None:
                name = quote(name)
                fields=fields+'name=%s, '
                values.append(name)

            if calf_num is not None:
                calf_num = quote(calf_num)
                fields=fields+'calf_num=%s, '
                values.append(calf_num)

            if sex is not None:
                sex = quote(sex)
                fields=fields+'sex=%s, '
                values.append(sex)

            if birth is not None:
                birth = quote(str(birth))
                fields=fields+'birth=%s, '
                values.append(birth)

            if cw is not None:
                cw = quote(cw)
                fields=fields+'cw=%s, '
                values.append(cw)

            if caught is not None:
                caught = quote(str(caught))
                fields=fields+'age_capture=%s, '
                values.append(caught)

            if camp is not None:
                camp = quote(camp)
                fields=fields+'camp=%s, '
                values.append(camp)

            if alive is not None:
                alive = quote(alive)
                fields=fields+'alive=%s, '
                values.append(alive)

            if research is not None:
                research = quote(research)
                fields=fields+'research=%s, '
                values.append(research)

            if commits is not None:
                newcommits = (quote(str(commits)+','+str(self.__i)))
                fields=fields+'commits=%s, '
                values.append(newcommits)
            else:
                newcommits = (quote(str(self.__i)))
                fields=fields+'commits=%s, '
                values.append(newcommits)

            values.append(id)
            values_t = tuple(values)
            f = fields.rstrip(', ')
            statement = str("UPDATE elephants SET "+f+" WHERE id=%s;") % (values_t)

            return(statement)

################################################################################
## 'insert_pedigree' function                                                 ##
################################################################################

    def insert_pedigree(self, id1, id2, rel_fwd, rel_rev, coef):
        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            sql = "SELECT max(rel_id) FROM pedigree;"
            try:
                self.__cursor.execute(sql)
                y = self.__cursor.fetchall()[0][0]
                if y is not None:
                    last_id = y+1
                else:
                    last_id = 1
            except:
                print("Unable to connect to database")

            statement_1 = "INSERT INTO pedigree (rel_id, elephant_1_id, elephant_2_id, rel, commits) VALUES (%s, %s, %s, %s, %s, %s);" % (last_id, id1, id2, rel_fwd, coef, quote(self.__i))
            statement_2 = "INSERT INTO pedigree (rel_id, elephant_1_id, elephant_2_id, rel, commits) VALUES (%s, %s, %s, %s, %s, %s);" % (last_id, id2, id1, rel_rev, coef, quote(self.__i))

            return(statement_1, statement_2)

################################################################################
## 'insert_measure' function                                                 ##
################################################################################

    def insert_measure(self, measure_id, elephant_id, date, measure_code_id, value, commits = None):

        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            if commits is not None:
                newcommits = (quote(str(commits)+','+str(self.__i)))
            else:
                newcommits = (quote(str(self.__i)))
            statement = "INSERT INTO measures (measure_id, elephant_id, date, measure, value, commits) VALUES (%s, %s, %s, %s, %s, %s);" % (quote(int(measure_id) + int(self.__max_measure_id)), elephant_id, quote(date), measure_code_id, value, newcommits)

            return(statement)

################################################################################
## 'insert_measure_code' function                                             ##
################################################################################

    def insert_measure_code(self, code, unit, descript, commits = None):

        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            if commits is not None:
                newcommits = (quote(str(commits)+','+str(self.__i)))
            else:
                newcommits = (quote(str(self.__i)))

            statement = "INSERT INTO measure_code (code, unit, descript, commits) VALUES (%s, %s, %s, %s);" % (quote(code), quote(unit), quote(descript), newcommits)

            return(statement)

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "ELEPHANT"                              ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class elephant: ##MAKE A __repr__ function !!

    def __init__(self, num=None, name=None, calf_num=None, sex=None, birth=None, cw=None, caught=None, camp=None, alive=None, research=None, solved='N'):

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
            self.caught=int(caught)
        else:
            self.caught = caught
        if camp is not None:
            self.camp=string.capwords(camp)
        else:
            self.camp=camp
        self.alive=alive
        self.research=research

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

# Getter function for some private variables that could be useful in scripting
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

        print("#########################################################")

        self.__db=db #db is a database connection object of class elephant.mysqlconnect()
        self.__sourced = 0

        if self.__num is not None:
            results = self.__db.get_elephant(num=self.__num)
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

            print ("\nThis elephant is present in the database as:\nIndex:\t\t", self.__db_id, "\nNumber:\t\t", self.__db_num, "\nName:\t\t",  self.__db_name,
                   "\nCalf number:\t", self.__db_calf_num, "\nSex:\t\t",  self.__db_sex, "\nBirth date:\t",  self.__db_birth, ", ",  self.__db_cw,
                   "\nAge at capture:\t",  self.__db_caught, "\nCamp:\t\t", self.__db_camp,"\nAlive:\t\t", self.__db_alive,"\nResearch:\t", self.__db_research, sep='')

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
        elif self.__sourced == 1:
            print("\nCONSISTENCY CHECK:")
            print ("This elephant is specified here as:\nNumber:\t\t", self.__num, "\nName:\t\t",  self.name,
            "\nCalf number:\t", self.calf_num, "\nSex:\t\t",  self.sex, "\nBirth date:\t",  self.birth, ", ",  self.cw,
              "\nAge at capture:\t",  self.caught, "\nCamp:\t\t", self.camp,"\nAlive:\t\t", self.alive, "\nResearch:\t", self.research, sep='')

            print("\nOperations for elephant number ", self.__num, ":", sep='')

############ Num and calf_num checked together (inter-dependent)
            if self.__num is not None and self.__num == self.__db_num:
                self.__xnum = 1
                print("Numbers match.")
                if self.__db_calf_num == self.calf_num and self.calf_num is not None:
                    self.__xcalf_num = 1
                    print("Calf numbers match")
                elif self.calf_num is not None and self.__db_calf_num is None:
                    self.__xcalf_num = 2
                    print("Calf number was still unknown, updating database.")
                elif self.__db_calf_num is None and self.calf_num is None:
                    self.__xcalf_num = 3
                    print("Calf number is still missing.")
                elif self.__db_calf_num is not None and self.calf_num is None:
                    self.__xcalf_num = 4
                    print("Calf number entered as", self.__db_calf_num, "in the database, no change.")
                elif self.__db_calf_num is not None and self.calf_num is not None and self.calf_num != self.__db_calf_num:
                    self.__xcalf_num = 0
                    print("Calf numbers are conflicting. You need to solve that manually.")
            elif self.__num is None and self.__db_num is None:
                if self.calf_num is not None and self.calf_num == self.__db_calf_num:
                    self.__xnum = 3
                    self.__xcalf_num = 1
                    print("No adult number, but calf numbers match.")
                elif self.calf_num is not None and self.__db_calf_num is None: #this should not be possible in the present version.
                    self.__xnum = 3
                    self.__xcalf_num = 2
                    print("Calf number unknown so far, updating database.")
                elif self.calf_num is None and self.__db_calf_num is not None: #this should not be possible in the present version.
                    self.__xnum = 3
                    self.__xcalf_num = 4
                    print("Calf number entered as", self.__db_calf_num, "in the database, no change.")
                elif self.calf_num is not None and self.calf_num != self.__db_calf_num:
                    self.__xnum = 3
                    self.__xcalf_num = 0
                    print("Calf numbers do not match (", self.calf_num, " here, ", self.__db_calf_num, " in the db)", sep="")
                elif self.calf_num is None and self.__db_calf_num is None: #this should not be possible in the present version.
                    self.__xnum = 0
                    self.__xcalf_num = 0
                    print("You need at least an adult or a calf number.")
            elif self.__num is not None and str(self.__num) != str(self.__db_num): #Impossible in the current version (match priority to num) but if later on: this means the match has been made on calf_num, so the case is clear on that side.
                if self.calf_num == self.__db_calf_num: #just a check so far, but later on there may be research by birth date.
                    self.__xnum = 0
                    self.__xcalf_num = 1
                    print("Adult numbers do not match. Please check the input.")
            #This is a slightly complicated case: we provided a num and a calf num, but fell back on calf num because num was absent. Not possible with the current version yet.
            elif self.calf_num is not None and self.__db_calf_num is None: #this means the match has been made on calf_num, so the case is clear on that side.
                if self.calf_num == self.__db_calf_num: #just a check so far, but later on there may be research by birth date.
                    self.__xnum = 2
                    print("Adult number was still unknown, updating database.")

############ Name

            if self.name is not None  and self.__db_name is not None and self.name in self.__db_name: #Partial match since there could be multiple names in the database
                self.__xname = 1
                self.name = self.__db_name #This is in case that name is a subset of database name
                print("Names match.")
            elif self.__db_name is None and self.name is not None:
                self.__xname = 2
                print("No known name yet, updating database.")
            elif self.__db_name is None and self.name is None:
                self.__xname = 3
                print("Name is still missing")
            elif self.__db_name is not None and self.name is None:
                self.__xname = 4
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
            elif self.__db_sex == 'UKN' and self.sex is not None:
                self.__xsex = 2
                print("No known sex yet, updating database.")
            elif self.__db_sex == 'UKN' and self.sex is None:
                self._xsex = 3
                self.sex = self.__db_sex
                print("Sex is still missing")
            elif self.__db_sex != 'UKN' and self.sex is None:
                self.__xsex = 4
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

            if self.birth == self.__db_birth and self.birth is not None:
                self.__xbirth = 1
                print("Birth dates match.")
            elif self.__db_birth is None and self.birth is not None:
                self.__xbirth = 2
                print("No known birth date yet, updating database.")
            elif self.__db_birth is None and self.birth is None:
                self.__xbirth = 3
                print("Birth date is still missing")
            elif self.__db_birth is not None and self.birth is None:
                self.__xbirth = 4
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

############ Wild or captive

            if self.cw == self.__db_cw:
                self.__xcw = 1
                print("Captive/wild matches.")
            elif self.__db_cw == 'UKN' and self.cw is not None:
                self.__xcw = 2
                print("Unknown whether captive or wild so far, updating database.")
            elif self.__db_cw == 'UKN' and self.cw is None:
                self.__xcw = 3
                self.cw = self.__db_cw
                print("Origin is still missing")
            elif self.__db_cw != 'UKN' and self.cw is None:
                self.__xcw = 4
                print("In the database, it is born ", self.__db_cw, " - no change.", sep='')
            else:
                self.__xcw = 0
                if self.__interactive == 1:
                    print("Different origin in database. You need to solve the conflict manually.")

############ Age at capture

            if self.cw == 'captive' or self.cw == 'UKN' or self.__db_cw == 'captive' or self.__db_cw =='UKN':
                if self.caught == self.__db_caught and self.caught is not None:
                    self.__xcaught = 0
                    print("Ages at capture match, but this elephant is registered as captive born. Check database and input data.")
                elif self.__db_caught is None and self.caught is not None:
                    self.__xcaught = 0
                    print("No known age at capture yet, but this elephant is registered as captive born. Check your data.")
                elif self.__db_caught is None and self.caught is None:
                    self.__xcaught = 1
                    print("Age at capture is still missing, and this elephant is registered as captive born. All good.")
                elif self.__db_caught is not None and self.caught is None:
                    self.__xcaught = 0
                    self.caught = self.__db_caught
                    print("In the database, it was captured at age ", self.__db_cw, " ,  but this elephant is registered as captive born. Check the database.", sep="")
                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        print("Different age at capture in database. You need to solve the conflict manually.")

            elif self.cw == 'wild' or self.__db_cw == 'wild':
                if self.caught == self.__db_caught and self.caught is not None:
                    self.__xcaught = 1
                    print("Ages at capture match.")
                elif self.__db_caught is None and self.caught is not None:
                    self.__xcaught = 2
                    print("No known age at capture yet, updating database.")
                elif self.__db_caught is None and self.caught is None:
                    self.__xcaught = 3
                    print("Age at capture is still missing")
                elif self.__db_caught is not None and self.caught is None:
                    self.__xcaught = 4
                    print("In the database, it was captured at age ", self.__db_cw, " - no change.", sep="")
                else :
                    self.__xcaught = 0
                    if self.__interactive == 1:
                        print("Different age at capture in database. You need to solve the conflict manually.")

############ Camp

            if self.camp is not None and self.__db_camp is not None and self.camp in self.__db_camp:
                self.__xcamp = 1
                self.camp = self.__db_camp
                print("Camps match.")
            elif self.__db_camp is None and self.camp is not None:
                self.__xcamp = 2
                print("No known camp yet, updating database.")
            elif self.__db_camp is None and self.camp is None:
                self.__xcamp = 3
                print("Camp is still missing")
            elif self.__db_camp is not None and self.camp is None:
                self.__xcamp = 4
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
            elif self.__db_alive == 'UKN' and self.alive is not None:
                self.__xalive = 2
                if self.alive == 'Y':
                    print("We were not sure if was alive, updating database.")
                elif self.alive == 'N':
                    print("We didn't know it was dead, updating database & requiescat in pace.")
            elif self.__db_alive == 'UKN' and self.alive is None:
                self.__xalive = 3
                print("Still unknown whether alive or not.")
            elif self.__db_alive != 'UKN' and self.alive is None:
                self.__xalive = 4
                if self.__db_alive == 'Y':
                    print("In the database, it is alive - no change")
                elif self.__db_alive == 'N':
                    print("In the database, it is dead - no change, & requiescat in pace.")
            else :
                self.__xalive = 0
                if self.__interactive == 1:
                    print("Different living status in database. You need to solve the conflict manually.")

############ Research elephant

            if self.research == self.__db_research and self.research is not None:
                self.__xresearch = 1
                print("Research status matches")
            elif self.research is not None and (self.__db_research is None or self.__db_research == 'N'):
                self.__xresearch = 2
                print("We didn't know that it was a research elephant, updating database.")
            elif self.research is None and self.__db_research is None:
                sef.__xresearch = 2
                self.research = 'N'
                print("No information, setting database to Not a research elephant.")
            elif self.research == 'N' and self.__db_research == 'Y':
                self.__xresearch = 4
                self.research = None
                print("If you wish to remove this elephant's research status, do it manually.")
            elif self.research == 'Y' and (self.__db_research == 'N' or self.__db_research is None):
                self.xresearch = 2
                print("Not yet a research elephant in the database, updating database.")
            elif self.research is None and self.__db_research is not None:
                self.xresearch = 4
                if self.__db_research == 'N':
                    print("In the database, it is not a research elephant - no change")
                elif self.__db_research == 'Y':
                    print("In the database, it is a research elephant - no change")

############ Check the consistency of birth date and living status

            if self.birth is not None:
                now = datetime.now().date()
                age = ((now - self.birth).days) / 365.25
                if self.alive == 'Y' and age > 90:
                    print("This elephant is now over 90 years old. Are you sure it is still alive?")
                    self.__xalive = 0
                elif age < 0:
                    print("This elephant is born in the future. We're doing science on the edge here.")
                    self.__xalive = 0

        print("\n#########################################################")

#Here, do the final fusion of data, and give an outcome (write to database or write out for manual conflict resolution)

        self.status = (self.__xnum, self.__xname, self.__xcalf_num, self.__xsex, self.__xbirth, self.__xcw, self.__xcaught, self.__xcamp, self.__xalive, self.__xresearch)
        self.__checked = 1

        return(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research, self.__db_commits)

################################################################################
## 'write' function writes out an sql statement to insert/update the elephant ##
################################################################################

    def write(self, db):

        self.__db=db
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

        #The elephant must have been checked in the database
        if self.__sourced == 0:
            print("\nWrite: You must check that the elephant is absent from the database first.")

        #If this elephant is not in the database yet, write an insert statement (consistency of data assumed).
        elif self.__sourced == 2 and self.__num is not None and self.birth is not None:
            #this is outsourced to mysqlconnect
            out = self.__db.insert_elephant(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research)
            return(out)

        #If the elephant has been checked and there is no conflict, write an update statement.
        elif self.__checked == 1 and any(x == 0 for x in self.status) == False:
            if all(x in (1,3,4) for x in self.status): #All fields are matching, no update
                pass
            else:
                #this is outsourced to mysqlconnect
                out = self.__db.update_elephant(wnum, wname, wcalf_num, wsex, wbirth, wcw, wcaught, wcamp, walive, wresearch, self.__db_commits, self.__db_id)
                return(out)

        #If there is a pending conflict, we write out a csv-type line.
        else:
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            f = ('num','name','calf_num','sex','birth','cw','age of capture','camp','alive','research')
            conflicts = ''
            for x in i:
                conflicts = conflicts+', '+f[x]
            c = conflicts.rstrip(', ')
            conflicts = c[2:]+"."
            if self.__sourced == 2:
                return("[Conflict] Elephant number "+str(self.__num)+" is not in the database yet, but you must provide at least number and birth date")
            elif self.__sourced != 2 and self.__num is not None:
                return("[Conflict] Elephant number "+str(self.__num)+": you need to solve conflicts for: "+conflicts)
            elif self.__sourced != 2 and self.__num is None:
                return("[Conflict] Calf number "+str(self.calf_num)+": you need to solve conflicts for: "+conflicts)

            #return(self.__num, self.name, self.calf_num, self.sex, self.birth, self.cw, self.caught, self.camp, self.alive, self.research)


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
        self.__db_eleph_1 = None
        self.__db_eleph_2 = None
        elephant_absent = 0

        try:
            el1 = self.__db.get_elephant(self.eleph_1)
            el2 = self.__db.get_elephant(self.eleph_2)
            self.__db_eleph_1 = []
            self.__db_eleph_2 = []
            for x in (0,4,5,9):
                self.__db_eleph_1.append(el1[x])
                self.__db_eleph_2.append(el2[x])
            self.__db_id1 = self.__db_eleph_1[0]
            self.__db_id2 = self.__db_eleph_2[0]

        except TypeError:
            print("Impossible to find elephants", self.eleph_1, "and/or", self.eleph_2, "in the database.")
            elephant_absent = 1

        if self.__db.get_pedigree(self.__db_id1, self.__db_id2):
            self.__rel_1 = self.__db.get_pedigree(self.__db_id1, self.__db_id2)[0]
            self.__rel_2 = self.__db.get_pedigree(self.__db_id1, self.__db_id2)[1]

        #If the relationship already exists, check exact consistency of the entry:

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

                    if self.__rel_1[4] == 'mother':
                        if delta > -10:
                            self.__sourced = 0
                            print("Mother too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -70:
                            self.__sourced = 0
                            print("Mother too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    if self.__rel_2[4] == 'mother':
                        if delta < 10:
                            self.__sourced = 0
                            print("Mother too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 10:
                            self.__sourced = 0
                            print("Mother too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_1[4] == 'father':
                        if delta > -10:
                            self.__sourced = 0
                            print("Father too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -70:
                            self.__sourced = 0
                            print("Father too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_2[4] == 'father':
                        if delta < 10:
                            self.__sourced = 0
                            print("Father too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 70:
                            self.__sourced = 0
                            print("Father too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_1[4] == 'offspring':
                        if delta < 10:
                            self.__sourced = 0
                            print("Parent too young (", round(abs(delta)), " years old)", sep="")
                        elif delta > 70:
                            self.__sourced = 0
                            print("Parent too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass
                    elif self.__rel_2[4] == 'offspring':
                        if delta > -10:
                            self.__sourced = 0
                            print("Parent too young (", round(abs(delta)), " years old)", sep="")
                        elif delta < -70:
                            self.__sourced = 0
                            print("Parent too old (", round(abs(delta)), " years old)", sep="")
                        else:
                            pass

            if elephant_absent == 1:
                self.__sourced = 0

            if self.__sourced == 1:
                print("This relationship is already correctly entered in the database, nothing to do.")

            else:
                print("This relationship is present but incorreclty entered in the database.\nCheck it manually (relationship id: ",
                      self.__rel_1[1], ", elephant ids ", self.__db_eleph_1[0], " and ", self.__db_eleph_2[0], ").", sep="")

        elif self.__rel_1 is None and self.__rel_2 is None and elephant_absent != 1:
            self.__sourced = 2
            print("This relationship is not in the database yet. You can proceed to check()")

################################################################################
## 'check' function, checks consistency between database and new data         ##
################################################################################

    def check(self):  ###CHECK THAT THIS ELEPHANT DOESN'T ALREADY HAVE A MOTHER/A FATHER!!!

        if self.__sourced == 0:
            print("\nCheck: This relationship is present in the database with an error. Please correct it manually")

        elif self.__sourced == 1:
            print("\nCheck: This relationship is already correctly entered in the database, nothing to do.")

        elif self.__sourced == 2:
            self.__checked = 1
            self.__xsex = 1
            self.__xbirth = 1

            delta = (self.__db_eleph_2[2] - self.__db_eleph_1[2]).days / 365.25

            print("\nThe proposed relationship states that elephant ", self.eleph_1, " (", self.__db_eleph_1[1], "), born on ", self.__db_eleph_1[2],
                    ", is the ", self.rel, " of elephant ", self.eleph_2, " (", self.__db_eleph_2[1], "), born on ", self.__db_eleph_2[2], ".\n", sep="")


            #Check that this elephant does not already have a father or mother.

            if self.rel == "mother": # elephant 2 should not already have a mother or a father.
                if self.__db.get_mother(self.eleph_2) is not None:
                    self.__checked = 0
                    print("Elephant ", self.eleph_2, " already has a registered mother (", self.__db.get_mother(self.eleph_2), ").", sep="")
            elif self.rel == "father":
                if self.__db.get_father(self.eleph_2) is not None:
                    self.__checked = 0
                    print("Elephant ", self.eleph_2, " already has a registered father (", self.__db.get_father(self.eleph_2), ").", sep="")


            if self.rel == 'mother': #eleph_1 must be a female, and older than self.eleph_2 (between 7 and 90 years age difference)
                if self.__db_eleph_1[1] != 'F':
                    self.__xsex = 0
                    self.__checked = 0
                    print("Not registered as female in the database, you cannot declare it as 'mother' here.")
                elif delta < 10:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Mother too young (", round(delta), " years old)", sep="")
                elif delta > 70:
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
                elif delta < 10:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Father too young (", round(delta), " years old)", sep="")
                elif delta > 70:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Father too old (", round(abs(delta)), " years old)", sep="")
                else:
                    pass

            elif self.rel == 'offspring': #eleph_1 must be younger than self.eleph_2 (between 7 and 90 years age difference)
                if delta > -10:
                    self.__xbirth = 0
                    self.__checked = 0
                    print("Parent too young (", round(abs(delta)), " years old)", sep="")
                elif delta < -70:
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
            self.coef='null'
        else:
            self.coef=quote(self.coef)

        if self.__checked == 1:
            out = self.__db.insert_pedigree(self.__db_id1, self.__db_id2, self.__rel_fwd, self.__rel_rev, self.coef)
            return(out)

        elif self.__checked == 0:
            status_array = np.array(self.status)
            conflicts_array = np.where(status_array == 0)
            i = tuple(map(tuple, conflicts_array))[0]
            f = ('sex','birth date')
            conflicts = str()
            for x in i:
                conflicts = conflicts+f[x]
            return("\n[Conflict] Elephant number " + self.eleph_1 + " and/or " + self.eleph_2 + ": you need to solve conflicts for:" + conflicts + "\n")

            #return(self.eleph_1, self.__db_eleph_1[1], self.__db_eleph_1[2], self.eleph_2, self.__db_eleph_2[1], self.__db_eleph_2[2])

    ##########################################################################
 ##############################################################################
###                                                                          ###
##                             CLASS "MEASURE"                                ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

#NEED TO ADD A DETECTION FOR REPLICATES IN THE READ MODULE (DON'T KNOW IF WE DO REPLICATES AT ALL?)

class measure:

    def __init__(self, num, date, measure_id, measure, value, replicate='N', solved = 'N'):
        self.__num=num
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
        self.__xval = 0
        self.__xeleph = 0
        self.__xrep = 1
        self.__sourced = 0
        self.__checked = 0

################################################################################
## 'source' function reads the measure from the database if it exists         ##
################################################################################

#Sees if a similar measure is already in the database
#Verifies if that measure type is already in the measure_code table.
#Note that adding a new measure should also be done through python (mysqlconnect module)

    def source(self, db):

        self.__db=db

        #Get the ID of the elephant:
        self.__elephant = self.__db.get_elephant(num = self.__num)
        if self.__elephant is None:
            print("This elephant is absent from the database. Impossible to add a measure.")
            self.__xeleph = 0

        else:
            self.__elephant_id = self.__elephant[0]
            self.__xeleph = 1

            #Start by seeing if that measure type is present in the measure_code table:
            self.__code = self.__db.get_measure_code(self.__measure)

            if self.__code is None:
                print("Measure type", self.__measure, "is not registered yet.\nPlease register it before proceeding (or check for typos)")

            else:
                self.__db_line = self.__db.get_measure(self.__num, self.__date, self.__code)
                #Cases where the measure is already entered in a similar form in the database:
                if self.__db_line is not None:

                    self.__db_value = self.__db_line[5]
                    if float(self.__value) == self.__db_value:
                        self.__sourced = 1
                        print("An identical measure is already entered in the database.")
                        self.__xrep = 0
                    else:
                        if self.__replicate == 'N':
                            print("There is already a measure for ", self.__measure, " at that date in the database (", self.__value, ")", sep="")
                            self.__sourced = 1
                            self.__xrep = 0

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
            self.__checked = 1
            print("This measure is already in the database. Nothing to do here.")
        #If the measure is not present yet but the measure type is valid
        elif self.__sourced == 2:
            self.__mean_value = float(self.__db.get_mean_measure(self.__code))
            if (self.__value > 10*self.__mean_value or self.__value < self.__mean_value/10) and self.__solved == 'N':
                print("The proposed value is out of the mean order of magnitude in the database. Check the input.")
                self.__xval = 0
            else:
                print("This measure is valid. You can proceed to write()")
                self.__xval = 1
                self.__checked = 2

################################################################################
## 'write' function writes out the sql instert statement or an error          ##
################################################################################

    def write(self, db):
        self.__db=db

        if self.__checked == 0:
            if self.__sourced == 0:
                print("This entry must pass through check() first.")
            elif self.__sourced == 1:
                print("This entry is not valid. Please check input before proceeding.")
        elif self.__checked == 1 and self.__sourced == 1:
            print("This measure is already entered, nothing to do.")
        elif self.__checked == 2:
            out = self.__db.insert_measure(self.__measure_id, self.__elephant_id, self.__date, self.__code, self.__value)

        if self.__xeleph == 1:
            if self.__xval == 0:
                if self.__xrep == 1:
                    out = "[Conflict] Value out of range for elephant "+str(self.__num)+" (here "+str(self.__measure)+"="+str(self.__value)+" vs. mean "+str(self.__mean_value)+")"
                elif self.__xrep == 0:
                    out = "[Conflict] Value "+str(self.__value)+" ("+str(self.__measure)+") for elephant "+str(self.__num)+" appears to be a duplicate"
        elif self.__xeleph == 0:
            out = "[Conflict] Elephant number "+str(self.__num)+" is absent from the database"

        return(out)

   ##########################################################################
 ##############################################################################
###                                                                          ###
##                              CLASS "EVENT"                                 ##
###                                                                          ###
 ##############################################################################
   ##########################################################################


# A measure object consists of fields
