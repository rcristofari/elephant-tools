#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui.analyse_classes import *

################################################################################
## Batch read an elephant file                                                ##
################################################################################

class read_elephant_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.solved = tk.IntVar()
        self.solved.set(0)
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_read_elephants()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=1, column = 1, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="This data has already been verified", variable=self.solved, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.master.focus_set()
        self.master.bind('<Return>', self.call_analyse)
        self.master.bind('<space>', self.show_file_content)

    def call_read_elephants(self):
        if self.name is None and self.master.manual_add_elephant is None:
            self.name = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an elephant definition file")
            self.master.shortname=os.path.split(self.name)[1]
            self.master.file_content = read_elephants(self.name, ',', is_file = True)

        elif self.master.manual_add_elephant is not None and self.master.pass_from_add_elephant is True:
            self.master.file_content = read_elephants(self.master.manual_add_elephant, ',', is_file = False)
            self.name=asksaveasfilename(initialdir=self.master.wdir, defaultextension='.csv')
            self.master.shortname=os.path.split(self.name)[1]
        else:
            self.master.shortname=os.path.split(self.name)[1]
            self.master.file_content = read_elephants(self.name, ',', is_file = True)

        n_accepted = self.master.file_content[1].__len__()
        n_rejected = self.master.file_content[3].__len__()

        parse_reads(self.master.file_content, prefix=(self.name.partition('.')[0]))

        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0,tk.END)
        self.result_text = ("\n  The file contains "+str(n_accepted+n_rejected)+" lines:\n"
            +"\n\t-"+str(n_accepted)+" were accepted,"
            +"\n\t-"+str(n_rejected)+" were rejected.\n"
            +"\n  Accepted and rejected entries and logs were written out in:\n\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.log\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.log")
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)

    def show_file_content(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Elephant file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('num','name','calf_num','sex','birth','cw','caught','camp','alive','research')

        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=100)

        # Create fields
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)

        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i,row in enumerate(rows):
            self.tv.insert('','end',text=str(i+1), values=row[0:10], tags = (row[10],))

        self.tv.tag_configure(1, background='#E08E45')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][11]
        self.warningbox = tk.Text(self.warning_window, height=5, width=45)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        if warning != []:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        else:
            self.warningbox.insert(tk.END, "No problem with this elephant.")
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_elephants()

    def call_analyse(self, *args):
        analyse_elephant_file(self.master, solved=self.solved.get())

################################################################################
## Batch read a pedigree file                                                 ##
################################################################################

class read_pedigree_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.calfvar = tk.BooleanVar()
        self.calfvar.set(False)
        self.create_widgets()
        self.call_read_pedigree()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=1, column = 1, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.calflabel = tk.Label(self.master, text='Elephant 2 is', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.calflabel.grid(row=3, column=1, sticky=tk.E, padx=5, pady=5)
        self.calfradio1 = tk.Radiobutton(self.master, text="an adult", variable=self.calfvar, value=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.calfradio1.grid(row=3, column=2, sticky=tk.W, padx=5, pady=5)
        self.calfradio2 = tk.Radiobutton(self.master, text="a calf", variable=self.calfvar, value=True, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.calfradio2.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)

        self.master.focus_set()
        self.master.bind('<Return>', self.call_analyse)
        self.master.bind('<space>', self.show_file_content)

    def call_read_pedigree(self):

        if self.name is None:
            self.name = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose a pedigree definition file")
        self.master.shortname = os.path.split(self.name)[1]

        self.master.file_content = read_pedigree(self.name, ',')
        n_accepted = self.master.file_content[1].__len__()
        n_rejected = self.master.file_content[3].__len__()
        parse_reads(self.master.file_content, prefix=(self.name.partition('.')[0]))

        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0,tk.END)

        self.result_text = ("\n  The file contains "+str(n_accepted+n_rejected)+" lines:\n"
            +"\n\t-"+str(n_accepted)+" were accepted,"
            +"\n\t-"+str(n_rejected)+" were rejected.\n"
            +"\n  Accepted and rejected entries and logs were written out in:\n\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.log\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.log")
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)

    def show_file_content(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.geometry("600x700")
        self.view_window.resizable(False, False)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        if self.calfvar.get() is False:
            self.tv['columns'] = ('Elephant 1', 'Elephant 2', 'rel', 'coef')
        else:
            self.tv['columns'] = ('Elephant', 'Calf', 'rel', 'coef')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=100)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)
        for i,row in enumerate(rows):
            self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = (row[4],))
        self.tv.tag_configure(1, background='#E08E45')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][5]
        self.warningbox = tk.Text(self.warning_window, height=5, width=45)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        if warning != []:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        else:
            self.warningbox.insert(tk.END, "No problem with this relationship.")
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_pedigree()

    def call_analyse(self, *args):
        self.master.eleph_2_is_calf = self.calfvar.get()
        analyse_pedigree_file(self.master)

