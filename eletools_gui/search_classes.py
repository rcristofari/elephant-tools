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

        self.numlabel = tk.Label(self.master, text="Number:", bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, columnspan=2, sticky = tk.EW, padx=0, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
        self.radio1.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
        self.radio2.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_get_elephant, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45").grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)
        self.treebutton = tk.Button(self.master, text='Show tree', width=15, command=self.call_show_matriline, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45").grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)

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
        self.view_window = tk.Toplevel(self.master, bg="#A30B37")
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
        self.backbutton = tk.Button(self.view_window, text='Close', width=20, command=self.view_window.destroy, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
        self.backbutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.saveimgbutton = tk.Button(self.view_window, width=20, text='Save as Image', command=self.save_tree, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
        self.saveimgbutton.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        self.savenexbutton = tk.Button(self.view_window, text='Save as Nexus', width=20, command=self.save_newick, bg="#E08E45", fg="#A30B37", highlightthickness=0, activebackground="#A30B37", activeforeground="#E08E45")
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
