#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui.add_classes import *

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

        self.in_db = []
        self.in_input = []

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

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

        self.master.focus_set()
        self.master.bind('<space>', self.show_conflicts)

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
        counter = 0

        for i,row in enumerate(self.elephants):
            # Evaluating and displaying the counter
            statenow="Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
            # Toggle for the "stop" button to abort a long import
            if self.break_loop != 0:
                break

            # In case that row has been flagged off at the import stage
            if row[10] == 1:
                self.in_db.append('')
                self.in_input.append('')

            else:
                counter += 1
                # Setting the values from the current row
                num, name, calf_num, sex, birth, cw, caught, camp, alive, research = row[0:10]
                ele = elephant(num, name, calf_num, sex, birth, cw, caught, camp, alive, research, solved=self.solved, flag=int(row[10]))
                ele.source(self.master.db)
                ele.check()

                self.in_db.append(ele.in_db)
                self.in_input.append(ele.in_input)

                w = ele.write(self.master.db)
                self.master.common_out.append(w[11])
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
                self.result.insert(tk.END, ("\tAnalysing elephant number "+str(num)+"\t\t("+str(counter)+" of "+str(n_elephs)+"): "+say+"\n"))
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

    def show_conflicts(self, *args):
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

        vsb = ttk.Scrollbar(self.view_window, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=2, sticky=tk.NS)
        self.tv.configure(yscrollcommand=vsb.set)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        print(int(self.tv.item(item,"text"))-1)

        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")

        self.dbboxlabel = tk.Label(self.warning_window, text='In the database', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.dbboxlabel.grid(row=1, column=1, sticky=tk.EW)
        self.inboxlabel = tk.Label(self.warning_window, text='In the input', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.inboxlabel.grid(row=1, column=2, sticky=tk.EW)

        self.dbbox = tk.Text(self.warning_window, height=13, width=40)
        self.dbbox.grid(row=2, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)

        self.inbox = tk.Text(self.warning_window, height=13, width=40)
        self.inbox.grid(row=2, column = 2, columnspan=1, sticky=tk.EW, padx=5, pady=5)

        self.warningbox = tk.Text(self.warning_window, height=12, width=85)
        self.warningbox.grid(row=3, column = 1, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][10]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][11]

        if flag != 1:
            self.dbbox.insert(tk.END, self.in_db[int(self.tv.item(item,"text"))-1])
            self.inbox.insert(tk.END, self.in_input[int(self.tv.item(item,"text"))-1])

        if flag == 8:
            self.warningbox.insert(tk.END, 'This elephant is already in the database')
        else:
            for w in warning:
                if w.__len__() > 1:
                    self.warningbox.insert(tk.END, w+'\n')
                else:
                    self.warningbox.insert(tk.END, w)
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def write_sql(self):
        folder = askdirectory(initialdir=self.master.wdir, title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)

################################################################################
## Batch analyse a pedigree file                                              ##
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

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

        self.master.focus_set()
        self.master.bind('<space>', self.show_conflicts)

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_pedigree(self):
        sV=0
        sC=0
        sK=0
        self.pedigrees = self.master.file_content[5]
        n_pedigree = self.pedigrees.__len__()

        # Get the first rel_id index, and increment it after each insert.
        self.last_id = self.master.db.insert_pedigree(last_id_only=True)

        for i,row in enumerate(self.pedigrees):
            statenow="Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
            if self.break_loop != 0:
                break
            if row[4] == 1:
                pass
            else:
                elephant_1_id, elephant_2_id, rel, coef  = row[0:4]

                p = pedigree(elephant_1_id, elephant_2_id, rel, coef, eleph_2_is_calf=self.master.eleph_2_is_calf, flag=row[4], last_id=self.last_id)

                p.source(self.master.db)
                p.check()
                w = p.write(self.master.db)
                row[4] = row[4] + w[4]
                row[5] = w[5]

                if 1 in break_flag(row[4]) or 2 in break_flag(row[4]):
                    say = 'valid'
                    sV += 1
                    self.last_id += 1
                elif 3 in break_flag(row[4]):
                    say = 'known'
                    sK += 1
                else:
                    say = 'conflicting'
                    sC += 1
                self.master.common_out.append(w[5])
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

    def show_conflicts(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Pedigree file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        if self.master.eleph_2_is_calf is False:
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
            if 1 in break_flag(row[4]) or 2 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = ('valid',))
            elif 3 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = ('known',))
            elif row[4] == 1:
                self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = ('rejected',))
            elif 6 in break_flag(row[4]):
                self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = ('missing',))
            else:
                self.tv.insert('','end',text=str(i+1), values=row[0:4], tags = ('conflicting',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.tag_configure('missing', background='#B3B3F1')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        self.warningbox = tk.Text(self.warning_window, height=10, width=65)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][4]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][5]
        if flag == 8:
            self.warningbox.insert(tk.END, 'This relationship is already in the database.')
        else:
            for w in warning:
                print(w)
                self.warningbox.insert(tk.END, w+'\n')
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def write_sql(self):
        folder = askdirectory(initialdir=self.master.wdir, title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder, is_elephant=False)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)