################################################################################
## Batch read an event file                                                   ##
################################################################################

class read_event_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.calfvar = tk.BooleanVar()
        self.calfvar.set(False)
        self.create_widgets()
        self.call_read_events()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=1, column = 1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=2, column=2, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)
        self.master.focus_set()
        self.master.bind('<Return>', self.call_analyse)
        self.master.bind('<space>', self.show_file_content)


    def call_read_events(self):
        if self.name is None:
            self.name = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an event definition file")
        self.master.shortname = os.path.split(self.name)[1]
        self.master.file_content = read_events(self.name, ',')
        n_accepted = self.master.file_content[1].__len__()
        n_rejected = self.master.file_content[3].__len__()
        parse_reads(self.master.file_content, prefix=(self.name.partition('.')[0]))
        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0,tk.END)
        self.result_text = ("\n  The file contains "+str(n_accepted+n_rejected)+" lines:\n"
            +"\n\t-"+str(n_accepted)+" were accepted,"
            +"\n\t-"+str(n_rejected)+" were rejected.\n"
            +"\n  Accepted and rejected entries and logs were written out in:\n\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.log\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.log")
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)

    def show_file_content(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.geometry("600x700")
        self.view_window.resizable(False, False)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('num', 'calf_num', 'date', 'loc', 'code')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=80)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)
        for i,row in enumerate(rows):
            self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = (row[5],))
        self.tv.tag_configure(1, background='#E08E45')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][6]
        self.warningbox = tk.Text(self.warning_window, height=5, width=45)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        if warning != []:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        else:
            self.warningbox.insert(tk.END, "No problem with this event.")
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_events()

    def call_analyse(self, *args):
        analyse_event_file(self.master)

################################################################################
## Batch read a measure file                                                   ##
################################################################################

class read_measure_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.calfvar = tk.StringVar()
        self.calfvar.set('N')
        self.repvar = tk.StringVar()
        self.repvar.set('N')
        self.solvedvar = tk.StringVar()
        self.solvedvar.set('N')
        self.create_widgets()
        self.call_read_measures()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=1, column = 1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=2, column=2, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)
        self.calfbutton = tk.Checkbutton(self.master, text="Numbers are Calf numbers", variable=self.calfvar, onvalue='Y', offvalue='N', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.calfbutton.grid(row=3, column=2, sticky=tk.W)
        self.repbutton = tk.Checkbutton(self.master, text="Input contains replicates", variable=self.repvar, onvalue='Y', offvalue='N', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.repbutton.grid(row=4, column=2, sticky=tk.W)
        self.solvedbutton = tk.Checkbutton(self.master, text="This is trusted data", variable=self.solvedvar, onvalue='Y', offvalue='N', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.solvedbutton.grid(row=5, column=2, sticky=tk.W)

        self.master.focus_set()
        self.master.bind('<Return>', self.call_analyse)
        self.master.bind('<space>', self.show_file_content)

    def call_read_measures(self):
        if self.name is None:
            self.name = askopenfilename(initialdir=self.master.wdir, filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose a measure definition file")
        self.master.shortname = os.path.split(self.name)[1]
        self.master.file_content = read_measures(self.name, ',', solved=self.solvedvar.get())
        n_accepted = self.master.file_content[1].__len__()
        n_rejected = self.master.file_content[3].__len__()
        parse_reads(self.master.file_content, prefix=(self.name.partition('.')[0]))
        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0,tk.END)
        self.result_text = ("\n  The file contains "+str(n_accepted+n_rejected)+" lines:\n"
            +"\n\t-"+str(n_accepted)+" were accepted,"
            +"\n\t-"+str(n_rejected)+" were rejected.\n"
            +"\n  Accepted and rejected entries and logs were written out in:\n\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_accepted.log\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.reads\n"
            +"\t"+self.master.shortname.partition('.')[0]+"_rejected.log")
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)

    def show_file_content(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.geometry("600x700")
        self.view_window.resizable(False, False)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        if self.calfvar.get() == 'N':
            self.tv['columns'] = ('set', 'elephant', 'date', 'code', 'value')
        else:
            self.tv['columns'] = ('set', 'calf', 'date', 'code', 'value')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=80)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)
        for i,row in enumerate(rows):
            if int(row[0])%2 == 0:
                evenodd = 'even'
            else:
                evenodd = 'odd'
            self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = (row[5],evenodd))
        self.tv.tag_configure(1, background='#E08E45')
        self.tv.tag_configure('odd', foreground='gray') #font = 'globalfont 10 bold'
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][6]
        self.warningbox = tk.Text(self.warning_window, height=5, width=45)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        if warning != []:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        else:
            self.warningbox.insert(tk.END, "No problem with this measure.")
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_measures()

    def call_analyse(self, *args):
        analyse_measure_file(self.master, self.calfvar.get(), self.repvar.get(), self.solvedvar.get())


