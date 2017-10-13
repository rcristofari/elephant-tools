    import csv
    import numpy as np
    import re

    rows = []

    with open('../fake_measures.csv') as elefile:
        eleread = csv.reader(elefile, delimiter=';', quotechar="'")
        fields = next(eleread)
        for row in eleread:
            if row != []:
                rows.append(row)
    nfields = rows[0].__len__() - 2

    #Check data types: only numeric values allowed for the measures
    reject = 0
    warnings = []

    num = []
    date = []
    for row in rows:
        num.append(row[0])
        date.append(row[1])

    ########## num
    for i,x in enumerate(num):
        if re.search(r"^[0-9]+$", x):
            pass
        elif x == '':
            warnings.append("Missing elephant number at line " + str(i+1) + ". You need one.")
            reject = 1
        else:
            warnings.append("Format problem with elephant number: " + str(x) + " at line " + str(i+1))
            reject = 1
            
    ########## date
    for i,x in enumerate(date):
        if re.search(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x):
            pass
        elif x == '':
            warnings.append("Missing date at line " + str(i+1))
        else:
            warnings.append("Format problem with date: " + str(x) + " at line " + str(i+1))
            reject = 1

    ########## other fields
    for f in range(nfields):
        current_field = fields[f+2]
        values = []
        for row in rows:
            values.append(row[f+2])
        for i,v in enumerate(values):
            if v.casefold() in ('', 'na','none','null','n/a','unknown','ukn'):
                v = None
            if v != None:
                try:
                    float(v)
                except ValueError:
                    reject = 1
                    warnings.append("Format problem with value "+str(v)+" at line "+str(i)+".")

    # Check the value ranges - isolate each measure as a vector
    # and check whether each point is within a 5x factor of the median

    if reject == 0:

        for f in range(nfields):
            current_field = fields[f+2]
            values = []
            for row in rows:
                try:
                    values.append(float(row[f+2]))
                except ValueError:
                    pass #for the purpose of calculating range, we ignore missing values
            v_array = np.array(values)
            vm = np.median(v_array)
            for i,v in enumerate(values):
                if v != 0 and (v > 5*vm or v < vm/5):
                    reject = 1
                    warnings.append(current_field+": value "+str(v)+" seems out of range at line "+str(i)+".")

        if reject == 1:
            warnings.append("Please check values are correct and declare the file Solved.")

    # Now parse the output out into small blocks
    # the measure_id field is temporary and needs to be added to the last measure_id in the db
    output = []
    for i,row in enumerate(rows):
        for f in range(nfields):
            line = (num[i], date[i], (i+1), fields[f+2], row[f+2])
            output.append(line)

    for w in warnings:
        print(w)

    if reject == 0:
        return(output)
    else:
       return(warnings)
            

         
        






