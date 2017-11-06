#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui.master import *
from eletools_gui.db_classes import *
from eletools_gui.import_classes import *
from eletools_gui.search_classes import *

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
        self.numlabel = tk.Label(self.master, text="Number:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.numlabel.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.numentry = tk.Entry(self.master, width=10, textvariable=self.stringvar1)
        self.numentry.grid(row=1, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.namelabel = tk.Label(self.master, text="Name:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.namelabel.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.nameentry = tk.Entry(self.master, width=10)
        self.nameentry.grid(row=2, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.calfnumlabel = tk.Label(self.master, text="Calf number:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.calfnumlabel.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.calfnumentry = tk.Entry(self.master, width=10)
        self.calfnumentry.grid(row=3, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.sexlabel = tk.Label(self.master, text="Sex:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexlabel.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.sexradio1 = tk.Radiobutton(self.master, text="F", variable=self.sex, value='F', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio1.grid(row=4, column=2, sticky=tk.W)
        self.sexradio2 = tk.Radiobutton(self.master, text="M", variable=self.sex, value='M', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio2.grid(row=4, column=3, sticky=tk.E)
        self.sexradio3 = tk.Radiobutton(self.master, text="?", variable=self.sex, value='UKN', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio3.grid(row=4, column=4, sticky=tk.E)

        self.birthlabel = tk.Label(self.master, text="Birth (DMY):", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.birthlabel.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.birthDD = tk.Entry(self.master, width=2, textvariable=self.stringvar2)
        self.birthDD.grid(row=5, column=2, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthMM = tk.Entry(self.master, width=2, textvariable=self.stringvar3)
        self.birthMM.grid(row=5, column=3, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthYYYY = tk.Entry(self.master, width=4, textvariable=self.stringvar4)
        self.birthYYYY.grid(row=5, column=4, columnspan=1, sticky=tk.EW, padx=1, pady=5)

        ########## Second column:
        self.cwlabel = tk.Label(self.master, text="Captive:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwlabel.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)
        self.cwradio1 = tk.Radiobutton(self.master, text="C", variable=self.cw, value='captive', command=self.disable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio1.grid(row=1, column=6, sticky=tk.W)
        self.cwradio2 = tk.Radiobutton(self.master, text="W", variable=self.cw, value='wild', command=self.enable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio2.grid(row=1, column=7, sticky=tk.E)
        self.cwradio3 = tk.Radiobutton(self.master, text="?", variable=self.cw, value='UKN', command=self.disable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio3.grid(row=1, column=8, sticky=tk.E)

        self.caughtlabel = tk.Label(self.master, text="Age caught:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.caughtlabel.grid(row=2, column=5, sticky=tk.W, padx=5, pady=5)
        self.caughtentry = tk.Entry(self.master, width=10)
        self.caughtentry.grid(row=2, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.caughtentry.config(state="disabled")

        self.camplabel = tk.Label(self.master, text="Camp:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.camplabel.grid(row=3, column=5, sticky=tk.W, padx=5, pady=5)
        self.campentry = tk.Entry(self.master, width=10)
        self.campentry.grid(row=3, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.alivelabel = tk.Label(self.master, text="Alive:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.alivelabel.grid(row=4, column=5, sticky=tk.W, padx=5, pady=5)
        self.aliveradio1 = tk.Radiobutton(self.master, text="Y", variable=self.alive, value='Y', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio1.grid(row=4, column=6, sticky=tk.W)
        self.aliveradio2 = tk.Radiobutton(self.master, text="N", variable=self.alive, value='N', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio2.grid(row=4, column=7, sticky=tk.E)
        self.aliveradio3 = tk.Radiobutton(self.master, text="?", variable=self.alive, value='UKN', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio3.grid(row=4, column=8, sticky=tk.E)

        self.researchlabel = tk.Label(self.master, text="Research:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchlabel.grid(row=5, column=5, sticky=tk.W, padx=5, pady=5)
        self.researchradio1 = tk.Radiobutton(self.master, text="Y", variable=self.research, value='Y', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchradio1.grid(row=5, column=6, sticky=tk.W)
        self.researchradio2 = tk.Radiobutton(self.master, text="N", variable=self.research, value='N', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchradio2.grid(row=5, column=7, sticky=tk.W)
        # self.researchradio3 = tk.Radiobutton(self.master, text="?", variable=self.research, value=3, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        # self.researchradio3.grid(row=5, column=8, sticky=tk.E)

        self.addbutton = tk.Button(self.master, text='Add', width=15, command=self.add_row, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.addbutton.grid(row=6, column=1, columnspan=4, sticky=tk.EW, padx=5, pady=5)
        self.checkbutton = tk.Button(self.master, text='Verify', width=15, command=self.check_entries, bg="#E08E45", fg="#A30B37", highlightthickness=0)
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
        if s1 and s2 and s3 and s4:
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

    def check_entries(self):
        pass
