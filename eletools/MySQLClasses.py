# External dependencies:
import pymysql as pms
import string
import re

# Cross-dependencies:
from eletools.Utilities import *


   ##########################################################################
 ##############################################################################
###                                                                          ###
##                               CLASS "MYSQLCONNECT"                         ##
###                                                                          ###
 ##############################################################################
   ##########################################################################

class mysqlconnect:

    def __init__(self, usr, pwd, host='localhost', db='mep', port=3306):
        self.__usr=usr
        self.__pwd=pwd
        self.__host=host
        self.__db=db
        self.__port=int(port)
        self.__db = pms.connect(host=self.__host, user=self.__usr, passwd=self.__pwd, db=self.__db, port=self.__port)
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

    def get_elephant(self, num=None, calf_num=None, id=None):
        self.__num=num
        self.__calf_num=calf_num
        self.__id=id
        if self.__num is not None and self.__id is None:
            sql = "SELECT * FROM elephants WHERE num = %s;" % (self.__num)
        elif self.__num is None and self.__calf_num is not None and self.__id is None:
            sql = "SELECT * FROM elephants WHERE calfnum = %s;" % (self.__calf_num) ##Will open to a problem when several calves have the same ID and no adult ID...fix by matching on dates
        elif self.__num is None and self.__calf_num is None and self.__id is not None:
            sql = "SELECT * FROM elephants WHERE id = %s;" % (self.__id)
        else:
            print("Error: you one and only one identifier")
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

    def get_mother(self, num=None, id=None):
        self.__num=num
        self.__id=id
        if self.__num is not None and self.__id is None:
            sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
            self.__cursor.execute(sql)
            id1 = self.__cursor.fetchall()[0][0]
            sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_1_id WHERE pedigree.elephant_2_id = %s AND rel = 'mother';" % (id1)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
        elif self.__num is None and self.__id is not None:
            sql = "SELECT elephant_1_id FROM pedigree WHERE elephant_2_id = %s AND rel = 'mother';" % (self.__id)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
        else:
            print("You must provide an ID number OR an elephant number")
        if result:
            return result[0][0]

################################################################################
## 'get_father' function                                                          ##
################################################################################

    def get_father(self, num=None, id=None):
        self.__num=num
        self.__id=id
        if self.__num is not None and self.__id is None:
            sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
            self.__cursor.execute(sql)
            id1 = self.__cursor.fetchall()[0][0]
            sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_1_id WHERE pedigree.elephant_2_id = %s AND rel = 'father';" % (id1)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
        elif self.__num is None and self.__id is not None:
            sql = "SELECT elephant_1_id FROM pedigree WHERE elephant_2_id = %s AND rel = 'father';" % (self.__id)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
        else:
            print("You must provide an ID number OR an elephant number")
        if result:
            return result[0][0]

################################################################################
## 'get_offsprings' function                                                          ##
################################################################################

    def get_offsprings(self, num=None, id=None):
        self.__num=num
        self.__id=id
        if self.__num is not None and self.__id is None:
            sql = "SELECT id FROM elephants WHERE num = %s" % (self.__num)
            self.__cursor.execute(sql)
            id1 = self.__cursor.fetchall()[0][0]
            sql = "SELECT num FROM elephants INNER JOIN pedigree ON elephants.id = pedigree.elephant_1_id WHERE pedigree.elephant_2_id = %s AND rel = 'offspring';" % (id1)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()
        elif self.__num is None and self.__id is not None:
            sql = "SELECT elephant_1_id FROM pedigree WHERE elephant_2_id = %s AND rel = 'offspring';" % (self.__id)
            self.__cursor.execute(sql)
            result = self.__cursor.fetchall()

        else:
            print("You must provide an ID number OR an elephant number")
        if result:
            o = []
            for r in result:
                o.append(r[0])
            return o

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
## 'get_measure' function                                                     ##
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
## 'get_mean_measure' function                                                ##
################################################################################

    def get_mean_measure(self, code):
        self.__code = code
        sql = "SELECT ROUND(AVG(value),2) FROM measures WHERE measure = %s;" % (self.__code)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'get_event_code' function                                                          ##
################################################################################

    def get_event_code(self, event):
        self.__event=event
        sql = "SELECT id FROM event_code WHERE code = %s" % (quote(self.__event))
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'get_event' function                                                       ##
################################################################################

    def get_event(self, num, date, event_type):
        sql = "SELECT id FROM elephants WHERE num = %s" % (num)
        try:
            self.__cursor.execute(sql)
            self.__eleph_id = self.__cursor.fetchall()[0][0]
        except:
            print("This elephant is absent from the database")

        sql = "SELECT * FROM events WHERE elephant_id = %s AND date = %s AND type = %s" % (quote(self.__eleph_id), quote(date), quote(event_type))
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0])

################################################################################
## 'get_date_of_death' function                                               ##
################################################################################

    def get_date_of_death(self, id):
        sql = "SELECT date FROM events WHERE elephant_id = %s AND type = 'death';" % (id)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'get_last_alive' function                                                  ##
################################################################################

    def get_last_alive(self, id):
        sql = "SELECT MAX(date) FROM events WHERE id = %s AND type != 'death';" % (id)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'get_last_breeding' function                                                  ##
################################################################################

    def get_last_breeding(self, id):
        sql = "SELECT MAX(b.birth) FROM pedigree AS p LEFT JOIN elephants AS a ON p.elephant_1_id = a.id LEFT JOIN elephants AS b ON p.elephant_2_id = b.id WHERE (p.rel = 'mother' OR p.rel = 'father') AND a.id = %s;" % (id)
        self.__cursor.execute(sql)
        result = self.__cursor.fetchall()
        if result:
            return(result[0][0])

################################################################################
## 'insert_elephant' function                                                 ##
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

################################################################################
## 'insert_event' function                                                    ##
################################################################################

    def insert_event(self, id, date, loc, event_type, code, commits=None):

        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            if commits is not None:
                newcommits = (quote(str(commits)+','+str(self.__i)))
            else:
                newcommits = (quote(str(self.__i)))

            statement = "INSERT INTO events (elephant_id, date, loc, type, code, commits) VALUES (%s, %s, %s, %s, %s, %s);" % (id, quote(date), quote(loc), quote(event_type), code, newcommits)

            return(statement)

################################################################################
## 'insert_event_code' function                                               ##
################################################################################

    def insert_event_code(self, code, descript, commits=None):

        if self.__i is None:
            print("You must generate a time stamp first using mysqlconnect.stamp()")
        else:
            if commits is not None:
                newcommits = (quote(str(commits)+','+str(self.__i)))
            else:
                newcommits = (quote(str(self.__i)))

            statement = "INSERT INTO event_code (code, descript, commits) VALUES (%s, %s, %s);" % (quote(code), quote(descript), newcommits)

            return(statement)
