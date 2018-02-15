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
        self.neleph = 0
        self.__available_classes = []
        self.__selected_classes = []
        self.__available_types = []
        self.__selected_types = []
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
        self.radio2 = tk.Radiobutton(self.master, text="Choose measures", variable=self.__mode, value=2, command=self.display_select_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio2.grid(row=1, column=2, sticky=tk.W)

    def display_load_template(self):
        self.clear_frame()
        self.create_widgets()
        self.loadtemplatebutton = tk.Button(self.master, text="Load template", width=35, command=self.load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.loadtemplatebutton.grid(row=2, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.radiolm1 = tk.Radiobutton(self.master, text="latest value", variable=self.__lm, value='l', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm1.grid(row=3, column=1, sticky=tk.W)
        self.radiolm1.config(state='disabled')
        self.radiolm2 = tk.Radiobutton(self.master, text="mean value", variable=self.__lm, value='m', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm2.grid(row=3, column=2, sticky=tk.W)
        self.radiolm2.config(state='disabled')
        self.findbutton = tk.Button(self.master, text="Make data file", width=35, command=self.make_datafile, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.findbutton.grid(row=4, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.findbutton.config(state='disabled')
        self.savebutton = tk.Button(self.master, text="Save as CSV", width=35, command=self.write_csv, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savebutton.grid(row=5, column=1, columnspan = 2, sticky=tk.EW, padx=5, pady=5)
        self.savebutton.config(state='disabled')

    def display_select_measures(self):
        self.clear_frame()
        self.radio1 = tk.Radiobutton(self.master, text="From template", variable=self.__mode, value=1, command=self.display_load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=1, column=1, sticky=tk.W)
        self.radio2 = tk.Radiobutton(self.master, text="Choose measures", variable=self.__mode, value=2, command=self.display_select_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio2.grid(row=1, column=3, sticky=tk.E)
        self.choosebutton = tk.Button(self.master, text="Choose measures", width=25, command=self.choose_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.choosebutton.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.missinglabel = tk.Label(self.master, text="Max missing data (0-1):", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.missinglabel.grid(row=3, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.missingentry = tk.Entry(self.master, width=8)
        self.missingentry.grid(row=3, column=3, sticky=tk.E, padx=5, pady=5)
        self.missingentry.insert(10,'0.2')
        self.radiolm1 = tk.Radiobutton(self.master, text="latest value", variable=self.__lm, value='l', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm1.grid(row=4, column=1, sticky=tk.W)
        self.radiolm1.config(state='disabled')
        self.radiolm2 = tk.Radiobutton(self.master, text="mean value", variable=self.__lm, value='m', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radiolm2.grid(row=4, column=3, sticky=tk.E)
        self.radiolm2.config(state='disabled')
        self.nelephlabel = tk.Label(self.master, text=("-"), bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.nelephlabel.grid(row=6, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.findbutton = tk.Button(self.master, text="Make data file", width=25, command=self.make_datafile_from_gui, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.findbutton.grid(row=7, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.findbutton.config(state='disabled')
        self.savebutton = tk.Button(self.master, text="Save as CSV", width=25, command=self.write_csv, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savebutton.grid(row=8, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.savebutton.config(state='disabled')

    def load_template(self):
        self.__templatefilename = askopenfilename(initialdir=self.master.wdir, filetypes =(("Template file", "*.templ"),("All Files","*.*")), title = "Choose a template file")
        self.radiolm1.config(state='normal')
        self.radiolm2.config(state='normal')
        self.findbutton.config(state='normal')
        self.loadtemplatebutton.config(state='disabled')

    def make_datafile(self):
        if self.__mode.get() == 1:
            self.radiolm1.config(state='disabled')
            self.radiolm2.config(state='disabled')
            self.findbutton.config(state='disabled')
            self.loadtemplatebutton.config(state='normal')

        self.__elephants = []
        self.__measures = []
        self.__filter = []

        if self.__mode.get() == 1:
            with open(self.__templatefilename) as templatefile:
                lines = csv.reader(templatefile, delimiter=',')
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
        if self.__key.casefold() in ('m', 'b'):
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
            for i, m in enumerate(self.__measures):
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
            for i, m in enumerate(__measure_list):
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

        for i, m in enumerate(self.__measures):
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
                self.__elephants.append(e)

        for i,e in enumerate(self.__elephants):
            line = [e]
            for k in self.__kept[i]:
                line.append(k)
            self.__out.append(line)

        del self.__kept
        self.savebutton.config(state='normal')

        self.neleph = self.__out.__len__()
        self.nelephlabel.destroy()
        self.nelephlabel = tk.Label(self.master, text=("Data is available for "+str(self.neleph)+" elephants"), bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.nelephlabel.grid(row=6, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.master.update()

    def choose_measures(self, *args):


        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Select measures")
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(3, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv1label = tk.Label(self.view_window, text="Available measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.tv1label = tk.Label(self.view_window, text="Selected measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=2, sticky=tk.EW, pady=5)

        self.tv1 = ttk.Treeview(self.view_window, height=20, columns=('Unit','Description'), show="tree")
        self.tv1.heading("#0", text='Class')
        self.tv1.heading("#1", text='Type')
        self.tv1.column("#0", width = 120, stretch=0)
        self.tv1.column("#1", width = 20, stretch=0)
        self.tv1.heading('Unit', text='Unit')
        self.tv1.column('Unit', anchor='w', width=50)
        self.tv1.heading('Description', text='Description')
        self.tv1.column('Description', anchor='w', width=200)
        self.tv1.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)

        self.tv2 = ttk.Treeview(self.view_window, height=20, columns=('Unit','Description'), show="tree")
        self.tv2.heading("#0", text='Class')
        self.tv2.heading("#1", text='Type')
        self.tv2.column("#0", width = 120, stretch=0)
        self.tv2.column("#1", width = 20, stretch=0)
        self.tv2.heading('Unit', text='Unit')
        self.tv2.column('Unit', anchor='w', width=50)
        self.tv2.heading('Description', text='Description')
        self.tv2.column('Description', anchor='w', width=200)
        self.tv2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.N)
        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

        self.donebutton = tk.Button(self.view_window, text='Done', width=15, command=self.finish_choosing, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.donebutton.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        # Retrieve the classes ('disease','accident',...) and types (detailed events)
        self.__classes_types = self.master.db.get_measure_list()

        classes_all = []
        for c in self.__classes_types:
            classes_all.append(c[0])
        self.__classes = list(set(classes_all))
        self.__classes.sort(key=lambda k: (k[0]))

        self.__types = []
        for t in self.__classes_types:
            if t in self.__types:
                pass
            else:
                self.__types.append(t)


        self.__selected_classes = []
        self.__selected_types = []

        self.__available_classes = [] #This is to break the vicious binding
        for c in self.__classes:
            self.__available_classes.append(c)
        self.__available_types = []
        for t in self.__types:
            self.__available_types.append(t)

        for c in self.__available_classes:
            globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
        for t in self.__available_types:
            name = t[0]
            self.tv1.insert(globals()[name], "end", text=t[1], values=t[2:4], tags = ('type',))

        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

    def OnDoubleClick1(self, event):

        item = self.tv1.selection()[0]
        __selection = self.tv1.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__available_classes):
                if c == __selection:
                    break
            transfer = self.__available_classes.pop(i)
            self.__selected_classes.append(transfer)
            self.__selected_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            at=[]
            # st=[]
            for t in self.__available_types:
                if t[0] in self.__available_classes:
                    at.append(t)
                elif t[0] in self.__selected_classes:
                    self.__selected_types.append(t)


            self.__available_types = at
            self.__available_types.sort(key=lambda k: (k[1]))
            # self.__selected_types = st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

        else:

            for i,t in enumerate(self.__available_types):
                if t[1] == __selection:
                    break
            transfer = self.__available_types.pop(i)
            self.__selected_types.append(transfer)
            self.__selected_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            ac=[]
            sc=[]
            for t in self.__available_types:
                ac.append(t[0])
            self.__available_classes = list(set(ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                sc.append(t[0])
            self.__selected_classes = list(set(sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

    def OnDoubleClick2(self, event):

        item = self.tv2.selection()[0]
        __selection = self.tv2.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__selected_classes):
                if c == __selection:
                    break
            transfer = self.__selected_classes.pop(i)
            self.__available_classes.append(transfer)
            self.__available_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            # __at=[]
            __st=[]
            for t in self.__selected_types:
                if t[0] in self.__available_classes:
                    self.__available_types.append(t)
                elif t[0] in self.__selected_classes:
                    __st.append(t)

            # self.__available_types = __at
            self.__available_types.sort(key=lambda k: (k[1]))
            self.__selected_types = __st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

        else:

            for i,t in enumerate(self.__selected_types):
                if t[1] == __selection:
                    break
            transfer = self.__selected_types.pop(i)
            self.__available_types.append(transfer)
            self.__available_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            __ac=[]
            __sc=[]
            for t in self.__available_types:
                __ac.append(t[0])
            self.__available_classes = list(set(__ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                __sc.append(t[0])
            self.__selected_classes = list(set(__sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

    def finish_choosing(self):
        self.view_window.destroy()
        self.findbutton.config(state='normal')
        self.radiolm1.config(state='normal')
        self.radiolm2.config(state='normal')

    def make_datafile_from_gui(self):
        self.choosebutton.config(state='disabled')
        self.radiolm1.config(state='disabled')
        self.radiolm2.config(state='disabled')
        self.missingentry.config(state='disabled')
        self.findbutton.config(state='disabled')
        self.__key = 'm'
        self.__tag = self.__key+':'+self.missingentry.get()
        try:
            self.__missing = float(self.missingentry.get())
        except:
            print("Wrong format for missing data limit", self.missingentry.get())

        self.__measures_tags = []
        for m in self.__selected_types:
            self.__measures_tags.append(m[1]+':'+self.__lm.get())
        #
        # self.__filter = []
        # for x in range(self.__measures_tags.__len__()):
        #     self.__filter.append(self.__lm.get())
        self.make_datafile()

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