################################################################################
## Manually add some calves (i.e. birth and mother at the same time)          ##
################################################################################

class read_calf_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.solved = tk.IntVar()
        self.solved.set(0)
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_read_calves()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="This data has already been verified", variable=self.solved, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)

        self.master.focus_set()
        self.master.bind('<Return>', self.call_analyse)
        self.master.bind('<space>', self.show_file_content)

    def call_read_calves(self):
        if self.name is None:
            self.name = askopenfilename(initialdir=self.master.wdir, filetypes=(("CSV File", "*.csv"),
                                        ("All Files", "*.*")), title="Choose a calf definition file")
            self.master.shortname = os.path.split(self.name)[1]
            self.master.file_content = read_calves(self.name, ',', is_file=True)

        else:
            self.master.shortname = os.path.split(self.name)[1]
            self.master.file_content = read_calves(self.name, ',', is_file=True)

        n_accepted = self.master.file_content[1].__len__()
        n_rejected = self.master.file_content[3].__len__()

        parse_reads(self.master.file_content, prefix=(self.name.partition('.')[0]))

        self.result.config(state=tk.NORMAL)
        self.result.delete(1.0,tk.END)
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)
        self.result_text = ("\n  The file contains "+str(n_accepted+n_rejected)+" lines:\n"
            + "\n\t-"+str(n_accepted)+" were accepted,"
            + "\n\t-"+str(n_rejected)+" were rejected.\n"
            + "\n  Accepted and rejected entries and logs were written out in:\n\n"
            + "\t"+str(self.master.shortname.partition('.')[0])+"_accepted.reads\n"
            + "\t"+str(self.master.shortname.partition('.')[0])+"_accepted.log\n"
            + "\t"+str(self.master.shortname.partition('.')[0])+"_rejected.reads\n"
            + "\t"+str(self.master.shortname.partition('.')[0])+"_rejected.log")

    def show_file_content(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Elephant file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('calf_name', 'calf_num', 'sex', 'birth', 'cw', 'caught', 'camp', 'alive', 'research',
                              'mother_num', 'mother_name')

        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=100)

        # Create fields
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)

        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i, row in enumerate(rows):
            self.tv.insert('', 'end', text=str(i+1), values=row[0:11], tags=(row[11],))

        self.tv.tag_configure(1, background='#E08E45')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][11]
        self.warningbox = tk.Text(self.warning_window, height=5, width=45)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        if warning != []:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        else:
            self.warningbox.insert(tk.END, "No problem with this elephant.")
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_elephants()

    def call_analyse(self, *args):
        analyse_elephant_file(self.master, solved=self.solved.get())
