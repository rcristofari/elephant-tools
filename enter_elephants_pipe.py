from elephant_classes import *
from elephant_functions import *

common_out = []

db = mysqlconnect('robin','12345','localhost','mep')

#Generate a timestamp and append it to the query list
s = db.stamp()
common_out.append(s)

print("\nREADING INPUT FILE...\n")
eles_raw = read_elephants('../elephants.csv', sep=',')

parse_reads(eles_raw, prefix='../test')

eles = eles_raw[1]
del eles_raw

print("...DONE.\n")


for row in eles[1:]:
    num = row[0]
    name = row[1]
    calf_num = row[2]
    sex = row[3]
    birth = row[4]
    cw = row[5]
    caught = row[6]
    camp = row[7]
    alive = row[8]
    research = row[9]
    ele = elephant(num,name,calf_num,sex,birth,cw,caught,camp,alive,research, solved='Y')
    ele.source(db)
    ele.check()
    self.master.common_out.append(ele.write(db))

parse_output(common_out,db)