################################################################################
## Batch analyse an event file                                                ##
################################################################################

class analyse_event_file(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None
        self.break_loop = 0
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_event()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

        self.master.focus_set()
        self.master.bind('<space>', self.show_conflicts)

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_event(self):
        sV=0
        sC=0
        sK=0
        self.events = self.master.file_content[5]
        n_events = self.events.__len__()
        counter = 0

        for i,row in enumerate(self.events):
            statenow="Valid: "+str(sV)+"\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

            if self.break_loop != 0:
                break

            print(row)
            if row[5] == 1:
                pass

            else:
                counter += 1
                num, date, loc, code, details = row[0:5]
                v = event(num=num, date=date, code=code, loc=loc, details=details, solved='Y', flag=row[5])
                v.source(self.master.db)
                v.check(self.master.db)
                w = v.write(self.master.db)

                row[5] = row[5] + w[5]
                row[6] = w[6]

                if 1 in break_flag(row[5]) or 2 in break_flag(row[5]):
                    say = 'valid'
                    sV += 1
                elif 3 in break_flag(row[5]):
                    say = 'known'
                    sK += 1
                else:
                    say = 'conflicting'
                    sC += 1

                if type(w[6]) is list and w[6].__len__() > 1:
                    # This is for when we add death and simultaneously update the 'alive' status.
                    self.master.common_out.append(w[6][0])
                    self.master.common_out.append(w[6][1])
                elif type(w[6]) is list and w[6].__len__() == 1:
                    self.master.common_out.append(w[6][0])
                else:
                    self.master.common_out.append(w[6])

                self.result.insert(tk.END, ("\tAnalysing event number "+str(counter)+" of "+str(n_events)+": "+say+"\n"))
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

    def show_conflicts(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Event file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('num', 'date', 'loc', 'code', 'details')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=80)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i,row in enumerate(rows):
            if 1 in break_flag(row[5]) or 2 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('valid',))
            elif 3 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('known',))
            elif row[5] == 1:
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('rejected',))
            elif 6 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('missing',))
            elif 7 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('event',))
            else:
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('conflicting',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.tag_configure('missing', background='#B3B3F1')
        self.tv.tag_configure('event', background='#CE6A85')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        vsb = ttk.Scrollbar(self.view_window, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=2, sticky=tk.NS)
        self.tv.configure(yscrollcommand=vsb.set)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        self.warningbox = tk.Text(self.warning_window, height=10, width=65)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][5]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][6]
        if flag == 8:
            self.warningbox.insert(tk.END, 'This event is already in the database.')
        else:
            if warning:
                if warning.__len__() == 1:
                    self.warningbox.insert(tk.END, str(warning))
                else:
                    for w in warning:
                        self.warningbox.insert(tk.END, str(w)+'\n')
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def write_sql(self):
        folder = askdirectory(initialdir=self.master.wdir, title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder, is_elephant=False)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)

################################################################################
## Batch analyse a measure file                                               ##
################################################################################

