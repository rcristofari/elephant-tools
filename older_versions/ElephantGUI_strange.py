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
## Main application window                                                    ##
################################################################################

class MainApplication(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.create_widgets()
        self.master.common_out = [] #This will be the main MySQL and error out
        self.goconnect()

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        self.master.geometry("500x500")
        self.master.resizable(False, False)
        self.master.background_image = tk.PhotoImage(file='./__resources/background.png')
        self.master.background_label = tk.Label(self.master, image=self.master.background_image)
        self.master.background_label.place(x=0, y=0, relwidth=1, relheight=1)


    def create_widgets(self):
        self.master.menubar = tk.Menu(self)

        filemenu = tk.Menu(self.master.menubar, tearoff=0)
        filemenu.add_command(label="Import elephants", command=self.read_elephants_prompt)
        filemenu.add_command(label="Import pedigrees", command=self.read_pedigree_prompt)
        filemenu.add_command(label="Import events", command=self.notimplemented)
        filemenu.add_command(label="Import measures", command=self.notimplemented)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.quit)
        filemenu.config(bg="#E08E45", fg="#A30B37")
        self.master.menubar.add_cascade(label="File", menu=filemenu)
        self.master.menubar.entryconfig("File", state='disabled')

        searchmenu = tk.Menu(self.master.menubar, tearoff=0)
        searchmenu.add_command(label="Find an elephant", command=self.gofindeleph)
        searchmenu.add_command(label="Find a relationship", command=self.notimplemented)
        searchmenu.add_command(label="Find an event", command=self.notimplemented)
        searchmenu.add_command(label="Find a measure", command=self.notimplemented)
        searchmenu.add_separator()
        searchmenu.add_command(label="Make a measure set", command=self.notimplemented)
        searchmenu.add_separator()
        searchmenu.add_command(label="Advanced search", command=self.notimplemented)
        searchmenu.config(bg="#E08E45", fg="#A30B37")
        self.master.menubar.add_cascade(label="Search", menu=searchmenu)
        self.master.menubar.entryconfig("Search", state='disabled')

        addmenu = tk.Menu(self.master.menubar, tearoff=0)
        addmenu.add_command(label="Add an elephant", command=self.call_add_elephants)
        addmenu.add_command(label="Add a relationship", command=self.notimplemented)
        addmenu.add_command(label="Add an event", command=self.notimplemented)
        addmenu.add_command(label="Add a measure", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Add a measure type", command=self.notimplemented)
        addmenu.add_command(label="Add an event type", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Update living status", command=self.notimplemented)
        addmenu.config(bg="#E08E45", fg="#A30B37")
        self.master.menubar.add_cascade(label="Add", menu=addmenu)
        self.master.menubar.entryconfig("Add", state='disabled')

        dbmenu = tk.Menu(self.master.menubar, tearoff = 0)
        dbmenu.add_command(label="Connexion", command=self.goconnect)
        dbmenu.add_command(label="MySQL dump", command=self.notimplemented)
        dbmenu.config(bg="#E08E45", fg="#A30B37")
        self.master.menubar.add_cascade(label="Database", menu=dbmenu)

        self.master.menubar.config(bg="#E08E45", fg="#A30B37")
        self.master.config(menu=self.master.menubar)


    def goconnect(self):
        dbconnect(self.master)

    def read_elephants_prompt(self):
        read_elephant_file(self.master)

    def read_pedigree_prompt(self):
        read_pedigree_file(self.master)

    def gofindeleph(self):
        findeleph(self.master, back = 0)

    def call_add_elephants(self):
        add_elephants(self.master)

    def notimplemented(self):
        print("Not implemented yet")

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

        self.numlabel = tk.Label(self.master, text="Number:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, columnspan=2, sticky = tk.EW, padx=0, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.radio1.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.radio2.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_get_elephant, bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)
        self.treebutton = tk.Button(self.master, text='Show tree', width=15, command=self.call_show_matriline, bg="#E08E45", fg="#A30B37", highlightthickness=0).grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)

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
        self.backbutton = tk.Button(self.view_window, text='Close', width=20, command=self.view_window.destroy, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.backbutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.saveimgbutton = tk.Button(self.view_window, width=20, text='Save as Image', command=self.save_tree, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.saveimgbutton.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        self.savenexbutton = tk.Button(self.view_window, text='Save as Nexus', width=20, command=self.save_newick, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.savenexbutton.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=5)


    def call_show_matriline(self):
        matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

    def back_to_find(self):
        findeleph(self.master, back = 1)

    def save_tree(self):
        treefile = asksaveasfilename(title='Save tree image...', initialdir='~', defaultextension='.png')
        self.background.save(treefile)

    def save_newick(self):
        nexusfile = asksaveasfilename(title='Save tree definition...', initialdir='~', defaultextension='.nex')
        nexus_tree(self.master.newick, nexusfile)

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


################################################################################
## Manually add some elephants                                                ##
################################################################################

class add_elephants(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.sex = tk.StringVar()
        self.cw = tk.StringVar()
        self.alive = tk.StringVar()
        self.research = tk.StringVar()
        self.stringvar1 = tk.StringVar()
        self.stringvar1.trace("w", self.valid_entry)
        self.stringvar2 = tk.StringVar()
        self.stringvar2.trace("w", self.valid_entry)
        self.stringvar3 = tk.StringVar()
        self.stringvar3.trace("w", self.valid_entry)
        self.stringvar4 = tk.StringVar()
        self.stringvar4.trace("w", self.valid_entry)
        self.sex.set('UKN')
        self.cw.set('UKN')
        self.alive.set('UKN')
        self.research.set('N')
        self.rows = []
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
        ########## First column:
        self.numlabel = tk.Label(self.master, text="Number:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.numlabel.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.numentry = tk.Entry(self.master, width=10, textvariable=self.stringvar1)
        self.numentry.grid(row=1, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.namelabel = tk.Label(self.master, text="Name:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.namelabel.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.nameentry = tk.Entry(self.master, width=10)
        self.nameentry.grid(row=2, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.calfnumlabel = tk.Label(self.master, text="Calf number:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.calfnumlabel.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.calfnumentry = tk.Entry(self.master, width=10)
        self.calfnumentry.grid(row=3, column=2, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.sexlabel = tk.Label(self.master, text="Sex:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexlabel.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.sexradio1 = tk.Radiobutton(self.master, text="F", variable=self.sex, value='F', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio1.grid(row=4, column=2, sticky=tk.W)
        self.sexradio2 = tk.Radiobutton(self.master, text="M", variable=self.sex, value='M', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio2.grid(row=4, column=3, sticky=tk.E)
        self.sexradio3 = tk.Radiobutton(self.master, text="?", variable=self.sex, value='UKN', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.sexradio3.grid(row=4, column=4, sticky=tk.E)

        self.birthlabel = tk.Label(self.master, text="Birth (DMY):", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.birthlabel.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.birthDD = tk.Entry(self.master, width=2, textvariable=self.stringvar2)
        self.birthDD.grid(row=5, column=2, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthMM = tk.Entry(self.master, width=2, textvariable=self.stringvar3)
        self.birthMM.grid(row=5, column=3, columnspan=1, sticky=tk.W, padx=1, pady=5)
        self.birthYYYY = tk.Entry(self.master, width=4, textvariable=self.stringvar4)
        self.birthYYYY.grid(row=5, column=4, columnspan=1, sticky=tk.EW, padx=1, pady=5)

        ########## Second column:
        self.cwlabel = tk.Label(self.master, text="Captive:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwlabel.grid(row=1, column=5, sticky=tk.W, padx=5, pady=5)
        self.cwradio1 = tk.Radiobutton(self.master, text="C", variable=self.cw, value='captive', command=self.disable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio1.grid(row=1, column=6, sticky=tk.W)
        self.cwradio2 = tk.Radiobutton(self.master, text="W", variable=self.cw, value='wild', command=self.enable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio2.grid(row=1, column=7, sticky=tk.E)
        self.cwradio3 = tk.Radiobutton(self.master, text="?", variable=self.cw, value='UKN', command=self.disable_caught, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.cwradio3.grid(row=1, column=8, sticky=tk.E)

        self.caughtlabel = tk.Label(self.master, text="Age caught:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.caughtlabel.grid(row=2, column=5, sticky=tk.W, padx=5, pady=5)
        self.caughtentry = tk.Entry(self.master, width=10)
        self.caughtentry.grid(row=2, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        self.caughtentry.config(state="disabled")

        self.camplabel = tk.Label(self.master, text="Camp:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.camplabel.grid(row=3, column=5, sticky=tk.W, padx=5, pady=5)
        self.campentry = tk.Entry(self.master, width=10)
        self.campentry.grid(row=3, column=6, columnspan=3, sticky=tk.EW, padx=5, pady=5)

        self.alivelabel = tk.Label(self.master, text="Alive:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.alivelabel.grid(row=4, column=5, sticky=tk.W, padx=5, pady=5)
        self.aliveradio1 = tk.Radiobutton(self.master, text="Y", variable=self.alive, value='Y', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio1.grid(row=4, column=6, sticky=tk.W)
        self.aliveradio2 = tk.Radiobutton(self.master, text="N", variable=self.alive, value='N', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio2.grid(row=4, column=7, sticky=tk.E)
        self.aliveradio3 = tk.Radiobutton(self.master, text="?", variable=self.alive, value='UKN', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.aliveradio3.grid(row=4, column=8, sticky=tk.E)

        self.researchlabel = tk.Label(self.master, text="Research:", bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchlabel.grid(row=5, column=5, sticky=tk.W, padx=5, pady=5)
        self.researchradio1 = tk.Radiobutton(self.master, text="Y", variable=self.research, value='Y', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchradio1.grid(row=5, column=6, sticky=tk.W)
        self.researchradio2 = tk.Radiobutton(self.master, text="N", variable=self.research, value='N', bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.researchradio2.grid(row=5, column=7, sticky=tk.W)
        # self.researchradio3 = tk.Radiobutton(self.master, text="?", variable=self.research, value=3, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        # self.researchradio3.grid(row=5, column=8, sticky=tk.E)

        self.addbutton = tk.Button(self.master, text='Add', width=15, command=self.add_row, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.addbutton.grid(row=6, column=1, columnspan=4, sticky=tk.EW, padx=5, pady=5)
        self.checkbutton = tk.Button(self.master, text='Verify', width=15, command=self.check_entries, bg="#E08E45", fg="#A30B37", highlightthickness=0)
        self.checkbutton.grid(row=6, column=5, columnspan=4, sticky=tk.EW, padx=5, pady=5)

        self.tv = ttk.Treeview(self.master, height=6)
        self.tv['columns'] = ('Num','Name','Calf','S','B','CW','Cg','Cp','A','R')
        self.tv.heading("#0", text='#')
        self.tv.column("#0", anchor='center', width=20)
        # Create fields
        for c in self.tv['columns']:
            self.tv.heading(c, text=c)
            self.tv.column(c, anchor='w', width=25)
        self.tv.grid(row=7, column=1, columnspan=8, padx=5, pady=5, sticky=tk.EW)

        self.tv.bind("<Double-1>", self.OnDoubleClick)

    def valid_entry(self, *args):
        s1 = self.stringvar1.get()
        s2 = self.stringvar2.get()
        s3 = self.stringvar3.get()
        s4 = self.stringvar4.get()
        if s1 and s2 and s3 and s4:
            self.addbutton.config(state='normal')
        else:
            self.addbutton.config(state='disabled')

    def disable_caught(self):
        self.caughtentry.config(state="disabled")
        self.caughtentry.update()

    def enable_caught(self):
        self.caughtentry.config(state="normal")
        self.caughtentry.update()

    def add_row(self):
        birth = str(self.birthYYYY.get())+'-'+str(self.birthMM.get())+'-'+str(self.birthDD.get())
        row = [self.numentry.get(), self.nameentry.get(), self.calfnumentry.get(), self.sex.get(), birth, self.cw.get(), self.caughtentry.get(), self.campentry.get(), self.alive.get(), self.research.get()]
        self.rows.append(row)
        for item in self.tv.get_children():
            self.tv.delete(item)
        i = 1
        for row in self.rows:
            i += 1
            self.tv.insert('','end',text=str(i), values=row[0:10], tags = ('smalltext',))
        self.tv.tag_configure('smalltext', font=('Helvetica',8))
        self.clear_entries()

    def clear_entries(self):
        self.numentry.delete(0, tk.END)
        self.nameentry.delete(0, tk.END)
        self.calfnumentry.delete(0, tk.END)
        self.birthYYYY.delete(0, tk.END)
        self.birthMM.delete(0, tk.END)
        self.birthDD.delete(0, tk.END)
        self.caughtentry.delete(0, tk.END)
        self.campentry.delete(0, tk.END)
        self.sex.set('UKN')
        self.cw.set('UKN')
        self.alive.set('UKN')
        self.research.set('N')

    def OnDoubleClick(self, event):
        item = self.tv.selection()[0]
        # self.tv.delete(item)
        r = self.rows.pop(int(self.tv.item(item,"text"))-2)
        for item in self.tv.get_children():
            self.tv.delete(item)
        i = 1
        for row in self.rows:
            i += 1
            self.tv.insert('','end',text=str(i), values=row[0:10], tags = ('smalltext',))
        self.clear_entries()
        self.numentry.insert(10,r[0])
        self.nameentry.insert(10,r[1])
        self.calfnumentry.insert(10,r[2])
        self.sex.set(r[3])
        self.birthYYYY.insert(10, r[4].partition('-')[0])
        self.birthMM.insert(10, r[4].partition('-')[2].partition('-')[0])
        self.birthDD.insert(10, r[4].partition('-')[2].partition('-')[0])
        self.cw.set(r[5])
        self.caughtentry.insert(10, r[6])
        self.campentry.insert(10, r[7])
        self.alive.set(r[8])
        self.research.set(r[9])

    def check_entries(self):
        pass
################################################################################
## Call the main application                                                  ##
################################################################################

if __name__ == '__main__':
   root = tk.Tk(className='eletools')
   main_app =  MainApplication(root).grid(sticky="nsew")
   root.grid_rowconfigure(0, weight=1)
   root.grid_columnconfigure(0, weight=1)
   root.grid_rowconfigure(10, weight=1)
   root.grid_columnconfigure(9, weight=1)
   root.mainloop()
