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
# from eletools_gui.db_classes import *
# from eletools_gui.import_classes import *
# from eletools_gui.add_classes import *

################################################################################
## Search for an elephant                                                     ##
################################################################################

class findeleph(tk.Frame):

    def __init__(self, master, back):
        self.back = back
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.age = tk.IntVar()
        self.age.set(1)
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

        self.numlabel = tk.Label(self.master, text="Number:", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, columnspan=2, sticky = tk.EW, padx=0, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio1.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.radio2.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_get_elephant, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour).grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)
        self.treebutton = tk.Button(self.master, text='Show tree', width=15, command=self.call_show_matriline, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour).grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)

        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=4, column = 1, columnspan=3, sticky=tk.EW, padx=0, pady=5)

    def call_get_elephant(self):
        self.result.config(state=tk.NORMAL)
        if self.back == 0:
            if self.age.get() == 1:
                self.eleph = self.master.db.get_elephant(num = self.e1.get())
                self.master.eleph_now = self.eleph
            elif self.age.get() == 2:
                self.eleph = self.master.db.get_elephant(calf_num = self.e1.get())
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
            born = self.eleph[5]
            now = datetime.now().date()
            age = round(((now - born).days / 365.25))
            self.result.delete(1.0,tk.END)
            self.result_text = ("\nIndex:\t\t"+str(self.eleph[0])
                +"\nNumber:\t\t"+str(self.eleph[1])
                +"\nName:\t\t"+str(self.eleph[2])
                +"\nCalf number:\t\t"+str(self.eleph[3])
                +"\nSex:\t\t"+str(self.eleph[4])
                +"\nBirth date:\t\t"+str(self.eleph[5])+" ("+str(age)+" y.b.p.)"
                +"\nOrigin:\t\t"+str(self.eleph[6])
                +"\nAge at capture:\t"+str(self.eleph[7])
                +"\nCamp:\t\t"+str(self.eleph[8])
                +"\nAlive:\t\t"+str(self.eleph[9])
                +"\nResearch:\t\t"+str(self.eleph[10]))
            self.result.insert(tk.END, self.result_text)
            self.result.update()
            self.result.config(state=tk.DISABLED)

    def call_show_matriline(self):
        self.master.newick = matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

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
        self.backbutton = tk.Button(self.view_window, text='Close', width=20, command=self.view_window.destroy, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.backbutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.saveimgbutton = tk.Button(self.view_window, width=20, text='Save as Image', command=self.save_tree, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.saveimgbutton.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        self.savenexbutton = tk.Button(self.view_window, text='Save as Nexus', width=20, command=self.save_newick, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savenexbutton.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)


    def call_show_matriline(self):
        matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

    def back_to_find(self):
        findeleph(self.master, back = 1)

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
        self.moderadio1.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.moderadio2=tk.Radiobutton(self.master, text="One elephant", variable=self.run_mode, value=2, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.moderadio2.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.moderadio2.config(state='disabled')
        if self.run_mode.get() == 0:
            self.entrylabel = tk.Label(self.master, text="Mother's number:\t\t", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
            self.entrylabel.grid(row=2, column=1, sticky=tk.E, padx=0, pady=5)
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
        self.age=tk.IntVar()
        self.age.set(1)
        self.stringvar = tk.StringVar()
        self.stringvar.trace("w", self.enable_search)
        self.create_widgets()
        self.available_measures = []
        self.selected_measures = []

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
        self.choosebutton = tk.Button(self.master, text='Select measures', width=25, command=self.choose_measures, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.choosebutton.grid(row=3, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)
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
        self.exportbutton.grid(row=5, column=3, columnspan=2, sticky = tk.W, padx=5, pady=5)

    def enable_search(self, *args):
        x = self.stringvar.get()
        if x:
            self.choosebutton.config(state='normal')
        else:
            self.choosebutton.config(state='disabled')

    def choose_measures(self):
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

        self.tv1 = ttk.Treeview(self.view_window, height=20)
        self.tv1['columns'] = ('Measure','Unit','Details')
        self.tv1.heading("#0", text='#')
        self.tv1.column("#0", anchor='center', width=100)
        for c in self.tv1['columns']:
            self.tv1.heading(c, text=c)
            self.tv1.column(c, anchor='w', width=100)
        self.tv1.grid(row=2, column=1, padx=5, pady=5, sticky=tk.N)

        self.tv2 = ttk.Treeview(self.view_window, height=20)
        self.tv2['columns'] = ('Measure','Unit','Details')
        self.tv2.heading("#0", text='#')
        self.tv2.column("#0", anchor='center', width=100)
        for c in self.tv2['columns']:
            self.tv2.heading(c, text=c)
            self.tv2.column(c, anchor='w', width=100)
        self.tv2.grid(row=2, column=2, padx=5, pady=5, sticky=tk.N)
        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)

        self.donebutton = tk.Button(self.view_window, text='Done', width=15, command=self.fetch_values, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)        # Select measures button opens a window that allows to select any number of measures
        self.donebutton.grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)

        if self.available_measures == []:
            self.available_measures = self.master.db.get_measure_list()
            self.available_measures.sort(key=lambda k: (k[0]))
            for i,m in enumerate(self.available_measures):
                self.tv1.insert('','end',text=str(i+1), values=m[0:3])
        else:
            for i,m in enumerate(self.available_measures):
                self.tv1.insert('','end',text=str(i+1), values=m[0:3])
            for i,m in enumerate(self.selected_measures):
                self.tv2.insert('','end',text=str(i+1), values=m[0:3])

    def OnDoubleClick1(self, event):
        item = self.tv1.selection()[0]
        id = int(self.tv1.item(item, "text"))-1
        transfer = self.available_measures.pop(id)
        self.selected_measures.append(transfer)
        self.available_measures.sort(key=lambda k: (k[0]))
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)
        for i,m in enumerate(self.available_measures):
            self.tv1.insert('','end',text=str(i+1), values=m[0:3])
        for i,m in enumerate(self.selected_measures):
            self.tv2.insert('','end',text=str(i+1), values=m[0:3])

    def OnDoubleClick2(self, event):
        item = self.tv2.selection()[0]
        id = int(self.tv2.item(item, "text"))-1
        transfer = self.selected_measures.pop(id)
        self.available_measures.append(transfer)
        self.available_measures.sort(key=lambda k: (k[0]))
        for item in self.tv1.get_children():
            self.tv1.delete(item)
        for item in self.tv2.get_children():
            self.tv2.delete(item)
        for i,m in enumerate(self.available_measures):
            self.tv1.insert('','end',text=str(i+1), values=m[0:3])
        for i,m in enumerate(self.selected_measures):
            self.tv2.insert('','end',text=str(i+1), values=m[0:3])

    def fetch_values(self):
        measure_str = '('
        for m in self.selected_measures:
            measure_str = measure_str+"'"+m[0]+"',"
        measure_str = measure_str.rstrip(',')+')'
        self.measures = self.master.db.get_measure_values(self.e1.get(), measure_str)
        for item in self.tv.get_children():
            self.tv.delete(item)
        for i,m in enumerate(self.measures):
            self.tv.insert('','end',text=str(i+1), values=m[0:6])
        self.view_window.destroy()

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, defaultextension='.csv')
        with open(filename,"w") as f:
            f.write("Set,Measure,Date,Value,Unit\n")
            for x in self.measures:
                f.write(str(x[0])+',')
                f.write(str(x[1])+',')
                f.write(str(x[2].strftime('%Y-%m-%d'))+',')
                f.write(str(x[3])+',')
                f.write(str(x[4]))
                f.write('\n')

################################################################################
## Search for events on an elephant                                         ##
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
        self.classes_types = []
        self.selected_types = []
        self.selected_classes = []
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
        self.view_window.title("Select measures")
        self.view_window.grid_columnconfigure(0, weight=1)
        self.view_window.grid_columnconfigure(3, weight=1)
        self.view_window.grid_rowconfigure(0, weight=1)
        self.view_window.grid_rowconfigure(2, weight=1)

        self.tv1label = tk.Label(self.view_window, text="Available measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.tv1label.grid(row=1, column=1, sticky=tk.EW, pady=5)
        self.tv1label = tk.Label(self.view_window, text="Selected measures", bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
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
        self.classes_types = self.master.db.get_event_list()
        classes_all = []
        for c in self.classes_types:
            classes_all.append(c[0])
        self.classes = list(set(classes_all))
        self.classes.sort(key=lambda k: (k[0]))
        self.classes_list = list(set(classes_all))

        self.types = []
        for t in self.classes_types:
            if t in self.types:
                pass
            else:
                self.types.append(t)

        for c in self.classes_list:
            globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
        for t in self.types:
            name = t[0]
            self.tv1.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))

        self.tv1.bind("<Double-1>", self.OnDoubleClick1)
        self.tv2.bind("<Double-1>", self.OnDoubleClick2)


    def OnDoubleClick1(self, event):

        item = self.tv1.selection()[0]
        selection = self.tv1.item(item, "text")

        if selection in self.classes_list: # Then a main category has been clicked, move all subcategories too

            # Isolate the clicked class
            index=None
            select_class = self.tv1.item(item, "text")
            for i,c in enumerate(self.classes):
                if c == select_class:
                    index = i
            transfer = self.classes.pop(index)
            self.selected_classes.append(transfer)
            self.selected_classes.sort(key=lambda k: (k[0]))

            #Clear the boxes
            for item in self.tv1.get_children():
                self.tv1.delete(item)
            for item in self.tv2.get_children():
                self.tv2.delete(item)

            # Fill back the classes:
            for c in self.classes:
                globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.selected_classes:
                globals()[c] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            self.type_buffer = []
            for i,t in enumerate(self.types):
                name = t[0]
                if t[0] in self.selected_classes:
                    self.selected_types.append(t)
                else:
                    self.type_buffer.append(t)
                    self.tv1.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))
            self.types = self.type_buffer
            for st in self.selected_types:
                sname = st[0]
                self.tv2.insert(globals()[sname], "end", text=st[1], values=(st[2],), tags = ('type',))

        else:
            select_type = self.tv1.item(item, "text")
            index=None
            for i,t in enumerate(self.types):
                if t[1] == select_type:
                    index = i
            transfer = self.types.pop(index)
            self.selected_types.append(transfer)
            self.selected_types.sort(key=lambda k: (k[1]))
            for item in self.tv1.get_children():
                self.tv1.delete(item)
            for item in self.tv2.get_children():
                self.tv2.delete(item)
            for c in self.classes:
                globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for t in self.types:
                name = t[0]
                self.tv1.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))
            for c in self.classes:
                globals()[c] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))
            for t in self.selected_types:
                name = t[0]
                self.tv2.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))

    def OnDoubleClick2(self, event):
        item = self.tv2.selection()[0]
        selection = self.tv2.item(item, "text")
        print(selection, self.classes_list)
        if selection in self.classes_list:
            # Isolate the clicked class
            index=None
            select_class = self.tv2.item(item, "text")
            for i,c in enumerate(self.selected_classes):
                if c == select_class:
                    index = i
            transfer = self.selected_classes.pop(index)
            self.classes.append(transfer)
            self.classes.sort(key=lambda k: (k[0]))

            #Clear the boxes
            for item in self.tv1.get_children():
                self.tv1.delete(item)
            for item in self.tv2.get_children():
                self.tv2.delete(item)

            # Fill back the classes:
            for c in self.classes:
                globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.selected_classes:
                globals()[c] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            # Add in the types:
            self.type_buffer = []
            for t in self.selected_types:
                name = t[0]
                if name in self.classes:
                    self.types.append(t)
                else:
                    self.type_buffer.append(t)
                    self.tv2.insert(globals()[name], "end", text=st[1], values=(st[2],), tags = ('type',))

            self.selected_types = self.type_buffer

            for st in self.types:
                sname = st[0]
                self.tv1.insert(globals()[sname], "end", text=st[1], values=(st[2],), tags = ('type',))

        else:
            select_type = self.tv2.item(item, "text")
            index=None
            for i,t in enumerate(self.selected_types):
                if t[1] == select_type:
                    index = i
            transfer = self.selected_types.pop(index)
            self.types.append(transfer)
            self.types.sort(key=lambda k: (k[1]))
            for item in self.tv1.get_children():
                self.tv1.delete(item)
            for item in self.tv2.get_children():
                self.tv2.delete(item)
                    #Change the classes / selected classes by a clearer available/selected classes
            for c in self.classes:
                globals()[c] = self.tv1.insert("", "end", text=c, open = True, tags = ('class',))
            for c in self.classes:
                globals()[c] = self.tv2.insert("", "end", text=c, open = True, tags = ('class',))

            for t in self.types:
                name = t[0]
                self.tv1.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))
            for t in self.selected_types:
                name = t[0]
                self.tv2.insert(globals()[name], "end", text=t[1], values=(t[2],), tags = ('type',))

    def fetch_values(self):
        measure_str = '('
        for m in self.selected_measures:
            measure_str = measure_str+"'"+m[0]+"',"
        measure_str = measure_str.rstrip(',')+')'
        self.measures = self.master.db.get_measure_values(self.e1.get(), measure_str)
        for item in self.tv.get_children():
            self.tv.delete(item)
        for i,m in enumerate(self.measures):
            self.tv.insert('','end',text=str(i+1), values=m[0:6])
        self.view_window.destroy()

    def write_csv(self):
        filename = asksaveasfilename(initialdir=self.master.wdir, defaultextension='.csv')
        with open(filename,"w") as f:
            f.write("Set,Measure,Date,Value,Unit\n")
            for x in self.measures:
                f.write(str(x[0])+',')
                f.write(str(x[1])+',')
                f.write(str(x[2].strftime('%Y-%m-%d'))+',')
                f.write(str(x[3])+',')
                f.write(str(x[4]))
                f.write('\n')
