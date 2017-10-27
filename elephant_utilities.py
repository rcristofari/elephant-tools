import csv
import string
import re
import numpy as np
from datetime import datetime

# Write a "crawler" function to work the pedigrees up and down from one individual
# Write a "consolidate_alive" function to assess who is alive / dead now from data (using get_last_alive and get_last_breeding)
# Write a "get commits" function that parses out the list of commits and get the corresponding entries.

####################################################################################
##  make_measure_set() takes an optional list of individuals and measure names    ##
####################################################################################
# ind is a tuple of individuals
# measures is a tuple with measure names.
# either we fix the measures, and we get all elephants that have them.
# or we fix the elephants, and we get all available measures.
# or we fix both and then we get what's available.

# then there will be a read_example() function to provide an empty table

def make_measure_set(ind=None, measures=None):
    if ind is None and measures is None:
        print("You must give at least one desciption")
        mode = 0
    elif ind is None and measures is not None:
        mode = 1
    elif ind is not None and measures is None:
        mode = 2
    elif ind is not None and measures is not None:
        mode = 3

def make_time_series(ind=None, measure=None):
    pass

def retrieve_dataset(dataset):
    pass
