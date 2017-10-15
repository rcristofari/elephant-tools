from elephant_classes import *
from elephant_functions import *

common_out = []

db = mysqlconnect('robin','12345','localhost','mep')

#Generate a timestamp and append it to the query list
s = db.stamp()
common_out.append(s)

print("\nREADING INPUT FILE...\n")
eles = read_elephants('../elephants.csv', sep=',')
print("...DONE.\n")

for row in eles[1:2]:
    try:
        num = int(row[0])
    except:
        num = None
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
    common_out.append(ele.write(db))

for o in common_out:
    print(o)