class analyse_measure_file(tk.Frame):

    def __init__(self, master, repvar, solvedvar):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None
        self.break_loop = 0
        self.repvar = repvar
        self.solvedvar = solvedvar
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_measures()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

        self.master.focus_set()
        self.master.bind('<space>', self.show_conflicts)
        # self.master.bind('<space>', self.update_measure_type)


    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_measures(self):
        sV=0
        sC=0
        sK=0
        self.events = self.master.file_content[5]
        n_events = self.events.__len__()
        counter = 0

        for i,row in enumerate(self.events):
            statenow = "Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

            if self.break_loop != 0:
                break

            if row[5] == 1:
                pass

            else:
                counter += 1

                measure_id, num, date, code, value  = row[0:5]

                if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', str(num)):
                    v = measure(calf_num=num, date=date, measure=code, measure_id=measure_id, value=value, replicate=self.repvar, solved=self.solvedvar, flag=row[5])
                else:
                    v = measure(num=num, date=date, measure=code, measure_id=measure_id, value=value, replicate=self.repvar, solved=self.solvedvar, flag=row[5])

                v.source(self.master.db)
                v.check(self.master.db)
                w = v.write(self.master.db)

                row[5] = row[5] + w[5]
                row[6] = w[6]

                if 1 in break_flag(row[5]) or 2 in break_flag(row[5]):
                    say = 'valid'
                    sV += 1
                elif 3 in break_flag(row[5]):
                    say = 'known'
                    sK += 1
                else:
                    say = 'conflicting'
                    sC += 1

                self.master.common_out.append(w[6])
                self.result.insert(tk.END, ("\tAnalysing measure number "+str(counter)+" of "+str(n_events)+": "+say+"\n"))
                self.result.update()
                self.result.see(tk.END)

        if self.break_loop == 0:
            self.result.insert(tk.END, "\n\tFinished..!\n")
            self.writebutton.config(state="normal")
            self.stopbutton.config(state="disabled")
        else:
            self.result.insert(tk.END, "\n\tStopped.\n")
            self.stopbutton.config(state="disabled")
        self.result.update()
        self.result.see(tk.END)

    def show_conflicts(self, *args):
        rows = self.master.file_content[5]
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Measure file "+self.master.shortname)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.tv = ttk.Treeview(self.view_window, height=32)
        self.tv['columns'] = ('set', 'elephant', 'date', 'code', 'value')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=80)
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i, row in enumerate(rows):
            if row[5] == 1:
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('rejected',))
            elif 1 in break_flag(row[5]) or 2 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('valid',))
            elif 3 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('known',))
            elif 4 in break_flag(row[5]) or 5 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('conflicting',))
            elif 6 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('missing',))
            elif 7 in break_flag(row[5]):
                self.tv.insert('','end',text=str(i+1), values=row[0:5], tags = ('measure',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.tag_configure('missing', background='#B3B3F1')
        self.tv.tag_configure('measure', background='#CE6A85')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]

        # This will be passed on to the add_measure_type class if needed
        self.master.preselect = self.master.file_content[5][int(self.tv.item(item,"text"))-1][3]
        self.master.tvitem = item

        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")
        self.warningbox = tk.Text(self.warning_window, height=10, width=65)
        self.warningbox.grid(row=1, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)
        flag = self.master.file_content[5][int(self.tv.item(item,"text"))-1][5]
        warning = self.master.file_content[5][int(self.tv.item(item,"text"))-1][6]
        if 7 in break_flag(flag):
            self.addmeasurebutton = tk.Button(self.warning_window, text="Available measures", command=self.call_add_measure)
            self.addmeasurebutton.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
            self.addmeasurebutton.grid(row=2, column=1, sticky=tk.E, padx=5, pady=5)
        if 3 in break_flag(flag):
            self.warningbox.insert(tk.END, 'This measure is already in the database.')
        else:
            for w in warning:
                if w.__len__() ==1:
                    self.warningbox.insert(tk.END, str(w))
                else:
                    self.warningbox.insert(tk.END, str(w)+'\n')
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()
        self.update_measure_type()

    def call_add_measure(self):
        # self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        # self.warning_window.title("Add a new measure type")
        self.warning_window.geometry("400x400")
        self.warning_window.db = self.master.db
        self.warning_window.lightcolour = self.master.lightcolour
        self.warning_window.darkcolour = self.master.darkcolour
        self.warning_window.grid_rowconfigure(0, weight=1)
        self.warning_window.grid_columnconfigure(0, weight=1)
        self.warning_window.grid_rowconfigure(7, weight=1)
        self.warning_window.grid_columnconfigure(5, weight=1)
        self.warning_window.file_content = self.master.file_content[5] # That's to pass the file content to the add_measure_type class
        self.master.add_measure_type_from_analyse = add_measure_type(self.warning_window, fromAnalyse=True, preselect=self.master.preselect)
        self.master.add_measure_type_from_analyse.file_content = self.master.file_content[5]

    def update_measure_type(self, *args):
        self.master.file_content[5][int(self.tv.item(self.master.tvitem, "text"))-1][3] = self.master.add_measure_type_from_analyse.select_type
        #print(self.master.tvitem,"text")
        print(self.master.file_content[5][int(self.tv.item(self.master.tvitem,"text"))-1][3])

    def write_sql(self):
        folder = askdirectory(initialdir=self.master.wdir, title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)

################################################################################
## Batch analyse a calf file                                                  ##
################################################################################

class analyse_calf_file(tk.Frame):

    def __init__(self, master, solved):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None

        if solved==1:
            self.solved='Y'
        else:
            self.solved='N'

        self.in_db = []
        self.in_input = []

        self.messages = []

        self.break_loop = 0
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_calves()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")

        self.master.focus_set()
        self.master.bind('<space>', self.show_conflicts)

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_calves(self):
        sV=0 # Number of valid elephants so far
        sC=0 # Number of conflicting elephants so far
        sK=0 # Number of known elephants sor far
        # We scan over all elephants, including the ones flagged out during the reading process
        # These will simply be ignored.

        self.calves = self.master.file_content[5]
        self.joint_flags = []
        # Number of valid elephants is read from the partial list 'Accepted'
        n_elephs = self.master.file_content[1].__len__()
        counter = 0

        for i, row in enumerate(self.calves):
            # Evaluating and displaying the counter
            statenow = "Valid: "+str(sV)+"\t\tConflicting: "+str(sC)+"\tAlready known: "+str(sK)
            self.statelabel = tk.Label(self.master, text=statenow, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=2, highlightbackground=self.master.darkcolour)
            self.statelabel.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
            # Toggle for the "stop" button to abort a long import
            if self.break_loop != 0:
                break

            # In case that row has been flagged off at the import stage
            if row[11] == 1:
                self.in_db.append('')
                self.in_input.append('')
                self.joint_flags.append(1)
                self.messages.append(self.master.file_content[5][i][12])


            else:
                counter += 1
                # Setting the values from the current row
                calf = analyse_calf(calf_name=row[0], calf_num=row[1], sex=row[2], birth=row[3], cw=row[4], caught=row[5],
                                  camp=row[6], alive=row[7], research=row[8], mother_num=row[9], mother_name=row[10],
                                  solved=self.solved, flag=int(row[11]), limit_age=28, db=self.master.db)

                self.joint_flags.append(calf[5])

                self.in_db.append(calf[6])
                self.in_input.append(calf[7])

                self.master.common_out.append(calf[0][11])
                if calf[1] is not None:
                    self.master.common_out.append(calf[1][11])
                self.messages.append(calf[3])

                if 0 in break_flag(calf[5]):
                    say = 'conflicting'
                    sC += 1
                elif all(x in break_flag(calf[5]) for x in [1, 2, 3]) or all(x in break_flag(calf[5]) for x in [2, 6]):
                    say = 'valid'
                    sV += 1
                elif any(x in break_flag(calf[5]) for x in [4, 5]):
                    say = 'known'
                    sK += 1
                else:  # redundant but better to be waterproof
                    say = 'conflicting'
                    sC += 1
                self.result.insert(tk.END, ("\tAnalysing elephant number "+str(row[1])+"\t\t("+str(counter)+" of "+str(n_elephs)+"): "+say+"\n"))
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


    def show_conflicts(self, *args):

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

        vsb = ttk.Scrollbar(self.view_window, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=2, sticky=tk.NS)
        self.tv.configure(yscrollcommand=vsb.set)

        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=100)

        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.N)

        for i, row in enumerate(rows):
            if all(x in break_flag(self.joint_flags[i]) for x in [1, 2, 3]) or all(x in break_flag(self.joint_flags[i]) for x in [2, 6]):
                self.tv.insert('','end',text=str(i+1), values=row[0:11], tags=('valid',))
            elif 4 in break_flag(self.joint_flags[i]) or 5 in break_flag(self.joint_flags[i]):
                self.tv.insert('','end',text=str(i+1), values=row[0:11], tags=('known',))
            elif 0 in break_flag(self.joint_flags[i]) and 0 in break_flag(row[11]):
                self.tv.insert('','end',text=str(i+1), values=row[0:11], tags=('rejected',))
            else:
                self.tv.insert('','end',text=str(i+1), values=row[0:11], tags=('conflicting',))

        self.tv.tag_configure('rejected', background='#E08E45')
        self.tv.tag_configure('known', background='#D5D0CD')
        self.tv.tag_configure('conflicting', background='#A30B37')
        self.tv.bind("<Double-1>", self.OnDoubleClick)

        self.view_window.focus_set()
        self.view_window.bind('<space>', self.close_view)

    def close_view(self, *args):
        self.view_window.destroy()

    def OnDoubleClick(self, event):

        item = self.tv.selection()[0]

        self.warning_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.warning_window.title("")

        self.dbboxlabel = tk.Label(self.warning_window, text='In the database', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.dbboxlabel.grid(row=1, column=1, sticky=tk.EW)
        self.inboxlabel = tk.Label(self.warning_window, text='In the input', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0)
        self.inboxlabel.grid(row=1, column=2, sticky=tk.EW)

        self.dbbox = tk.Text(self.warning_window, height=13, width=40)
        self.dbbox.grid(row=2, column = 1, columnspan=1, sticky=tk.EW, padx=5, pady=5)

        self.inbox = tk.Text(self.warning_window, height=13, width=40)
        self.inbox.grid(row=2, column = 2, columnspan=1, sticky=tk.EW, padx=5, pady=5)

        self.warningbox = tk.Text(self.warning_window, height=12, width=85)
        self.warningbox.grid(row=3, column = 1, columnspan=2, sticky=tk.EW, padx=5, pady=5)

        flag = self.joint_flags[int(self.tv.item(item,"text"))-1]
        warning = self.messages[int(self.tv.item(item,"text"))-1]

        if flag != 1:
            self.dbbox.insert(tk.END, self.in_db[int(self.tv.item(item,"text"))-1])
            self.inbox.insert(tk.END, self.in_input[int(self.tv.item(item,"text"))-1])

        if 4 in break_flag(flag) or 5 in break_flag(flag):
            self.warningbox.insert(tk.END, 'These two elephants are already in the database')
        else:
            for w in warning:
                if w.__len__() > 1:
                    self.warningbox.insert(tk.END, w+'\n')
                else:
                    self.warningbox.insert(tk.END, w)
        self.warningbox.config(state=tk.DISABLED)
        self.warning_window.focus_set()
        self.warning_window.bind('<Escape>', self.close_warning)

    def close_warning(self, *args):
        self.warning_window.destroy()

    def write_sql(self):
        folder = askdirectory(title='Choose SQL file directory...')
        parse_output(self.master.common_out+self.messages, self.master.db, folder, conflicts_only=True)
        self.result.insert(tk.END, ("\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)


################################################################################
## Batch analyse a logbook file                                                ##
################################################################################

class analyse_logbook_file(tk.Frame):

    def __init__(self, master, solved=False):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None
        self.__solved = solved
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_analyse_logbook()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.result = tk.Text(self.master, height=25, width=65)
        self.result.grid(row=2, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)
        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.writebutton.grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)
        self.writebutton.config(state="disabled")
        self.master.focus_set()

    def call_analyse_logbook(self):

        lb = logbook(self.master.file_content, self.master.db)
        lb.source()
        lb.check()
        lw = lb.write()

        if any(x in [2, 4] for x in break_flag(lw[1])):
            self.result.insert(tk.END, "\nThe logbook is valid and can be input in the database")
        else:
            for line in lw[2]:
                self.result.insert(tk.END, "\n" + line + "\n")

        for line in lw[2]:
            self.master.common_out.append(line)

        self.writebutton.config(state="normal")
        self.result.update()
        self.result.see(tk.END)

    def write_sql(self):
        folder = askdirectory(initialdir=self.master.wdir, title='Choose SQL file directory...')
        parse_output(self.master.common_out, self.master.db, folder, is_elephant=False)
        self.result.insert(tk.END, ("\n\n------------------------------------------------------------------\n\n\tFiles written in "+folder))
        self.result.update()
        self.result.see(tk.END)
