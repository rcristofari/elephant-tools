#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui.import_classes import *

################################################################################
## Manually add some elephants                                                ##
################################################################################

class add_elephants(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.sex = tk.StringVar()
        self.cw = tk.StringVar()
        self.alive = tk.StringVar()
        self.research = tk.StringVar()
        self.stringvar1 = tk.StringVar()
        self.stringvar1.trace("w", self.valid_entry)
        self.stringvar5 = tk.StringVar() #calf number, added on second thought
        self.stringvar5.trace("w", self.valid_entry)
        self.stringvar2 = tk.StringVar()
        self.stringvar2.trace("w", self.valid_entry)
        self.stringvar3 = tk.StringVar()
        self.stringvar3.trace("w", self.valid_entry)
        self.stringvar4 = tk.StringVar()
        self.stringvar4.trace("w", self.valid_entry)
        self.sex.set('UKN')
        self.cw.set('UKN')
        self.alive.set('UKN')
        self.research.set('N')
        self.rows = []
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        ########## First column:
        self.numlabel = tk.Label(self.master, text="Number:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.numentry = tk.Entry(self.master, width=10, textvariable=self.stringvar1)
        self.numentry.grid(row=1, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.namelabel = tk.Label(self.master, text="Name:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.namelabel.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.nameentry = tk.Entry(self.master, width=10)
        self.nameentry.grid(row=2, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.calfnumlabel = tk.Label(self.master, text="Calf number:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.calfnumlabel.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.calfnumentry = tk.Entry(self.master, width=10, textvariable=self.stringvar5)
        self.calfnumentry.grid(row=3, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.sexlabel = tk.Label(self.master, text="Sex:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.sexlabel.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.sexradio1 = tk.Radiobutton(self.master, text="F", variable=self.sex, value='F', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.sexradio1.grid(row=4, column=2, sticky=tk.W)
        self.sexradio2 = tk.Radiobutton(self.master, text="M", variable=self.sex, value='M', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.sexradio2.grid(row=4, column=3, sticky=tk.E)
        self.sexradio3 = tk.Radiobutton(self.master, text="?", variable=self.sex, value='UKN', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.sexradio3.grid(row=4, column=4, sticky=tk.E)

        self.birthlabel = tk.Label(self.master, text="Birth (DMY):", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.birthlabel.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.birthDD = tk.Entry(self.master, width=2, textvariable=self.stringvar2)
        self.birthDD.grid(row=5, column=2, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthMM = tk.Entry(self.master, width=2, textvariable=self.stringvar3)
        self.birthMM.grid(row=5, column=3, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthYYYY = tk.Entry(self.master, width=4, textvariable=self.stringvar4)
        self.birthYYYY.grid(row=5, column=4, columnspan=1, sticky=tk.EW, padx=1, pady=5)

        ########## Second column:
        self.cwlabel = tk.Label(self.master, text="Captive:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cwlabel.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)
        self.cwradio1 = tk.Radiobutton(self.master, text="C", variable=self.cw, value='captive', command=self.disable_caught, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cwradio1.grid(row=1, column=6, sticky=tk.W)
        self.cwradio2 = tk.Radiobutton(self.master, text="W", variable=self.cw, value='wild', command=self.enable_caught, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cwradio2.grid(row=1, column=7, sticky=tk.E)
        self.cwradio3 = tk.Radiobutton(self.master, text="?", variable=self.cw, value='UKN', command=self.disable_caught, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cwradio3.grid(row=1, column=8, sticky=tk.E)

        self.caughtlabel = tk.Label(self.master, text="Age caught:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.caughtlabel.grid(row=2, column=5, sticky=tk.W, padx=5, pady=5)
        self.caughtentry = tk.Entry(self.master, width=10)
        self.caughtentry.grid(row=2, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.caughtentry.config(state="disabled")

        self.camplabel = tk.Label(self.master, text="Camp:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.camplabel.grid(row=3, column=5, sticky=tk.W, padx=5, pady=5)
        self.campentry = tk.Entry(self.master, width=10)
        self.campentry.grid(row=3, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.alivelabel = tk.Label(self.master, text="Alive:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.alivelabel.grid(row=4, column=5, sticky=tk.W, padx=5, pady=5)
        self.aliveradio1 = tk.Radiobutton(self.master, text="Y", variable=self.alive, value='Y', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.aliveradio1.grid(row=4, column=6, sticky=tk.W)
        self.aliveradio2 = tk.Radiobutton(self.master, text="N", variable=self.alive, value='N', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.aliveradio2.grid(row=4, column=7, sticky=tk.E)
        self.aliveradio3 = tk.Radiobutton(self.master, text="?", variable=self.alive, value='UKN', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.aliveradio3.grid(row=4, column=8, sticky=tk.E)

        self.researchlabel = tk.Label(self.master, text="Research:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.researchlabel.grid(row=5, column=5, sticky=tk.W, padx=5, pady=5)
        self.researchradio1 = tk.Radiobutton(self.master, text="Y", variable=self.research, value='Y', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.researchradio1.grid(row=5, column=6, sticky=tk.W)
        self.researchradio2 = tk.Radiobutton(self.master, text="N", variable=self.research, value='N', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.researchradio2.grid(row=5, column=7, sticky=tk.W)
        # self.researchradio3 = tk.Radiobutton(self.master, text="?", variable=self.research, value=3, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        # self.researchradio3.grid(row=5, column=8, sticky=tk.E)

        self.addbutton = tk.Button(self.master, text='Add', width=15, command=self.add_row, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.addbutton.grid(row=6, column=1, columnspan=4, sticky=tk.EW, padx=5, pady=5)
        self.checkbutton = tk.Button(self.master, text='Verify', width=15, command=self.verify_entries, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.checkbutton.grid(row=6, column=5, columnspan=4, sticky=tk.EW, padx=5, pady=5)

        self.tv = ttk.Treeview(self.master, height=6)
        self.tv['columns'] = ('Num','Name','Calf','S','B','CW','Cg','Cp','A','R')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=20)
        # Create fields
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=25)
        self.tv.grid(row=7, column=1, columnspan=8, padx=5, pady=5, sticky=tk.EW)

        self.tv.bind("<Double-1>", self.OnDoubleClick)

    def valid_entry(self, *args):
        s1 = self.stringvar1.get()
        s2 = self.stringvar2.get()
        s3 = self.stringvar3.get()
        s4 = self.stringvar4.get()
        s5 = self.stringvar5.get()
        if (s1 and s2 and s3 and s4) or (s5 and s2 and s3 and s4):
            self.addbutton.config(state='normal')
        else:
            self.addbutton.config(state='disabled')

    def disable_caught(self):
        self.caughtentry.config(state="disabled")
        self.caughtentry.update()

    def enable_caught(self):
        self.caughtentry.config(state="normal")
        self.caughtentry.update()

    def add_row(self):
        birth = str(self.birthYYYY.get())+'-'+str(self.birthMM.get())+'-'+str(self.birthDD.get())
        row = [self.numentry.get(), self.nameentry.get(), self.calfnumentry.get(), self.sex.get(), birth, self.cw.get(), self.caughtentry.get(), self.campentry.get(), self.alive.get(), self.research.get()]
        self.rows.append(row)
        for item in self.tv.get_children():
            self.tv.delete(item)
        i = 1
        for row in self.rows:
            i += 1
            self.tv.insert('','end',text=str(i), values=row[0:10], tags = ('smalltext',))
        self.tv.tag_configure('smalltext', font=('Helvetica',8))
        self.clear_entries()

    def clear_entries(self):
        self.numentry.delete(0, tk.END)
        self.nameentry.delete(0, tk.END)
        self.calfnumentry.delete(0, tk.END)
        self.birthYYYY.delete(0, tk.END)
        self.birthMM.delete(0, tk.END)
        self.birthDD.delete(0, tk.END)
        self.caughtentry.delete(0, tk.END)
        self.campentry.delete(0, tk.END)
        self.sex.set('UKN')
        self.cw.set('UKN')
        self.alive.set('UKN')
        self.research.set('N')

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        # self.tv.delete(item)
        r = self.rows.pop(int(self.tv.item(item,"text"))-2)
        for item in self.tv.get_children():
            self.tv.delete(item)
        i = 1
        for row in self.rows:
            i += 1
            self.tv.insert('','end',text=str(i), values=row[0:10], tags = ('smalltext',))
        self.clear_entries()
        self.numentry.insert(10,r[0])
        self.nameentry.insert(10,r[1])
        self.calfnumentry.insert(10,r[2])
        self.sex.set(r[3])
        self.birthYYYY.insert(10, r[4].partition('-')[0])
        self.birthMM.insert(10, r[4].partition('-')[2].partition('-')[0])
        self.birthDD.insert(10, r[4].partition('-')[2].partition('-')[0])
        self.cw.set(r[5])
        self.caughtentry.insert(10, r[6])
        self.campentry.insert(10, r[7])
        self.alive.set(r[8])
        self.research.set(r[9])

    def verify_entries(self):
        if self.rows != []:
            self.master.pass_from_add_elephant = True
            self.master.manual_add_elephant = self.rows
            read_elephant_file(self.master)


################################################################################
## Check (and add) a measure type                                             ##
################################################################################

class add_measure_type(tk.Frame):

    def __init__(self, master, fromAnalyse = False, preselect=None):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.fromAnalyse = fromAnalyse
        self.master.select_type = None
        self.master.preselect = preselect
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        if self.master.preselect is not None:
            self.check_measure()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.__classes_types = self.master.db.get_measure_list()
        self.__classes = []
        for c in self.__classes_types:
            self.__classes.append(c[0])
        self.__classes = list(set(self.__classes))
        self.__classes.sort()
        self.__chosen = tk.StringVar()
        self.__chosen.set(self.__classes[0])
        self.classlabel = tk.Label(self.master, text="Measure class: ")
        self.classlabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.classlabel.grid(row=1, column=1, sticky=tk.W)
        self.classmenu = tk.OptionMenu(self.master, self.__chosen, *self.__classes)
        self.classmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.classmenu.grid(row=1, column=2, columnspan=3, sticky=tk.EW)
        self.typelabel = tk.Label(self.master, text="Measure type: ")
        self.typelabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.typelabel.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.typeentry = tk.Entry(self.master, width=10)
        self.typeentry.grid(row=2, column=2, sticky=tk.E, pady=5)
        if self.master.preselect is not None:
            self.typeentry.insert(10, self.master.preselect)
        self.unitlabel = tk.Label(self.master, text="   Unit: ")
        self.unitlabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.unitlabel.grid(row=2, column=3, sticky=tk.E, pady=5)
        self.unitentry = tk.Entry(self.master, width=10)
        self.unitentry.grid(row=2, column=4, sticky=tk.E, pady=5)
        self.detailslabel = tk.Label(self.master, text="Details: ")
        self.detailslabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.detailslabel.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.detailsentry = tk.Entry(self.master, width=6)
        self.detailsentry.grid(row=3, column=2, columnspan=3, sticky=tk.EW, pady=5)
        self.checkbutton = tk.Button(self.master, text="Check", command=self.check_measure)
        self.checkbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.checkbutton.grid(row=4, column=1, columnspan=4, sticky=tk.EW, pady=5)
        self.tv = ttk.Treeview(self.master, height=6)
        self.tv['columns'] = ('Type','Unit','Details')
        self.tv.heading("#0", text='Class')
        self.tv.column("#0", anchor='w', width=40)
        # Create fields
        self.tv.heading('Type', text='Type')
        self.tv.column('Type', anchor='w', width=15)
        self.tv.heading('Unit', text='Unit')
        self.tv.column('Unit', anchor='w', width=10)
        self.tv.heading('Details', text='Details')
        self.tv.column('Details', anchor='w', width=100)
        self.tv.grid(row=5, column=1, columnspan=4, padx=5, sticky=tk.EW)
        self.tv.bind("<Double-1>", self.OnDoubleClick)
        self.cancelbutton = tk.Button(self.master, text="Cancel", command=self.cancel_entry, width=10)
        self.cancelbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cancelbutton.grid(row=6, column=1, columnspan=1, sticky=tk.EW, pady=5)
        if self.fromAnalyse is True:
            self.usebutton = tk.Button(self.master, text="Select", command=self.select_measure, width=10)
            self.usebutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
            self.usebutton.grid(row=6, column=2, columnspan=2, sticky=tk.EW, pady=5, padx=5)
        self.addbutton = tk.Button(self.master, text="Add", command=self.add_measure, width=10)
        self.addbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.addbutton.grid(row=6, column=4, columnspan=1, sticky=tk.EW, pady=5)
        self.master.focus_set()
        self.master.bind('<Return>', self.check_measure)

    def OnDoubleClick(self, event): # Add something here to prevent user from selecting the greyed row
        for item in self.tv.get_children()[1:]:
            self.tv.item(item, tags=('smalltext',))
        item = self.tv.selection()[0]
        self.tv.item(item, tags=('red',))
        self.tv.tag_configure('smalltext', font=('Helvetica',8))
        self.tv.tag_configure('grey', font=('Helvetica',8), background='#D5D0CD')
        self.tv.tag_configure('red', font=('Helvetica',8), background=self.master.darkcolour)
        self.select_type = self.tv.item(item, 'values')[0]

    def check_measure(self, *args):
        for item in self.tv.get_children():
            self.tv.delete(item)
        m = [self.__chosen.get(), self.typeentry.get(), self.unitentry.get(), self.detailsentry.get()]
        self.tv.insert('','end',text=m[0], values=m[1:4], tags = ('grey',))
        self.master.matches = fuzzy_match_measure(self.master.db, type=self.typeentry.get(), cutoff=0.6)
        if self.master.matches is not None:
            for m in self.master.matches:
                self.tv.insert('','end',text=m[0], values=m[1:4], tags = ('smalltext',))
        self.tv.tag_configure('smalltext', font=('Helvetica',8))
        self.tv.tag_configure('grey', font=('Helvetica',8), background='#D5D0CD')

    def cancel_entry(self):
        for item in self.tv.get_children():
            self.tv.delete(item)
        self.typeentry.delete(0, tk.END)
        self.unitentry.delete(0, tk.END)
        self.detailsentry.delete(0, tk.END)

    def select_measure(self):
        # self.master.select_type has been defined by OnDoubleClick
        # This is a bit tricky, since we now need to update the Add Measures input class
        # using the row index that was clicked to instantiate the add_measure_type class
        if self.master.select_type is not None:
            print(self.master.preselect, self.master.select_type)
            print(self.file_content)

    def add_measure(self):
        print(self.__chosen.get(), self.typeentry.get(), self.unitentry.get(), self.detailsentry.get())
        statement = self.master.db.write_new_measure(mclass=self.__chosen.get(), mtype=self.typeentry.get(), unit=self.unitentry.get(), details=self.detailsentry.get())
        if statement is not None:
            self.master.common_out.append(statement)
            print(statement)


################################################################################
## Check (and add) an experiment                                              ##
################################################################################

class add_experiment(tk.Frame):

    def __init__(self, master, fromAnalyse = False, preselect=None):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()

        # Clear the common out and stamp it:
        self.master.common_out = []
        self.master.common_out.append(self.master.stamp)

        # Create a list for experiments to be inserted:
        self.experiments = []

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):

        self.explabel = tk.Label(self.master, text="Experiment: ")
        self.explabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.explabel.grid(row=2, column=1, sticky=tk.W, pady=5)
        self.expentry = tk.Entry(self.master, width=10)
        self.expentry.grid(row=2, column=2, columnspan=3, sticky=tk.EW, pady=5)

        self.detailslabel = tk.Label(self.master, text="Details: ")
        self.detailslabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.detailslabel.grid(row=3, column=1, sticky=tk.W, pady=5)
        self.detailsentry = tk.Entry(self.master, width=40)
        self.detailsentry.grid(row=4, column=1, columnspan=4, sticky=tk.EW, pady=5)

        self.checkbutton = tk.Button(self.master, text="Add", command=self.check_experiment)
        self.checkbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.checkbutton.grid(row=5, column=1, columnspan=4, sticky=tk.EW, pady=5)

        self.tv = ttk.Treeview(self.master, height=6)
        self.tv['columns'] = ('Experiment','Details')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='w', width=5)
        # Create fields
        self.tv.heading('Experiment', text='Experiment')
        self.tv.column('Experiment', anchor='w', width=25)
        self.tv.heading('Details', text='Details')
        self.tv.column('Details', anchor='w', width=100)
        self.tv.grid(row=6, column=1, columnspan=4, padx=0, pady=5, sticky=tk.EW)
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.cancelbutton = tk.Button(self.master, text="Clear", command=self.cancel_entry, width=10)
        self.cancelbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cancelbutton.grid(row=7, column=1, columnspan=1, sticky=tk.EW, pady=5)

        self.addbutton = tk.Button(self.master, text="Apply", command=self.apply_add_experiment, width=10)
        self.addbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.addbutton.grid(row=7, column=4, columnspan=1, sticky=tk.EW, pady=5)
        self.addbutton.config(state='disabled')

        self.master.focus_set()
        self.master.bind('<Return>', self.check_experiment)

    def OnDoubleClick(self, event): # Add something here to prevent user from selecting the greyed row
        for item in self.tv.get_children()[1:]:
            self.tv.item(item, tags=('smalltext',))
        item = self.tv.selection()[0]
        self.tv.item(item, tags=('red',))
        self.tv.tag_configure('smalltext', font=('Helvetica',8))
        self.tv.tag_configure('grey', font=('Helvetica',8), background='#D5D0CD')
        self.tv.tag_configure('red', font=('Helvetica',8), background=self.master.darkcolour)
        self.select_type = self.tv.item(item, 'values')[0]

    def check_experiment(self, *args):
        m = [self.expentry.get(), self.detailsentry.get()]
        # Check that the experiment is valid, and not yet in the database:
        inDB = self.master.db.get_experiment_code(m[0])
        if inDB:
            pass
            self.WarningPopup("This experiment is already registered in the database")

        else:
            # Check format:
            if re.search(r"^[a-zA-Z0-9_\- /]{0,128}$", m[0]) and all(x not in ["'", '"', ","] for x in m[1]):
                self.tv.insert('','end', text='', values=m[0:2], tags = ('grey',))
                self.tv.tag_configure('smalltext', font=('Helvetica',8))
                self.tv.tag_configure('grey', font=('Helvetica',8), background='#D5D0CD')
                self.addbutton.config(state='normal')
                # Add to the experiment list:
                self.experiments.append(m)

            else:
                self.WarningPopup("Format error, please avoid special characters")

    def WarningPopup(self, warning):
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("Warning")
        self.warningbox = tk.Text(self.warning_window, height=5, width=35)
        self.warningbox.grid(row=1, column=1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        self.warningbox.insert(tk.END, warning)
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def cancel_entry(self):
        self.disable_addbutton()
        for item in self.tv.get_children():
            self.tv.delete(item)
        # Flush the list of experiments to be inserted:
        self.experiments = []
        # Clear the common out and stamp it:
        self.master.common_out = []
        self.master.common_out.append(self.master.stamp)

        self.expentry.delete(0, tk.END)
        self.detailsentry.delete(0, tk.END)

    def disable_addbutton(self):
        self.addbutton.config(state='disabled')

    def apply_add_experiment(self):
        for m in self.experiments:
            print(m)
            statement = self.master.db.insert_experiment(experiment=m[0], details=m[1], commits=None)
            if statement is not None:
                self.master.common_out.append(statement)
        self.InsertPopup()
        ## HERE, RESET THE COMMIT NUMBER AND CLEAR THE COMMON OUT !!

    def InsertPopup(self):
        self.insert_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.insert_window.title("")
        self.insertlabel = tk.Label(self.insert_window, text="The following statements will be applied to the database. Are you sure you want to proceed?\t")
        self.insertlabel.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.insertlabel.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=10, pady=5)

        self.queries = list(set(self.master.common_out))
        self.queries.sort()

        querytext=''
        for q in self.queries:
            querytext = querytext + q + '\n'

        self.insertbox = tk.Text(self.insert_window, height=10, width=70)
        self.insertbox.grid(row=2, column=1, columnspan=2, sticky=tk.EW, padx=10, pady=5)
        self.insertbox.insert(tk.END, querytext)
        self.insertbox.config(state=tk.DISABLED)

        self.cancelbutton = tk.Button(self.insert_window, text="Cancel", command=self.close_insert, width=10)
        self.cancelbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cancelbutton.grid(row=3, column=1, columnspan=1, sticky=tk.EW, padx=10, pady=5)

        self.addbutton = tk.Button(self.insert_window, text="Apply", command=self.call_send_query, width=10)
        self.addbutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.addbutton.grid(row=3, column=2, columnspan=1, sticky=tk.EW, padx=10, pady=5)

        self.insert_window.focus_set()

    def close_insert(self):
       self.insert_window.destroy()

    def call_send_query(self):
        for q in self.queries:
            s = self.master.db.send_query(q)
            if s != 1:
                self.errorw = tk.Toplevel(self.master, bg=self.master.lightcolour)
                self.errorw.title("Error")
                self.errorl = tk.Label(self.errorw, text=s)
                self.errorl.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0,
                                        activebackground=self.master.darkcolour,
                                        activeforeground=self.master.lightcolour)
                self.errorl.grid(row=1, column=1, columnspan=1, sticky=tk.EW, padx=10, pady=5)
                self.errorw.focus_set()
                break

        # Flush the list of experiments to be inserted:
        self.experiments = []
        # Clear the common out and stamp it:
        self.master.common_out = []
        self.master.stamp = self.master.db.stamp()
        self.master.common_out.append(self.master.stamp)
        print(self.master.stamp)

        self.close_insert()
        #self.cancel_entry()
