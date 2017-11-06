#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *

################################################################################
## SQL connexion window                                                       ##
################################################################################

class dbconnect(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
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
        self.userlabel = tk.Label(self.master, text="User:", bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.pwdlabel = tk.Label(self.master, text="Password:", bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.hostlabel = tk.Label(self.master, text="Host:", bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Database:", bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Port:", bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master, show='*')
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)
        self.e5 = tk.Entry(self.master)
        self.e3.insert(10,"localhost")
        self.e4.insert(10,"mep")
        self.e5.insert(10,"3306")
        self.e1.grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)
        self.e2.grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)
        self.e3.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)
        self.e4.grid(row=4, column=2, sticky=tk.E, padx=5, pady=5)
        self.e5.grid(row=5, column=2, sticky=tk.E, padx=5, pady=5)
        self.detailslabel = tk.Label(self.master, text="Details (optional, if entering new data):", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.detailslabel.grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.details = tk.Text(self.master, height=5, width=45)
        self.details.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.connectbutton = tk.Button(self.master, text='Connect', width=15, command=self.connect_to_db, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.disconnectbutton = tk.Button(self.master, text='Disconnect', width=15, command=self.disconnect_from_db, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.connectbutton.grid(row=8, column=1, sticky=tk.W, padx=5, pady=5)
        self.disconnectbutton.grid(row=8, column=2, sticky=tk.E, padx=5, pady=5)
        self.disconnectbutton.config(state="disabled")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.bind('<Return>', self.connect_to_db)

    def connect_to_db(self):
        try:
            self.master.db = mysqlconnect(usr=self.e1.get(), pwd=self.e2.get(), host=self.e3.get(), db=self.e4.get(), port=self.e5.get())
            if self.details.get("1.0", tk.END) is not None:
                self.master.stamp = self.master.db.stamp(details=self.details.get("1.0", tk.END)) #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            else:
                self.master.stamp = self.master.db.stamp() #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            self.master.common_out.append(self.master.stamp)
            print("You are connected!")
        except: #still an error here.
            print("Impossible to connect to database.")
        self.master.menubar.entryconfig("File", state='normal')
        self.master.menubar.entryconfig("Search", state='normal')
        self.master.menubar.entryconfig("Add", state='normal')
        self.disconnectbutton.config(state="normal")
        self.connectbutton.config(state="disabled")

    def disconnect_from_db(self):
        try:
            del self.master.db
            self.disconnectbutton.config(state="disabled")
            self.connectbutton.config(state="normal")
            self.master.menubar.entryconfig("File", state='disabled')
            self.master.menubar.entryconfig("Search", state='disabled')
            self.master.menubar.entryconfig("Add", state='normal')
        except:
            print("You are not connected to any database.")
