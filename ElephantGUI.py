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

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        self.master.geometry("500x500")
        self.master.resizable(False, False)


    def create_widgets(self):
        self.master.menubar = tk.Menu(self)

        filemenu = tk.Menu(self.master.menubar, tearoff=0)
        filemenu.add_command(label="Import elephants", command=self.read_elephants_prompt)
        filemenu.add_command(label="Import pedigrees", command=self.read_pedigree_prompt)
        filemenu.add_command(label="Import events", command=self.notimplemented)
        filemenu.add_command(label="Import measures", command=self.notimplemented)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command=self.quit)
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
        self.master.menubar.add_cascade(label="Search", menu=searchmenu)
        self.master.menubar.entryconfig("Search", state='disabled')

        addmenu = tk.Menu(self.master.menubar, tearoff=0)
        addmenu.add_command(label="Add an elephant", command=self.notimplemented)
        addmenu.add_command(label="Add a relationship", command=self.notimplemented)
        addmenu.add_command(label="Add an event", command=self.notimplemented)
        addmenu.add_command(label="Add a measure", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Add a measure type", command=self.notimplemented)
        addmenu.add_command(label="Add an event type", command=self.notimplemented)
        addmenu.add_separator()
        addmenu.add_command(label="Update living status", command=self.notimplemented)
        self.master.menubar.add_cascade(label="Add", menu=addmenu)
        self.master.menubar.entryconfig("Add", state='disabled')

        dbmenu = tk.Menu(self.master.menubar, tearoff = 0)
        dbmenu.add_command(label="Connexion", command=self.goconnect)
        dbmenu.add_command(label="MySQL dump", command=self.notimplemented)
        self.master.menubar.add_cascade(label="Database", menu=dbmenu)

        self.master.config(menu=self.master.menubar)

    def goconnect(self):
        dbconnect(self.master)

    def read_elephants_prompt(self):
        read_elephant_file(self.master)

    def read_pedigree_prompt(self):
        read_pedigree_file(self.master)

    def gofindeleph(self):
        findeleph(self.master, back = 0)

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
        self.userlabel = tk.Label(self.master, text="User:").grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.pwdlabel = tk.Label(self.master, text="Password:").grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.hostlabel = tk.Label(self.master, text="Host:").grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Database:").grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Port:").grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
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
        self.detailslabel = tk.Label(self.master, text="Details (optional, if entering new data):")
        self.detailslabel.grid(row=6, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.details = tk.Text(self.master, height=5, width=45)
        self.details.grid(row=7, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.connectbutton = tk.Button(self.master, text='Connect', width=15, command=self.connect_to_db)
        self.disconnectbutton = tk.Button(self.master, text='Disconnect', width=15, command=self.disconnect_from_db)
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

        self.numlabel = tk.Label(self.master, text="Number:")
        self.numlabel.grid(row=1, column=1, sticky = tk.W, padx=0, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, columnspan=2, sticky = tk.EW, padx=0, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1)
        self.radio1.grid(row=2, column=2, sticky=tk.W, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2)
        self.radio2.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.findbutton = tk.Button(self.master, text='Find', width=15, command=self.call_get_elephant).grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)
        self.treebutton = tk.Button(self.master, text='Show tree', width=15, command=self.call_show_matriline).grid(row=3, column=3, sticky=tk.E, padx=0, pady=5)

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
        self.view_window = tk.Toplevel(self.master)
        self.view_window.title("Pedigree view")
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
        self.backbutton = tk.Button(self.view_window, text='Close', width=20, command=self.view_window.destroy)
        self.backbutton.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.saveimgbutton = tk.Button(self.view_window, width=20, text='Save as Image', command=self.save_tree)
        self.saveimgbutton.grid(row=1, column=4, sticky=tk.EW, padx=5, pady=5)
        self.savenexbutton = tk.Button(self.view_window, text='Save as Nexus', width=20, command=self.save_newick)
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

        self.reloadbutton = tk.Button(self.master, text='Reload', width=15, command=self.reload_file)
        self.reloadbutton.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_file_content)
        self.showfilebutton.grid(row=2, column=2, sticky=tk.EW, padx=5, pady=5)

        self.analysebutton = tk.Button(self.master, text='Analyse', width=15, command=self.call_analyse)
        self.analysebutton.grid(row=2, column=3, sticky=tk.E, padx=5, pady=5)

        self.radio1 = tk.Radiobutton(self.master, text="This data has already been verified", variable=self.solved, value=1)
        self.radio1.grid(row=3, column=2, columnspan=2, sticky=tk.E, padx=5, pady=5)

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
        self.view_window = tk.Toplevel(self.master)
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

        self.stopbutton = tk.Button(self.master, text='Stop', width=15, command=self.stop_loop)
        self.stopbutton.grid(row=3, column=1, sticky=tk.W, padx=0, pady=5)

        self.showfilebutton = tk.Button(self.master, text='Show', width=15, command=self.show_conflicts)
        self.showfilebutton.grid(row=3, column=2, sticky=tk.EW, padx=5, pady=5)

        self.writebutton = tk.Button(self.master, text='Write an SQL file', width=15, command=self.write_sql)
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
            self.statelabel = tk.Label(self.master, text=statenow)
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

        self.view_window = tk.Toplevel(self.master)
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
## Call the main application                                                  ##
################################################################################

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root).grid(sticky="nsew")
   root.grid_rowconfigure(0, weight=1)
   root.grid_columnconfigure(0, weight=1)
   root.grid_rowconfigure(9, weight=1)
   root.grid_columnconfigure(4, weight=1)
   root.mainloop()
