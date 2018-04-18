#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
import csv
from datetime import datetime
from eletools import *
from eletools_gui.plot_classes import plot_measures
import matplotlib.pyplot as plt

################################################################################
## Search for an elephant                                                     ##
################################################################################

class findeleph(tk.Frame):

    def __init__(self, master, back):
        self.back = back
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.lifeline_control = None
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        if self.back == 1:
            self.call_get_elephant()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):

        self.numlabel = tk.Label(self.master, text="Number:\t", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=3, columnspan=1, sticky = tk.EW, padx=0, pady=5)

        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_get_elephant, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.findbutton.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=0, pady=2)

        self.plotbutton = tk.Button(self.master, text='Measures', width=15, command=self.call_plot_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.plotbutton.grid(row=3, column=1, sticky=tk.EW, padx=0, pady=2)
        self.treebutton = tk.Button(self.master, text='Pedigree', width=15, command=self.call_show_matriline, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.treebutton.grid(row=3, column=3, sticky=tk.EW, padx=0, pady=2)
        self.linebutton = tk.Button(self.master, text='Lifeline', width=15, command=self.call_lifeline, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.linebutton.grid(row=4, column=1, sticky=tk.EW, padx=0, pady=2)
        self.censorbutton = tk.Button(self.master, text='Censoring', width=15, command=self.call_censoring, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.censorbutton.grid(row=4, column=3, sticky=tk.EW, padx=0, pady=2)
        self.plotbutton.config(state=tk.DISABLED)
        self.treebutton.config(state=tk.DISABLED)
        self.linebutton.config(state=tk.DISABLED)
        self.censorbutton.config(state=tk.DISABLED)

        self.result = tk.Text(self.master, height=16, width=45)
        self.result.grid(row=5, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

        self.master.focus_set()
        self.master.bind("<Return>", self.call_get_elephant)
        self.master.bind("<space>", self.call_show_matriline)

    def call_get_elephant(self, *args):
        self.close_plot()
        self.result.config(state=tk.NORMAL)
        if self.back == 0:
            if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', self.e1.get()):
                self.eleph = self.master.db.get_elephant(calf_num = self.e1.get())
                self.master.eleph_now = self.eleph
            else:
                self.eleph = self.master.db.get_elephant(num = self.e1.get())
                self.master.eleph_now = self.eleph

        elif self.back == 1:
            self.back = 0
            self.eleph = self.master.eleph_now

        if self.eleph is None:
            self.result.delete(1.0,tk.END)
            self.result_text = ("This elephant does not exist in the database")
            self.result.insert(tk.END, self.result_text)
            self.result.config(state=tk.DISABLED)
        else:
            # Activate the other options:
            self.plotbutton.config(state=tk.NORMAL)
            self.treebutton.config(state=tk.NORMAL)
            self.linebutton.config(state=tk.NORMAL)
            self.censorbutton.config(state=tk.NORMAL)

            born = self.eleph[5]
            now = datetime.now().date()
            age = round(((now - born).days / 365.25))
            self.result.delete(1.0,tk.END)

            # Get censoring information and display summary:
            censor = censor_elephant(db=self.master.db, id=self.eleph[0], survival='./__resources/Sx_curves', cutoff=0.05)
            if censor[0] == 1: # Elephant is dead
                censorstr = 'No - died on ' + datetime.strftime(censor[2], '%Y-%m-%d') + '\n\t\tat age ' + str(round((censor[2] - censor[1]).days/365.25)) + ' (' + censor[3] + ')'
            else:
                if censor[5] >= 0.9:
                    censorstr = 'Yes\n'
                elif censor[5] < 0.9 and censor[5] >= 0.75:
                    censorstr = 'Probably\n'
                elif censor[5] < 0.75 and censor[5] >= 0.05:
                    censorstr = 'Possibly\n'
                else:
                    censorstr = 'Probably not - exp. death in ' + str(censor[3].year) + '\n'


            self.result_text = ("\n Index:\t\t"+str(self.eleph[0])
                +"\n--------------------------------------------------"
                +"\n Number:\t\t"+str(self.eleph[1])
                +"\n Name:\t\t"+str(self.eleph[2])
                +"\n Calf number:\t\t"+str(self.eleph[3])
                +"\n Sex:\t\t"+str(self.eleph[4])
                +"\n Birth date:\t\t"+str(self.eleph[5])+" ("+str(age)+" y.b.p.)"
                +"\n Origin:\t\t"+str(self.eleph[6])
                +"\n Age at capture:\t\t"+str(self.eleph[7])
                +"\n Camp:\t\t"+str(self.eleph[8])
                +"\n Alive:\t\t"+censorstr
                +"\n--------------------------------------------------"
                +"\n Research:\t\t"+str(self.eleph[10]))
            self.result.insert(tk.END, self.result_text)
            self.result.update()
            self.result.config(state=tk.DISABLED)

    def call_show_matriline(self, *args):
        self.master.newick = matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

    def call_lifeline(self, *args):
        self.lifeline_control = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.lifeline_control.title("Lifeline options")
        self.lifeline_control.grid_columnconfigure(0, weight=1)
        self.lifeline_control.grid_columnconfigure(2, weight=1)
        self.lifeline_control.grid_rowconfigure(0, weight=1)
        self.lifeline_control.grid_rowconfigure(8, weight=1)
        self.lifeline_control.geometry("200x200")
        self.lifeline_control.resizable(False, False)
        self.lifeline_control.lightcolour = self.master.lightcolour
        self.lifeline_control.darkcolour = self.master.darkcolour
        self.lifeline_control.db = self.master.db
        self.lifeline_control.id = self.eleph[0]

        self.logs = tk.BooleanVar()
        self.logs.set(True)
        self.taming = tk.BooleanVar()
        self.taming.set(True)
        self.breeding = tk.BooleanVar()
        self.breeding.set(True)
        self.censoring = tk.BooleanVar()
        self.censoring.set(True)
        self.events = tk.BooleanVar()
        self.events.set(False)
        self.measures = tk.BooleanVar()
        self.measures.set(False)

        # Put a watch on these buttons to auto refresh
        self.lifeline_control.logsbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Logbooks", variable=self.logs, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.logsbutton.grid(row=1, column=1, sticky=tk.W)
        self.lifeline_control.tamingbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Taming", variable=self.taming, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.tamingbutton.grid(row=2, column=1, sticky=tk.W)
        self.lifeline_control.breedingbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Breeding", variable=self.breeding, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.breedingbutton.grid(row=3, column=1, sticky=tk.W)
        self.lifeline_control.censoringbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Censoring", variable=self.censoring, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.censoringbutton.grid(row=4, column=1, sticky=tk.W)
        self.lifeline_control.eventsbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Events", variable=self.events, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.eventsbutton.grid(row=5, column=1, sticky=tk.W)
        self.lifeline_control.measuresbutton  = tk.Checkbutton(self.lifeline_control, command=self.call_create_lifeline, text="Measures", variable=self.measures, onvalue=True, offvalue=False, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.lifeline_control.measuresbutton.grid(row=6, column=1, sticky=tk.W)
        self.lifeline_control.protocol("WM_DELETE_WINDOW", self.close_plot)
        create_lifeline(self.lifeline_control.db, id=self.lifeline_control.id, logs=self.logs.get(), taming=self.taming.get(), breeding=self.breeding.get(), censoring=self.censoring.get(), events=self.events.get(), measures=self.measures.get())

    def call_create_lifeline(self, *args):
        plt.close()
        create_lifeline(self.lifeline_control.db, id=self.lifeline_control.id, logs=self.logs.get(), taming=self.taming.get(), breeding=self.breeding.get(), censoring=self.censoring.get(), events=self.events.get(), measures=self.measures.get())

    def close_plot(self):
        if self.lifeline_control:
            plt.close()
            self.lifeline_control.destroy()

    def call_censoring(self, *args):
        self.censor_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.censor_window.title("Censoring details")
        # self.view_window.group(self.master)
        self.censor_window.grid_columnconfigure(0, weight=1)
        self.censor_window.grid_columnconfigure(4, weight=1)
        self.censor_window.grid_rowconfigure(0, weight=1)
        self.censor_window.grid_rowconfigure(4, weight=1)
        self.censor_window.geometry("350x300")
        self.censor_window.resizable(False, False)
        self.censor_window.lightcolour = self.master.lightcolour
        self.censor_window.darkcolour = self.master.darkcolour
        self.censor_window.db = self.master.db
        censor_date(self.censor_window, call_censoring_from_eleph=self.e1.get())

    def call_plot_measures(self):
        self.master.plot_measures = plot_measures(self.master, id=self.eleph[0])

################################################################################
## Display matriline                                                          ##
################################################################################

class show_matriline(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        # self.clear_frame()
        self.create_widgets()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        self.view_window = tk.Toplevel(self.master, bg=self.master.darkcolour)
        self.view_window.title("Pedigree view")
        # self.view_window.group(self.master)
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(2, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)
        self.view_window.geometry("600x700")
        self.view_window.resizable(False, False)

        img = Image.open('./tree.png','r')
        img_w, img_h = img.size
        if img_h > img_w:
            newsize= round(600*(600/img_h)),600
            img = img.resize(newsize, Image.ANTIALIAS)
            img.save('./tree.png')
        img_w, img_h = img.size
        self.background = Image.new('RGBA', (600, 600), (255, 255, 255, 255))
        bg_w, bg_h = self.background.size
        offset = (round((bg_w - img_w) / 2), round((bg_h - img_h) / 2))
        self.background.paste(img, offset)
        self.background.save('./tree.png')

        self.treebox = tk.Text(self.view_window, height=50, width=100)
        self.tree=tk.PhotoImage(file='./tree.png')
        self.treebox.image_create(tk.END, image=self.tree)
        self.treebox.grid(row=2, column = 1, columnspan=4)
        self.backbutton = tk.Button(self.view_window, text='Close', width=20, command=self.close_tree, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.backbutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.saveimgbutton = tk.Button(self.view_window, width=20, text='Save as Image', command=self.save_tree, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.saveimgbutton.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        self.savenexbutton = tk.Button(self.view_window, text='Save as Nexus', width=20, command=self.save_newick, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savenexbutton.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)

        self.view_window.focus_set()
        self.view_window.bind("<Escape>", self.close_tree)

    def call_show_matriline(self):
        matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

    def close_tree(self, *args):
        self.view_window.destroy()

    def save_tree(self):
        treefile = asksaveasfilename(title='Save tree image...', initialdir=self.master.wdir, defaultextension='.png')
        self.background.save(treefile)

    def save_newick(self):
        nexusfile = asksaveasfilename(title='Save tree definition...', initialdir=self.master.wdir, defaultextension='.nex')
        nexus_tree(self.master.newick, nexusfile)

################################################################################
## Control age gaps between births                                            ##
################################################################################

class age_gaps(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.run_mode=tk.IntVar()
        self.run_mode.set(0)
        self.create_widgets()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        # add a tracker here
        self.moderadio1=tk.Radiobutton(self.master, text="One elephant", variable=self.run_mode, value=0, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.moderadio1.grid(row=1, column=1, sticky=tk.W, padx=0, pady=5)
        self.moderadio2=tk.Radiobutton(self.master, text="All elephants", variable=self.run_mode, value=2, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.moderadio2.grid(row=1, column=2, sticky=tk.W, padx=0, pady=5)
        self.moderadio2.config(state='disabled')

        if self.run_mode.get() == 0:
            self.entrylabel = tk.Label(self.master, text="Mother's number:\t\t", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
            self.entrylabel.grid(row=2, column=1, sticky=tk.W, padx=0, pady=5)
            self.numentry = tk.Entry(self.master, width=25)
            self.numentry.grid(row=2, column=2, columnspan=1, sticky = tk.E, padx=0, pady=5)
            self.searchbutton=tk.Button(self.master, text='Search', width=15, command=self.call_get_all_offsprings, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
            self.searchbutton.grid(row=3, column=2, sticky=tk.E, pady=5)
            self.tv = ttk.Treeview(self.master, height=8)
            self.tv['columns'] = ('ID','Number','Birth','Gap')
            self.tv.heading("#0", text='#')
            self.tv.column("#0", anchor='center', width=20)
            # Create fields
            for c in self.tv['columns']:
                self.tv.heading(c, text=c)
                self.tv.column(c, anchor='center', width=25)
            self.tv.grid(row=4, column=1, columnspan=2, sticky=tk.EW)

    def call_get_all_offsprings(self):
        for item in self.tv.get_children():
            self.tv.delete(item)
        self.result = self.master.db.get_all_offsprings(num = self.numentry.get(), age_gap=True, pairs = True, limit_age = 28)
        print(self.result)
        for i,r in enumerate(self.result):
            if r[4]==0:
                self.tv.insert('','end',text=str(i+1), values=r[0:4], tags = ('valid',))
            elif r[4]==1:
                self.tv.insert('','end',text=str(i+1), values=r[0:4], tags = ('conflict',))
        self.tv.tag_configure('conflict', background='#A30B37')

################################################################################
## Search for measures on an elephant                                         ##
################################################################################

class find_measure(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        # self.age=tk.IntVar()
        # self.age.set(1)
        self.stringvar = tk.StringVar()
        self.stringvar.trace("w", self.enable_search)
        self.create_widgets()
        self.__available_types = []
        self.__selected_types = []
        self.__available_classes = []
        self.__selected_classes = []

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()

    def create_widgets(self):
        self.numlabel = tk.Label(self.master, text="Number:\t", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master, width=10, textvariable=self.stringvar)
        self.e1.grid(row=1, column=3, columnspan=2, sticky = tk.EW, padx=0, pady=5)
        # self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        # self.radio1.grid(row=1, column=3, sticky=tk.E, padx=5, pady=5)
        # self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        # self.radio2.grid(row=1, column=4, sticky=tk.E, padx=5, pady=5)
        self.plotbutton = tk.Button(self.master, text='Graph', width=20, command=self.call_plot_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.plotbutton.grid(row=3, column=1, columnspan=2, sticky = tk.EW, padx=5, pady=5)
        self.plotbutton.config(state='disabled')
        self.choosebutton = tk.Button(self.master, text='Select measures', width=25, command=self.choose_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.choosebutton.grid(row=3, column=3, columnspan=2, sticky = tk.EW, padx=5, pady=5)
        self.choosebutton.config(state='disabled')

        self.tv = ttk.Treeview(self.master, height=10)
        self.tv['columns'] = ('Set', 'Measure', 'Date', 'Value', 'Unit')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=8)
        self.tv.heading('Set', text="Set")
        self.tv.column('Set', anchor='center', width=8)
        self.tv.heading('Measure', text="Measure")
        self.tv.column('Measure', anchor='w', width=40)
        self.tv.heading('Date', text="Date")
        self.tv.column('Date', anchor='w', width=40)
        self.tv.heading('Value', text="Value")
        self.tv.column('Value', anchor='w', width=30)
        self.tv.heading('Unit', text="Unit")
        self.tv.column('Unit', anchor='w', width=20)
        self.tv.grid(row=4, column=1, columnspan=4, padx=5, pady=5, sticky=tk.EW)

        self.exportbutton = tk.Button(self.master, text='Export as file', width=20, command=self.write_csv, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.exportbutton.grid(row=5, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)


        self.master.focus_set()
        self.master.bind('<Return>', self.choose_measures)

    def enable_search(self, *args):
        x = self.stringvar.get()
        if x:
            self.choosebutton.config(state='normal')
            self.plotbutton.config(state='normal')
        else:
            self.choosebutton.config(state='disabled')
            self.plotbutton.config(state='disabled')

    def choose_measures(self, *args):
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Select measures")
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(3, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv1label = tk.Label(self.view_window, text="Available measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.tv1label = tk.Label(self.view_window, text="Selected measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=2, sticky=tk.EW, pady=5)

        self.tv1 = ttk.Treeview(self.view_window, height=20, columns=('Unit','Description'), show="tree")
        self.tv1.heading("#0", text='Class')
        self.tv1.heading("#1", text='Type')
        self.tv1.column("#0", width = 120, stretch=0)
        self.tv1.column("#1", width = 20, stretch=0)
        self.tv1.heading('Unit', text='Unit')
        self.tv1.column('Unit', anchor='w', width=50)
        self.tv1.heading('Description', text='Description')
        self.tv1.column('Description', anchor='w', width=200)
        self.tv1.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)

        self.tv2 = ttk.Treeview(self.view_window, height=20, columns=('Unit','Description'), show="tree")
        self.tv2.heading("#0", text='Class')
        self.tv2.heading("#1", text='Type')
        self.tv2.column("#0", width = 120, stretch=0)
        self.tv2.column("#1", width = 20, stretch=0)
        self.tv2.heading('Unit', text='Unit')
        self.tv2.column('Unit', anchor='w', width=50)
        self.tv2.heading('Description', text='Description')
        self.tv2.column('Description', anchor='w', width=200)
        self.tv2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.N)
        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

        self.donebutton = tk.Button(self.view_window, text='Done', width=15, command=self.fetch_values, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.donebutton.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        # Retrieve the classes ('disease','accident',...) and types (detailed events)
        if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', self.e1.get()):
            self.__classes_types = self.master.db.get_measure_list(calf_num=self.e1.get())
        else:
            self.__classes_types = self.master.db.get_measure_list(num=self.e1.get())

        # if self.age.get() == 1:
        #     self.__classes_types = self.master.db.get_measure_list(num=self.e1.get())
        # elif self.age.get() == 2:
        #     self.__classes_types = self.master.db.get_measure_list(calf_num=self.e1.get())
        # else:
        #     self.__classes_types = []

        classes_all = []
        for c in self.__classes_types:
            classes_all.append(c[0])
        self.__classes = list(set(classes_all))
        self.__classes.sort(key=lambda k: (k[0]))

        self.__types = []
        for t in self.__classes_types:
            if t in self.__types:
                pass
            else:
                self.__types.append(t)

        self.__available_classes = [] #This is to break the vicious binding
        for c in self.__classes:
            self.__available_classes.append(c)
        self.__available_types = []
        for t in self.__types:
            self.__available_types.append(t)

        for c in self.__available_classes:
            globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
        for t in self.__available_types:
            name = t[0]
            self.tv1.insert(globals()[name], "end", text=t[1], values=t[2:4], tags = ('type',))

        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

    def OnDoubleClick1(self, event):

        item = self.tv1.selection()[0]
        __selection = self.tv1.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__available_classes):
                if c == __selection:
                    break
            transfer = self.__available_classes.pop(i)
            self.__selected_classes.append(transfer)
            self.__selected_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            at=[]
            # st=[]
            for t in self.__available_types:
                if t[0] in self.__available_classes:
                    at.append(t)
                elif t[0] in self.__selected_classes:
                    self.__selected_types.append(t)


            self.__available_types = at
            self.__available_types.sort(key=lambda k: (k[1]))
            # self.__selected_types = st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

        else:

            for i,t in enumerate(self.__available_types):
                if t[1] == __selection:
                    break
            transfer = self.__available_types.pop(i)
            self.__selected_types.append(transfer)
            self.__selected_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            ac=[]
            sc=[]
            for t in self.__available_types:
                ac.append(t[0])
            self.__available_classes = list(set(ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                sc.append(t[0])
            self.__selected_classes = list(set(sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

    def OnDoubleClick2(self, event):

        item = self.tv2.selection()[0]
        __selection = self.tv2.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__selected_classes):
                if c == __selection:
                    break
            transfer = self.__selected_classes.pop(i)
            self.__available_classes.append(transfer)
            self.__available_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            # __at=[]
            __st=[]
            for t in self.__selected_types:
                if t[0] in self.__available_classes:
                    self.__available_types.append(t)
                elif t[0] in self.__selected_classes:
                    __st.append(t)

            # self.__available_types = __at
            self.__available_types.sort(key=lambda k: (k[1]))
            self.__selected_types = __st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

        else:

            for i,t in enumerate(self.__selected_types):
                if t[1] == __selection:
                    break
            transfer = self.__selected_types.pop(i)
            self.__available_types.append(transfer)
            self.__available_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            __ac=[]
            __sc=[]
            for t in self.__available_types:
                __ac.append(t[0])
            self.__available_classes = list(set(__ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                __sc.append(t[0])
            self.__selected_classes = list(set(__sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=t[2:4], tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=t[2:4], tags = ('type',))

    def fetch_values(self):
        measure_str = '('
        for m in self.__selected_types:
            measure_str = measure_str+"'"+m[1]+"',"
        measure_str = measure_str.rstrip(',')+')'
        self.measures = self.master.db.get_measure_values(num=self.e1.get(), measurelist=measure_str)

        # We also get details on the elephant (num, name, sex, and birth date)
        self.details = self.master.db.get_elephant(num=self.e1.get())

        for item in self.tv.get_children():
            self.tv.delete(item)
        try:
            for i,m in enumerate(self.measures):
                self.tv.insert('','end',text=str(i+1), values=m[0:6])
        except TypeError:
                pass
        self.view_window.destroy()

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, initialfile=('E_'+str(self.e1.get())+'_measures.csv'), defaultextension='.csv')
        with open(filename,"w") as f:
            f.write("Set,Measure,Date,Value,Unit\n")
            for x in self.measures:
                f.write(str(x[0])+',')
                f.write(str(x[1])+',')
                f.write(str(x[2].strftime('%Y-%m-%d'))+',')
                f.write(str(x[3])+',')
                f.write(str(x[4]))
                f.write('\n')

    def call_plot_measures(self):
        # self.plot_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        # self.plot_window.title("Measure graph")
        # # self.plot_window.geometry("400x400")
        # self.plot_window.db = self.master.db
        # self.plot_window.lightcolour = self.master.lightcolour
        # self.plot_window.darkcolour = self.master.darkcolour
        # self.plot_window.grid_rowconfigure(0, weight=1)
        # self.plot_window.grid_columnconfigure(0, weight=1)
        # self.plot_window.grid_rowconfigure(7, weight=1)
        # self.plot_window.grid_columnconfigure(5, weight=1)
        # self.master.plot_measures = plot_measures(self.plot_window, self.measures, self.details)
        if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', self.e1.get()):
            self.__id=self.master.db.get_elephant(calf_num=self.e1.get())[0]
        else:
            self.__id=self.master.db.get_elephant(num=self.e1.get())[0]
        self.master.plot_measures = plot_measures(self.master, id=self.__id)

################################################################################
## Search for events on an elephant                                           ##
################################################################################

class find_event(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.age=tk.IntVar()
        self.age.set(1)
        self.stringvar = tk.StringVar()
        self.stringvar.trace("w", self.enable_search)
        self.create_widgets()
        self.__classes_types = []
        self.__available_types = []
        self.__available_classes = []
        self.__selected_types = []
        self.__selected_classes = []
        self.type_buffer = []

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
            widget.grid_forget()

    def create_widgets(self):
        self.numlabel = tk.Label(self.master, text="Number:\t", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master, width=10, textvariable=self.stringvar)
        self.e1.grid(row=1, column=2, sticky = tk.W, padx=0, pady=5)
        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=1, column=3, sticky=tk.E, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio2.grid(row=1, column=4, sticky=tk.E, padx=5, pady=5)
        self.radio2.config(state='disabled') ### USE THAT
        self.choosebutton = tk.Button(self.master, text='Select events', width=25, command=self.choose_events, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.choosebutton.grid(row=3, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)
        self.choosebutton.config(state='disabled')

        self.tv = ttk.Treeview(self.master, height=10)
        self.tv['columns'] = ('Date', 'Place', 'Class', 'Type')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=8)
        self.tv.heading('Date', text="Date")
        self.tv.column('Date', anchor='w', width=40)
        self.tv.heading('Place', text="Place")
        self.tv.column('Place', anchor='w', width=30)
        self.tv.heading('Class', text="Class")
        self.tv.column('Class', anchor='w', width=30)
        self.tv.heading('Type', text="Type")
        self.tv.column('Type', anchor='w', width=30)
        self.tv.grid(row=4, column=1, columnspan=4, padx=5, pady=5, sticky=tk.EW)

        self.exportbutton = tk.Button(self.master, text='Export as file', width=20, command=self.write_csv, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.exportbutton.grid(row=5, column=3, columnspan=2, sticky = tk.W, padx=5, pady=5)

    def enable_search(self, *args):
        x = self.stringvar.get()
        if x:
            self.choosebutton.config(state='normal')
        else:
            self.choosebutton.config(state='disabled')

    def choose_events(self):
        self.view_window = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.view_window.title("Select events")
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(3, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv1label = tk.Label(self.view_window, text="Available events", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.tv1label = tk.Label(self.view_window, text="Selected events", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=2, sticky=tk.EW, pady=5)

        self.tv1 = ttk.Treeview(self.view_window, height=20, columns=('Description'), show="tree")
        self.tv1.heading("#0", text='Class')
        self.tv1.heading("#1", text='Type')
        self.tv1.column("#0", width = 120, stretch=0)
        self.tv1.column("#1", width = 20, stretch=0)
        self.tv1.heading('Description', text='Description')
        self.tv1.column('Description', anchor='w', width=200)
        self.tv1.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)

        self.tv2 = ttk.Treeview(self.view_window, height=20, columns=('Description'), show="tree")
        self.tv2.heading("#0", text='Class')
        self.tv2.heading("#1", text='Type')
        self.tv2.column("#0", width = 120, stretch=0)
        self.tv2.column("#1", width = 20, stretch=0)
        self.tv2.heading('Description', text='Description')
        self.tv2.column('Description', anchor='w', width=200)
        self.tv2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.N)
        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

        self.donebutton = tk.Button(self.view_window, text='Done', width=15, command=self.fetch_values, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.donebutton.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        # Retrieve the classes ('disease','accident',...) and types (detailed events)
        self.__classes_types = self.master.db.get_event_list()

        classes_all = []
        for c in self.__classes_types:
            classes_all.append(c[0])
        self.__classes = list(set(classes_all))
        self.__classes.sort(key=lambda k: (k[0]))

        self.__types = []
        for t in self.__classes_types:
            if t in self.__types:
                pass
            else:
                self.__types.append(t)

        self.__available_classes = [] #This is to break the vicious binding
        for c in self.__classes:
            self.__available_classes.append(c)
        self.__available_types = []
        for t in self.__types:
            self.__available_types.append(t)

        for c in self.__available_classes:
            globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
        for t in self.__available_types:
            name = t[0]
            self.tv1.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))

        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

    def OnDoubleClick1(self, event):

        item = self.tv1.selection()[0]
        __selection = self.tv1.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__available_classes):
                if c == __selection:
                    break
            transfer = self.__available_classes.pop(i)
            self.__selected_classes.append(transfer)
            self.__selected_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            at=[]
            # st=[]
            for t in self.__available_types:
                if t[0] in self.__available_classes:
                    at.append(t)
                elif t[0] in self.__selected_classes:
                    self.__selected_types.append(t)


            self.__available_types = at
            self.__available_types.sort(key=lambda k: (k[1]))
            # self.__selected_types = st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=(t[2],), tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=(t[2],), tags = ('type',))

        else:

            for i,t in enumerate(self.__available_types):
                if t[1] == __selection:
                    break
            transfer = self.__available_types.pop(i)
            self.__selected_types.append(transfer)
            self.__selected_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            ac=[]
            sc=[]
            for t in self.__available_types:
                ac.append(t[0])
            self.__available_classes = list(set(ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                sc.append(t[0])
            self.__selected_classes = list(set(sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=(t[2],), tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=(t[2],), tags = ('type',))

    def OnDoubleClick2(self, event):

        item = self.tv2.selection()[0]
        __selection = self.tv2.item(item, "text")

        #Clear the boxes
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)

        if __selection in self.__classes: # Then a main category has been clicked, move all subcategories too
            # Isolate the clicked class
            for i,c in enumerate(self.__selected_classes):
                if c == __selection:
                    break
            transfer = self.__selected_classes.pop(i)
            self.__available_classes.append(transfer)
            self.__available_classes.sort(key=lambda k: (k[0]))

            # Fill back the classes:
            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            # __at=[]
            __st=[]
            for t in self.__selected_types:
                if t[0] in self.__available_classes:
                    self.__available_types.append(t)
                elif t[0] in self.__selected_classes:
                    __st.append(t)

            # self.__available_types = __at
            self.__available_types.sort(key=lambda k: (k[1]))
            self.__selected_types = __st
            self.__selected_types.sort(key=lambda k: (k[1]))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=(t[2],), tags = ('type',))
            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=(t[2],), tags = ('type',))

        else:

            for i,t in enumerate(self.__selected_types):
                if t[1] == __selection:
                    break
            transfer = self.__selected_types.pop(i)
            self.__available_types.append(transfer)
            self.__available_types.sort(key=lambda k: (k[1]))

            # Rebuild the *_classes lists
            __ac=[]
            __sc=[]
            for t in self.__available_types:
                __ac.append(t[0])
            self.__available_classes = list(set(__ac))
            self.__available_classes.sort(key=lambda k: (k[0]))
            for t in self.__selected_types:
                __sc.append(t[0])
            self.__selected_classes = list(set(__sc))
            self.__selected_classes.sort(key=lambda k: (k[0]))

            for c in self.__available_classes:
                globals()[c+'a'] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.__selected_classes:
                globals()[c+'s'] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.__available_types:
                name = t[0]
                self.tv1.insert(globals()[name+'a'], "end", text=t[1], values=(t[2],), tags = ('type',))

            for t in self.__selected_types:
                name = t[0]
                self.tv2.insert(globals()[name+'s'], "end", text=t[1], values=(t[2],), tags = ('type',))

    def fetch_values(self):
        self.__fetch_types = []
        for t in self.__selected_types:
            self.__fetch_types.append(t[1])
        print(self.__fetch_types)

        __event_str = '('
        for e in self.__fetch_types:
            __event_str = __event_str+"'"+e+"',"
        __event_str = __event_str.rstrip(',')+')'

        self.__events = self.master.db.get_event_values(self.e1.get(), __event_str)

        for item in self.tv.get_children():
            self.tv.delete(item)

        for i,e in enumerate(self.__events):
            self.tv.insert('','end',text=str(i+1), values=e[0:4])

        self.view_window.destroy()
        self.__available_types = []
        self.__selected_types = []
        self.__available_classes = []
        self.__selected_classes = []

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, initialfile=('E_'+str(self.e1.get())+'_events.csv'), defaultextension='.csv')
        with open(filename,"w") as f:
            f.write("Date,Place,Class,Type\n")
            for x in self.__events:
                f.write(str(x[0])+',')
                f.write(str(x[1])+',')
                f.write(str(x[2]+','))
                f.write(str(x[3]))
                f.write('\n')

################################################################################
## Assess whether an elephant is alive or not now                             ##
################################################################################

class censor_date(tk.Frame):

    def __init__(self, master, call_censoring_from_eleph=None):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.call_censoring_from_eleph = call_censoring_from_eleph
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
        self.numlabel = tk.Label(self.master, text="Number:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, columnspan=2, sticky = tk.EW, padx=5, pady=5)
        self.cutofflabel = tk.Label(self.master, text="P cut-off:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.cutofflabel.grid(row=2, column=1, sticky = tk.W, padx=0, pady=5)
        self.e2 = tk.Entry(self.master, width=8)
        self.e2.insert(10, 0.05)
        self.e2.grid(row=2, column=2, columnspan=1, sticky = tk.EW, padx=5, pady=5)
        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_censor_date, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.findbutton.grid(row=2, column=3, sticky=tk.EW, padx=5, pady=5)
        self.result = tk.Text(self.master, height=10, width=47)
        self.result.grid(row=3, column = 1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.master.focus_set()
        self.master.bind("<Return>", self.call_censor_date)

        if self.call_censoring_from_eleph is not None:
            self.e1.insert(10, self.call_censoring_from_eleph)
            self.call_censor_date()
            self.e1.config(state=tk.DISABLED)

    def call_censor_date(self, *args):
        self.result.config(state=tk.NORMAL)
        self.__cutoff = float(self.e2.get())
        try:
            if re.search(r'[\d]{4}[a-zA-Z]{1}[\w]+', self.e1.get()):
                self.__eleph = self.master.db.get_elephant(calf_num = self.e1.get())
            else:
                self.__eleph = self.master.db.get_elephant(num = self.e1.get())
            self.__id = self.__eleph[0]
        except:
            print("Impossible to connect to the database.")

        censor = censor_elephant(db=self.master.db, id=self.__id, survival='./__resources/Sx_curves', cutoff=self.__cutoff)

        if censor is not None:
            if censor[0] == 0: # The elephant has no known death date
                out = ( "-----------------------------------------------" +
                    "\n Birth date: " + censor[1].strftime('%Y-%m-%d') +
                    "\n Last seen on: " + censor[2].strftime('%Y-%m-%d') +
                    "\n (Event type: " + censor[6] + ")" +
                    "\n Expected final bow: " + censor[3].strftime('%Y') + " (at age " + str(censor[4]) + ")" +
                    "\n-----------------------------------------------")

                if censor[5] > self.__cutoff:
                    verdict = ("\n Probability that it is alive today: "+str(round(censor[5],3)))
                else:
                    verdict = ("\n This elephant is certainly quite dead by now.")
                self.result.delete(1.0,tk.END)
                self.result.insert(tk.END, "\n Selected model: "+censor[-1]+'\n')
                self.result.insert(tk.END, out)
                self.result.insert(tk.END, verdict)
                self.result.config(state=tk.DISABLED)

            elif censor[0] == 1: # The elephant has a known death date
                out = ("\n This elephant is quite dead."+
                    "\n-----------------------------------------------" +
                    "\n Birth date: " + censor[1].strftime('%Y-%m-%d') +
                    "\n Final bow: " + censor[2].strftime('%Y-%m-%d') + " (at age " + str(int((censor[2]-censor[1]).days//362.25)) + ")" +
                    "\n Cause of death: " + censor[3] +
                    "\n-----------------------------------------------")
                self.result.delete(1.0,tk.END)
                self.result.insert(tk.END, out)
                self.result.config(state=tk.DISABLED)
