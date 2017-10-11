from elephant_functions import *
from elephant_classes import *

eles = read_elephant("../elephants.csv", ";")
print(eles[1][0:30])

total = eles[1].__len__()

out = []

for i in range(1,total):
    ele = elephant(mysql_usr='robin', mysql_pwd='12345', num=eles[1][i], name=eles[2][i], sex=eles[3][i],
                   birth=eles[4][i], cw=eles[5][i], caught=eles[6][i], camp=eles[7][i], alive=eles[8][i],
                   solved='Y')
    ele.source()
    ele.check()
    o = ele.write()
    out.append(o)


for o in out:
    if o != None:
        print(o)
