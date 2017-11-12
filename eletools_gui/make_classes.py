#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
import os
import re
import csv
from eletools import *

################################################################################
## make_measure_set                                                           ##
################################################################################

class make_measure_set(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.__mode = tk.IntVar()
        self.__lm = tk.StringVar()
        self.__lm.set('l')
        self.create_widgets()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.radio1 = tk.Radiobutton(self.master, text="From template", variable=self.__mode, value=1, command=self.display_load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=1, column=1, sticky=tk.W)
        self.radio2 = tk.Radiobutton(self.master, text="Choose measures", variable=self.__mode, value=2, command=self.display_load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio2.grid(row=1, column=2, sticky=tk.W)

    def display_load_template(self):
        self.clear_frame()
        self.create_widgets()
        self.loadtemplatebutton = tk.Button(self.master, text="Load template", width=25, command=self.load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.loadtemplatebutton.grid(row=2, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.radiolm1 = tk.Radiobutton(self.master, text="latest value", variable=self.__lm, value='l', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm1.grid(row=3, column=1, sticky=tk.W)
        self.radiolm1.config(state='disabled')
        self.radiolm2 = tk.Radiobutton(self.master, text="mean value", variable=self.__lm, value='m', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm2.grid(row=3, column=2, sticky=tk.W)
        self.radiolm2.config(state='disabled')
        self.findbutton = tk.Button(self.master, text="Make data file", width=25, command=self.make_datafile, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.findbutton.grid(row=4, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.findbutton.config(state='disabled')
        self.savebutton = tk.Button(self.master, text="Save as CSV", width=25, command=self.write_csv, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savebutton.grid(row=5, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.savebutton.config(state='disabled')

    def load_template(self):
        self.__templatefilename = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose a template file")
        self.radiolm1.config(state='normal')
        self.radiolm2.config(state='normal')
        self.findbutton.config(state='normal')
        self.loadtemplatebutton.config(state='disabled')

    def make_datafile(self):
        self.radiolm1.config(state='disabled')
        self.radiolm2.config(state='disabled')
        self.findbutton.config(state='disabled')
        self.loadtemplatebutton.config(state='normal')

        self.__elephants = []
        self.__measures = []
        self.__filter = []
        with open(self.__templatefilename) as templatefile:
            lines = csv.reader(templatefile, delimiter = ',')
            self.__measures_tags = next(lines)
            self.__tag = self.__measures_tags.pop(0)
            if re.search(r"^[bim]:.*", self.__tag.casefold()):
                self.__key = self.__tag.split(':')[0]
                self.__missingstr = self.__tag.split(':')[1]
                try:
                    self.__missing = float(self.__missingstr)
                except:
                    print("Format error on the missing data specification:", self.__missingstr)
            else:
                print("Format error on the template tag", self.__tag)

            if self.__key.casefold() in ('i','b'):
                for line in lines:
                    if line != []:
                        self.__elephants.append(line[0])

            # Parse the 'latest' or 'mean' tags, and complete them if missing
            if self.__key.casefold() in ('m','b'):
                __buffer = []

                for m in self.__measures_tags:
                    if re.search(r"^[a-zA-Z0-9_-]+:[lm]{1}", m.casefold()):
                        self.__measures.append(m.split(':')[0])
                        self.__filter.append(m.split(':')[1].casefold())
                        __buffer.append(m.casefold())
                    else:
                        self.__measures.append(m)
                        self.__filter.append(self.__lm.get())
                        __buffer.append(m+':'+self.__lm.get())

                self.__measures_tags = __buffer
                print(self.__measures_tags)

            # Send out to the right subprocedure
            if self.__key.casefold() == 'b':
                self.get_values_both()
            elif self.__key.casefold() == 'm':
                self.get_values_measures()
            elif self.__key.casefold() == 'i':
                self.get_values_individuals()

    def get_values_both(self):
        result = None
        self.__out = []
        for e in self.__elephants:
            line = [e]
            for i,m in enumerate(self.__measures):
                result = self.master.db.get_measure_values(e, "('"+m+"')")
                if result is not None:
                    if result.__len__() == 1 or (result.__len__() != 1 and self.__filter[i] == 'l'):
                        line.append(result[0][3])
                    elif result.__len__() != 1 and self.__filter[i] == 'm':
                        __mean = self.master.db.get_mean_measure(e, m)
                        line.append(__mean)
                else:
                    line.append('')

            self.__out.append(line)

        self.savebutton.config(state='normal')

    def get_values_individuals(self):
        result = None
        self.__out = []
        self.__all = []
        self.__measures = []
        self.__measures_tags= []

        # We start by calling all possible measures for each elephant (including a lot of missing data)
        __measure_list = []
        __measure_list_all = self.master.db.get_measure_list()
        for m in __measure_list_all:
            __measure_list.append(m[0])

        for e in self.__elephants:
            line = []
            for m in __measure_list:
                result = self.master.db.get_measure_values(e, "('"+m+"')")
                if result is not None:
                    if result.__len__() == 1 or (result.__len__() != 1 and self.__filter[i] == 'l'):
                        line.append(result[0][3])
                    elif result.__len__() != 1 and self.__filter[i] == 'm':
                        __mean = self.master.db.get_mean_measure(e, m)
                        line.append(__mean)
                else:
                    line.append('')
            self.__all.append(line)

        # Now we scan this column-wise (by measure)
        self.__kept = []
        for i,m in enumerate(__measure_list):
            __n_missing = 0
            __this_measure = []
            for a in self.__all:
                __this_measure.append(a[i])
                if a[i] == '':
                    __n_missing += 1
            __ratio = __n_missing / __this_measure.__len__()
            if __ratio <= self.__missing:
                self.__kept.append(__this_measure)
                self.__measures.append(m)
                self.__measures_tags.append(m+':'+self.__lm.get())

        for i,e in enumerate(self.__elephants):
            line = [e]
            for k in self.__kept:
                line.append(k[i])
            self.__out.append(line)
        del self.__kept
        self.savebutton.config(state='normal')


    def get_values_measures(self):
        result = None
        self.__out = []
        self.__all = []
        self.__elephants = []

        # We start by calling all possible elephants for each measure (including a lot of missing data)
        __elephant_list = []
        #Get all elephants that have at least one measure:
        __elephant_list_all = self.master.db.get_measured_elephants_list()

        for e in __elephant_list_all:
            __elephant_list.append(e)

        for m in self.__measures:
            line = []
            for e in __elephant_list:
                result = self.master.db.get_measure_values(e, "('"+m+"')")
                if result is not None:
                    if result.__len__() == 1 or (result.__len__() != 1 and self.__filter[i] == 'l'):
                        line.append(result[0][3])
                    elif result.__len__() != 1 and self.__filter[i] == 'm':
                        __mean = self.master.db.get_mean_measure(e, m)
                        line.append(__mean)
                else:
                    line.append('')
            self.__all.append(line)

        # Now we scan this column-wise (by elephant)
        self.__kept = []
        for i,e in enumerate(__elephant_list):
            __n_missing = 0
            __this_elephant = []
            for a in self.__all:
                __this_elephant.append(a[i])
                if a[i] == '':
                    __n_missing += 1
            __ratio = __n_missing / __this_elephant.__len__()
            if __ratio <= self.__missing:
                self.__kept.append(__this_elephant)
                print(self.__kept)
                self.__elephants.append(e)

        for i,e in enumerate(self.__elephants):
            line = [e]
            for k in self.__kept[i]:
                line.append(k)
            self.__out.append(line)

        del self.__kept
        self.savebutton.config(state='normal')

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, defaultextension='.csv')

        with open(filename,"w") as f:
            f.write(self.__tag+',')

            for m in self.__measures_tags:
                f.write(m+',')
            f.write('\n')

            for o in self.__out:
                for x in o:
                    f.write(str(x)+',')
                f.write('\n')

        del self.__measures
        del self.__elephants
        del self.__out
