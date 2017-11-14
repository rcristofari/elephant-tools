import string
from calendar import isleap

########## A function to double-quote strings for mysql queries:
def quote(string):
    return("'"+str(string)+"'")

########## A function to break down 2-power flags into their individual components
def break_flag(flag):
    try:
        flag = int(flag)
    except:
        print("Argument must be an integer")

    flags = []

    # Find the largest power of 2 entering the flag:
    n = 0
    while flag >= 2**n:
        n += 1

    # Find individual components
    remains = flag
    while remains > 0:
        if remains - 2**n >= 0:
            flags.append(n)
            remains = remains - 2**n
        n -= 1
    flags.sort()
    return(flags)

########## A function to add years to a datetime object
def add_years(d, years):
    new_year = d.year + years
    try:
        return d.replace(year=new_year)
    except ValueError:
        if (d.month == 2 and d.day == 29 and # leap day
            isleap(d.year) and not isleap(new_year)):
            return d.replace(year=new_year, day=28)
        raise
