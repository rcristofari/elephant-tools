from elephant_classes import *
#ele = elephant(7071, solved = 'N', name='mae', mysql_usr='robin', mysql_pwd='12345')
#ele.source()
#ele.check()
#a = ele.write()

#print("\n", a)


#This is to route the output to the right file
#if 'INSERT' in a or 'UPDATE' in a:
#    print('Output goes to the SQL file')
#else:
#    print('Output goes to the CSV file')


#Function "find_grandmother" to crawl up the database


p = pedigree(eleph_1='9071', eleph_2='3748', mysql_usr='robin', mysql_pwd='12345')
a = p.source()
#print(a)
