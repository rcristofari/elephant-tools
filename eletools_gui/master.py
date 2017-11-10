#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui.db_classes import *
from eletools_gui.import_classes import *
from eletools_gui.add_classes import *
from eletools_gui.search_classes import *

################################################################################
## Main application window                                                    ##
################################################################################

class MainApplication(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        # Graphical parameters:
        self.master.lightcolour = "#E08E45"
        self.master.darkcolour = "#A30B37"

        self.configure_gui()
        self.create_widgets()
        self.master.common_out = [] #This will be the main MySQL and error out
        self.goconnect()


        # These are "flow data" (to be passed on from manual add to the file-based pipeline)
        self.master.manual_add_elephant = None
        self.master.pass_from_add_elephant = False



    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        self.master.geometry("500x500")
        self.master.resizable(False, False)
        self.master.background_image = tk.PhotoImage(file='./__resources/background.png')
        self.master.background_label = tk.Label(self.master, image=self.master.background_image)
        self.master.background_label.place(x=0, y=0, relwidth=1, relheight=1)


    def create_widgets(self):
        self.master.menubar = tk.Menu(self)

        filemenu = tk.Menu(self.master.menubar, tearoff=0)
        filemenu.add_command(label="Import elephants", command=self.read_elephants_prompt)
        filemenu.add_command(label="Import pedigrees", command=self.read_pedigree_prompt)
        filemenu.add_command(label="Import events", command=self.notimplemented)
        filemenu.add_command(label="Import measures", command=self.notimplemented)
        filemenu.add_separator()
        filemenu.add_command(label="Set project folder", command=self.set_wdir)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.quit)
        filemenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="File", menu=filemenu)
        self.master.menubar.entryconfig("File", state='disabled')

        searchmenu = tk.Menu(self.master.menubar, tearoff=0)
        searchmenu.add_command(label="Find an elephant", command=self.gofindeleph)
        searchmenu.add_command(label="Find a relationship", command=self.notimplemented)
        searchmenu.add_command(label="Find an event", command=self.call_find_event)
        searchmenu.add_command(label="Find a measure", command=self.call_find_measure)
        searchmenu.add_separator()
        searchmenu.add_command(label="Make a measure set", command=self.notimplemented)
        searchmenu.add_command(label="Make a time series", command=self.notimplemented)
        searchmenu.add_command(label="Make a stud book", command=self.notimplemented)
        searchmenu.add_separator()
        searchmenu.add_command(label="Control birth gaps", command=self.call_age_gaps)
        searchmenu.add_command(label="Advanced search", command=self.notimplemented)
        searchmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Search", menu=searchmenu)
        self.master.menubar.entryconfig("Search", state='disabled')

        addmenu = tk.Menu(self.master.menubar, tearoff=0)
        addmenu.add_command(label="Add an elephant", command=self.call_add_elephants)
        addmenu.add_command(label="Add a relationship", command=self.notimplemented)
        addmenu.add_command(label="Add an event", command=self.notimplemented)
        addmenu.add_command(label="Add a measure", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Add a measure type", command=self.notimplemented)
        addmenu.add_command(label="Add an event type", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Update living status", command=self.notimplemented)
        addmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Add", menu=addmenu)
        self.master.menubar.entryconfig("Add", state='disabled')

        dbmenu = tk.Menu(self.master.menubar, tearoff = 0)
        dbmenu.add_command(label="Connexion", command=self.goconnect)
        dbmenu.add_command(label="MySQL dump", command=self.notimplemented)
        dbmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Database", menu=dbmenu)

        self.master.menubar.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.config(menu=self.master.menubar)


    def goconnect(self):
        dbconnect(self.master)

    def read_elephants_prompt(self):
        read_elephant_file(self.master)

    def read_pedigree_prompt(self):
        read_pedigree_file(self.master)

    def call_age_gaps(self):
        age_gaps(self.master)

    def set_wdir(self):
        self.master.wdir = askdirectory(initialdir=self.master.wdir, title='Choose a project folder...')
        with open('./parmfile', 'w') as parmfile:
            parmfile.write("//connexion parameters"+'\n')
            parmfile.write("username="+self.master.params_usr+'\n')
            parmfile.write("password="+self.master.params_pwd+'\n')
            parmfile.write("host="+self.master.params_host+'\n')
            parmfile.write("database="+self.master.params_db+'\n')
            parmfile.write("port="+self.master.params_port+'\n')
            parmfile.write("wdir="+self.master.wdir+'\n')

    def gofindeleph(self):
        findeleph(self.master, back = 0)

    def call_find_measure(self):
        find_measure(self.master)

    def call_find_event(self):
        find_event(self.master)

    def call_add_elephants(self):
        add_elephants(self.master)

    def notimplemented(self):
        print("Not implemented yet")
