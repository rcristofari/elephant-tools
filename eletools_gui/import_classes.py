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

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="This data has already been verified", variable=self.solved, value=1, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.radio1.grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=5, pady=5)

    def call_read_elephants(self):
        if self.name is None:
            self.name = askopenfilename(initialdir="~", filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an elephant definition file")
        self.master.shortname=os.path.split(self.name)[1]
        self.master.file_content = read_elephants(self.name, ',')

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

    def show_file_content(self):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg="#E08E45")
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

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master)
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

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_elephants()

    def call_analyse(self):
        analyse_elephant_file(self.master, solved=self.solved.get())

################################################################################
## Batch analyse an elephant file                                             ##
################################################################################

class analyse_elephant_file(tk.Frame):

    def __init__(self, master, solved):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None

        if solved==1:
            self.solved='Y'
        else:
            self.solved='N'

        self.break_loop = 0
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_elephants()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_elephants(self):
        sV=0 # Number of valid elephants so far
        sC=0 # Number of conflicting elephants so far
        sK=0 # Number of known elephants sor far
        # We scan over all elephants, including the ones flagged out during the reading process
        # These will simply be ignored.
        self.elephants = self.master.file_content[5]
        # Noumber of valid elephants is read from the partial list 'Accepted'
        n_elephs = self.master.file_content[1].__len__()

        for i,row in enumerate(self.elephants):
            # Evaluating and displaying the counter
            statenow="Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg="#E08E45", fg="#A30B37", highlightthickness=2, highlightbackground="#A30B37")
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
            # Toggle for the "stop" button to abort a long import
            if self.break_loop != 0:
                break

            # In case that row has been flagged off at the import stage
            if row[10] == 1:
                pass

            else:
                # Setting the values from the current row
                num, name, calf_num, sex, birth, cw, caught, camp, alive, research = row[0:10]
                ele = elephant(num, name, calf_num, sex, birth, cw, caught, camp, alive, research, solved=self.solved)
                ele.source(self.master.db)
                ele.check()
                w = ele.write(self.master.db)
                # Add up the flag values
                row[10] = row[10] + w[10]
                # Add the warnings field
                row[11] = w[11]
                if 1 in break_flag(row[10]) or 2 in break_flag(row[10]):
                    say = 'valid'
                    sV += 1
                elif 3 in break_flag(row[10]):
                    say = 'known'
                    sK += 1
                else:
                    say = 'conflicting'
                    sC += 1
                self.result.insert(tk.END, ("\tAnalysing elephant number "+num+"\t\t("+str(i+1)+" of "+str(n_elephs)+"): "+say+"\n"))
                self.result.update()
                self.result.see(tk.END)

        if self.break_loop == 0:
            self.result.insert(tk.END, ("\n\tFinished..!\n"))
            self.writebutton.config(state="normal")
            self.stopbutton.config(state="disabled")
        else:
            self.result.insert(tk.END, ("\n\tStopped.\n"))
            self.stopbutton.config(state="disabled")

        self.result.update()
        self.result.see(tk.END)

    def show_conflicts(self):
        rows = self.master.file_content[5]

        self.view_window = tk.Toplevel(self.master, bg="#E08E45")
        self.view_window.title("Elephant file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('num','name','calf_num','sex','birth','cw','caught','camp','alive','research')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=100)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i,row in enumerate(rows):
            if 1 in break_flag(row[10]) or 2 in break_flag(row[10]):
                self.tv.insert('','end',text=str(i+1), values=row[0:10], tags = ('valid',))
            elif 3 in break_flag(row[10]):
                self.tv.insert('','end',text=str(i+1), values=row[0:10], tags = ('known',))
            elif row[10] == 1:
                self.tv.insert('','end',text=str(i+1), values=row[0:10], tags = ('rejected',))
            else:
                self.tv.insert('','end',text=str(i+1), values=row[0:10], tags = ('conflicting',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master)
        self.warning_window.title("")
        self.warningbox = tk.Text(self.warning_window, height=10, width=65)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][10]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][11]
        if flag == 8:
            self.warningbox.insert(tk.END, 'This elephant is already in the database')
        else:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        self.warningbox.config(state=tk.DISABLED)


    def write_sql(self):
        folder = askdirectory(title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)

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

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

    def call_read_pedigree(self):

        if self.name is None:
            self.name = askopenfilename(initialdir="~", filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose a pedigree definition file")
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

    def show_file_content(self):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.geometry("600x700")
        self.view_window.resizable(False, False)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('elephant_1_id', 'elephant_2_id', 'rel', 'coef')
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

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master)
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

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_pedigree()

    def call_analyse(self):
        analyse_pedigree_file(self.master)

################################################################################
## Batch analyse an elephant file                                             ##
################################################################################

class analyse_pedigree_file(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None
        self.break_loop = 0
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_pedigree()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_pedigree(self):
        sV=0
        sC=0
        sK=0
        self.pedigrees = self.master.file_content[5]
        n_pedigree = self.pedigrees.__len__()
        for i,row in enumerate(self.pedigrees):
            statenow="Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
            if self.break_loop != 0:
                break
            if row[4] == 1:
                pass
            else:
                elephant_1_id, elephant_2_id, rel, coef  = row[0:4]
                p = pedigree(elephant_1_id, elephant_2_id, rel, coef)
                p.source(self.master.db)
                p.check()
                w = p.write(self.master.db)
                row[4] = row[4] + w[4]
                row[5] = w[5]
                if 1 in break_flag(row[4]) or 2 in break_flag(row[4]):
                    say = 'valid'
                    sV += 1
                elif 3 in break_flag(row[4]):
                    say = 'known'
                    sK += 1
                else:
                    say = 'conflicting'
                    sC += 1
                self.master.common_out.append(w)
                self.result.insert(tk.END, ("\tAnalysing relationship number "+str(i+1)+" of "+str(n_pedigree)+": "+say+"\n"))
                self.result.update()
                self.result.see(tk.END)
        if self.break_loop == 0:
            self.result.insert(tk.END, ("\n\tFinished..!\n"))
            self.writebutton.config(state="normal")
            self.stopbutton.config(state="disabled")
        else:
            self.result.insert(tk.END, ("\n\tStopped.\n"))
            self.stopbutton.config(state="disabled")
        self.result.update()
        self.result.see(tk.END)

    def show_conflicts(self):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('elephant_1_id', 'elephant_2_id', 'rel', 'coef')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=100)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i,row in enumerate(rows):
            if 1 in break_flag(row[4]) or 2 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:3], tags = ('valid',))
            elif 3 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:3], tags = ('known',))
            elif row[4] == 1:
                self.tv.insert('','end',text=str(i+1), values=row[0:3], tags = ('rejected',))
            elif 6 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:3], tags = ('missing',))
            else:
                self.tv.insert('','end',text=str(i+1), values=row[0:3], tags = ('conflicting',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.tag_configure('missing', background='#B3B3F1')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master)
        self.warning_window.title("")
        self.warningbox = tk.Text(self.warning_window, height=10, width=65)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][4]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][5]
        if flag == 8:
            self.warningbox.insert(tk.END, 'This relationship is already in the database.')
        else:
            for w in warning:
                self.warningbox.insert(tk.END, w+'\n')
        self.warningbox.config(state=tk.DISABLED)

    def write_sql(self):
        folder = askdirectory(title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)
