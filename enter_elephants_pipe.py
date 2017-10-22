from elephant_classes import *
from elephant_functions import *

common_out = []

db = mysqlconnect('robin','12345','localhost','mep')

#Generate a timestamp and append it to the query list
s = db.stamp()
common_out.append(s)

print("\nREADING INPUT FILE...\n")
eles_raw = read_elephants('../elephants_rejected_formatted_2nd.csv', sep=',')

with open("Accepted.txt", "w") as accepted:
    accepted.write(str(eles_raw[0])[1:-1]+'\n')
    for x in eles_raw[1]:
        accepted.write(str(x)[1:-1]+'\n')
with open("Rejected.txt", "w") as rejected:
    rejected.write(str(eles_raw[0])[1:-1]+'\n')
    for x in eles_raw[3]:
        rejected.write(str(x)[1:-1]+'\n')
with open("Remarks.txt","w") as remark:
    for x in eles_raw[2]:
        remark.write(str(x)[2:-2]+'\n')
with open("Issues.txt", "w") as issue:
    for x in eles_raw[4]:
        issue.write((str(x)[2:-2])+'\n')

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
    common_out.append(ele.write(db))

for o in common_out:
    print(o)
