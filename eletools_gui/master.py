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
from eletools_gui.make_classes import *

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
        self.master.db_state = 0
        self.master.details_text = '' # Details of the session for the db stamp
        self.goconnect()


        # These are "flow data" (to be passed on from manual add to the file-based pipeline)
        self.master.manual_add_elephant = None
        self.master.pass_from_add_elephant = False
        self.master.current_search_num = None # This is to keep the same elephant's number between searches


    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        self.master.geometry("500x500")
        self.master.resizable(False, False)
        self.master.background_image = tk.PhotoImage(file='./__resources/background.png')
        self.master.background_label = tk.Label(self.master, image=self.master.background_image)
        self.master.background_label.place(x=0, y=0, relwidth=1, relheight=1)


    def create_widgets(self):
        self.master.menubar = tk.Menu(self)

        self.filemenu = tk.Menu(self.master.menubar, tearoff=0)
        self.filemenu.add_command(label="Import elephants", command=self.read_elephants_prompt)
        self.filemenu.add_command(label="Import pedigrees", command=self.read_pedigree_prompt)
        self.filemenu.add_command(label="Import events", command=self.notimplemented)
        self.filemenu.add_command(label="Import measures", command=self.notimplemented)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Set project folder", command=self.set_wdir)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.quit)
        self.filemenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="File", menu=self.filemenu)
        self.master.menubar.entryconfig("File", state='disabled')

        self.searchmenu = tk.Menu(self.master.menubar, tearoff=0)
        self.searchmenu.add_command(label="Find an elephant", command=self.gofindeleph)
        self.searchmenu.add_command(label="Find a relationship", command=self.notimplemented)
        self.searchmenu.add_command(label="Find an event", command=self.call_find_event)
        self.searchmenu.add_command(label="Find a measure", command=self.call_find_measure)
        self.searchmenu.add_separator()
        self.searchmenu.add_command(label="Make a measure set", command=self.call_make_measure_set)
        self.searchmenu.add_command(label="Make a time series", command=self.notimplemented)
        self.searchmenu.add_command(label="Make a log book", command=self.notimplemented)
        self.searchmenu.add_separator()
        self.searchmenu.add_command(label="Control birth gaps", command=self.call_age_gaps)
        self.searchmenu.add_command(label="Advanced search", command=self.notimplemented)
        self.searchmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Search", menu=self.searchmenu)
        self.master.menubar.entryconfig("Search", state='disabled')

        self.addmenu = tk.Menu(self.master.menubar, tearoff=0)
        self.addmenu.add_command(label="Add an elephant", command=self.call_add_elephants)
        self.addmenu.add_command(label="Add a relationship", command=self.notimplemented)
        self.addmenu.add_command(label="Add an event", command=self.notimplemented)
        self.addmenu.add_command(label="Add a measure", command=self.notimplemented)
        self.addmenu.add_separator()
        self.addmenu.add_command(label="Add a measure type", command=self.notimplemented)
        self.addmenu.add_command(label="Add an event type", command=self.notimplemented)
        self.addmenu.add_separator()
        self.addmenu.add_command(label="Update living status", command=self.notimplemented)
        self.addmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Add", menu=self.addmenu)
        self.master.menubar.entryconfig("Add", state='disabled')

        self.dbmenu = tk.Menu(self.master.menubar, tearoff = 0)
        self.dbmenu.add_command(label="Connexion", command=self.goconnect)
        self.dbmenu.add_command(label="MySQL dump", command=self.notimplemented)
        self.dbmenu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.master.menubar.add_cascade(label="Database", menu=self.dbmenu)

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

    def call_make_measure_set(self):
        make_measure_set(self.master)

    def call_add_elephants(self):
        add_elephants(self.master)

    def notimplemented(self):
        print("Not implemented yet")
