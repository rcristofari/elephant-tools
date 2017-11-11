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
        self.create_widgets()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.loadtemplatebutton = tk.Button(self.master, text="Load template", width=25, command=self.load_template, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.loadtemplatebutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)

    def load_template(self):
        templatefilename = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose a template file")
        self.__elephants = []
        with open(templatefilename) as templatefile:
            lines = csv.reader(templatefile, delimiter = ',')
            self.__measures = next(lines)
            self.__key = self.__measures.pop(0)
            if self.__key.casefold() in ('i','b'):
                for line in lines:
                    if line != []:
                        self.__elephants.append(line[0])

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
            for m in self.__measures:
                result = self.master.db.get_measure_values(e, "('"+m+"')") # SO FAR THIS IS TAKING THE MOST RECENT VALUE (but could be most ancient, average, median...) 
                if result is not None:
                    if result.__len__()==1: ## IF THERE ARE SEVERAL MEASURES FOR THE SAME PARAMETER, WHAT DO WE DO ???
                        line.append(result[0][3])
                else:
                    line.append('')

            self.__out.append(line)
        self.write_csv()

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, defaultextension='.csv')
        with open(filename,"w") as f:
            f.write(self.__key+',')

            for m in self.__measures:
                f.write(m+',')
            f.write('\n')

            for o in self.__out:
                for x in o:
                    f.write(str(x)+',')
                f.write('\n')
