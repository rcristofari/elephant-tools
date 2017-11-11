#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
# from eletools_gui.master import *
# from eletools_gui.import_classes import *
# from eletools_gui.add_classes import *
# from eletools_gui.search_classes import *

################################################################################
## SQL connexion window                                                       ##
################################################################################

class dbconnect(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.read_parmfile()
        self.create_widgets()


    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.save_config_radio = tk.IntVar()
        self.save_config_radio.set(0)
        self.userlabel = tk.Label(self.master, text="User:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.pwdlabel = tk.Label(self.master, text="Password:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.hostlabel = tk.Label(self.master, text="Host:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Database:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Port:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master, show='*')
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)
        self.e5 = tk.Entry(self.master)
        self.e1.insert(10,self.master.params_usr)
        self.e2.insert(10,self.master.params_pwd)
        self.e3.insert(10,self.master.params_host)
        self.e4.insert(10,self.master.params_db)
        self.e5.insert(10,self.master.params_port)
        self.e1.grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)
        self.e2.grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)
        self.e3.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)
        self.e4.grid(row=4, column=2, sticky=tk.E, padx=5, pady=5)
        self.e5.grid(row=5, column=2, sticky=tk.E, padx=5, pady=5)
        self.detailslabel = tk.Label(self.master, text="Details (optional, if entering new data):", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.detailslabel.grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.details = tk.Text(self.master, height=5, width=45)
        self.details.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.connectbutton = tk.Button(self.master, text='Connect', width=15, command=self.connect_to_db, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.disconnectbutton = tk.Button(self.master, text='Disconnect', width=15, command=self.disconnect_from_db, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.connectbutton.grid(row=8, column=1, sticky=tk.W, padx=5, pady=5)
        self.disconnectbutton.grid(row=8, column=2, sticky=tk.E, padx=5, pady=5)
        self.disconnectbutton.config(state="disabled")
        self.radio = tk.Radiobutton(self.master, text="Save configuration", variable=self.save_config_radio, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio.grid(row=9, column=2, sticky=tk.NE, padx=5, pady=5)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.bind("<Return>", self.connect_to_db)

    def connect_to_db(self):
        try:
            self.master.db = mysqlconnect(usr=self.e1.get(), pwd=self.e2.get(), host=self.e3.get(), db=self.e4.get(), port=self.e5.get())
            if self.details.get("1.0", tk.END) !='\n':
                self.master.stamp = self.master.db.stamp(details=self.details.get("1.0", tk.END)) #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            else:
                self.master.stamp = self.master.db.stamp() #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            self.master.common_out.append(self.master.stamp)
            print("You are connected!")
            self.master.menubar.entryconfig("File", state='normal')
            self.master.menubar.entryconfig("Search", state='normal')
            self.master.menubar.entryconfig("Add", state='normal')
            self.disconnectbutton.config(state="normal")
            self.connectbutton.config(state="disabled")
            self.radio.config(state="disabled")
        except: #still an error here.
            print("Impossible to connect to database.")

        if self.save_config_radio.get() == 1:
            self.save_config()
            self.save_config_radio.set(0)

    def disconnect_from_db(self):
        try:
            del self.master.db
            self.disconnectbutton.config(state="disabled")
            self.connectbutton.config(state="normal")
            self.master.menubar.entryconfig("File", state='disabled')
            self.master.menubar.entryconfig("Search", state='disabled')
            self.master.menubar.entryconfig("Add", state='normal')
            self.radio.config(state="normal")
        except:
            print("You are not connected to any database.")

    def read_parmfile(self):
        params = []
        with open('./parmfile') as parmfile:
            for line in parmfile:
                params.append(line.partition('=')[2].rstrip('\n'))
        self.master.params_usr = params[1]
        self.master.params_pwd = params[2]
        self.master.params_host = params[3]
        self.master.params_db = params[4]
        self.master.params_port = params[5]
        self.master.wdir = params[6]
        if self.master.wdir == '' or self.master.wdir is None:
            self.master.wdir = '~'

    def save_config(self):
        with open('./parmfile', 'w') as parmfile:
            parmfile.write("//connexion parameters"+'\n')
            parmfile.write("username="+self.e1.get()+'\n')
            parmfile.write("password="+self.e2.get()+'\n')
            parmfile.write("host="+self.e3.get()+'\n')
            parmfile.write("database="+self.e4.get()+'\n')
            parmfile.write("port="+self.e5.get()+'\n')
            parmfile.write("wdir="+self.master.wdir+'\n')
