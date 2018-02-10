import string
from datetime import datetime
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

# Try to guess date format from excel
def format_date(date, proper_decimal=False):
    try:
        newdate = datetime.strptime(str(date), '%Y-%m-%d')
        return(datetime.strftime(newdate, '%Y-%m-%d'))
    except:
        try:
            newdate = datetime.strptime(str(date), '%d/%m/%Y')
            return(datetime.strftime(newdate, '%Y-%m-%d'))
        except:
            try:
                newdate = datetime.strptime(str(date), '%d.%m.%Y')
                return(datetime.strftime(newdate, '%Y-%m-%d'))
            except:
                try:
                    newdate = datetime.strptime(str(date), '%Y')
                    return(datetime.strftime(newdate, '%Y-%m-%d'))
                except:
                    try:
                        if proper_decimal is True:
                            dec = float(date)
                            years = int(dec // 1)
                            remains = dec % 1

                            if ( (int(years % 4) == 0) and (int(years % 100) != 0)) or (int(years % 400) == 0):
                                months = (31,29,31,30,31,30,31,31,30,31,30,31)
                            else:
                                months = (31,28,31,30,31,30,31,31,30,31,30,31)

                            days = round(remains * sum(months))

                            if days < 1:
                                month = 1
                                day = 1

                            elif days >= sum(months):
                                month=12
                                day=31

                            else:
                                sum_months = 0
                                m = -1
                                while sum_months <= days:
                                    m += 1
                                    sum_months += months[m]
                                month = m+1
                                sum_months -= months[m]
                                day = days - sum_months
                        else:

                            dec = float(date)
                            years = int(dec // 1)
                            remains = dec % 1

                            if ( (int(years % 4) == 0) and (int(years % 100) != 0)) or (int(years % 400) == 0):
                                months = (31,29,31,30,31,30,31,31,30,31,30,31)
                                lyear = 366
                            else:
                                months = (31,28,31,30,31,30,31,31,30,31,30,31)
                                lyear = 365

                            alldays = remains * lyear
                            month = int((alldays/30.44)//1 + 1)
                            if month > 12:
                                month = 12

                            day = int((alldays - sum(months[0:(month-1)]))//1 + 1)


                        if day > months[(month-1)] and month < 12:
                            day = 1
                            month = month + 1
                        elif day > months[(month-1)] and month == 12:
                            day = 31
                        elif day < 1 and month > 1:
                            day = months[(month - 2)]
                            month = month -1
                        elif day < 1 and month == 1:
                            day = 1
                            month = 1

                        newdate = str(years)+'-'+str(month)+'-'+str(day)
                        return(datetime.strftime(datetime.strptime(newdate, '%Y-%m-%d').date(), '%Y-%m-%d'))

                    except:
                        print("There's been a problem with date conversion - unknown format")
                        return(date)