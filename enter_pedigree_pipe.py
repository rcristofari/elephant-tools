from elephant_classes import *
from elephant_functions import *

common_out = []
db = mysqlconnect('robin','12345','localhost','mep')
s = db.stamp()
common_out.append(s)


print("\nREADING INPUT FILE...\n")
p_raw = read_pedigree('../true_rel_indb.csv', sep=',')

with open("Accepted.txt", "w") as accepted:
    accepted.write(str(p_raw[0])[1:-1]+'\n')
    for x in p_raw[1]:
        accepted.write(str(x)[1:-1]+'\n')
with open("Rejected.txt", "w") as rejected:
    rejected.write(str(p_raw[0])[1:-1]+'\n')
    for x in p_raw[3]:
        rejected.write(str(x)[1:-1]+'\n')
with open("Remarks.txt","w") as remark:
    for x in p_raw[2]:
        remark.write(str(x)[2:-2]+'\n')
with open("Issues.txt", "w") as issue:
    for x in p_raw[4]:
        issue.write((str(x)[2:-2])+'\n')

p = p_raw[1]
del p_raw

print("...DONE.\n")


for row in p:
    elephant_1_id = row[0]
    elephant_2_id = row[1]
    rel = row[2]
    coef = row[3]

    px = pedigree(elephant_1_id, elephant_2_id, rel, coef)
    px.source(db)
    px.check()
    common_out.append(px.write(db))

    print(common_out[0])
for o in common_out[1:]:
    print(o[0])
    print(o[1])
