from elephant_classes import *
db = mysqlconnect('robin','12345','localhost','MTE')
db.stamp()
ele = elephant(9271)
ele.source(db)
c = ele.check()
print(c)
ele.write(db)
