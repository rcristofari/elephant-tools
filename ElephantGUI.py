#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image
from ElephantTools import *

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
        self.master.geometry("600x700")
        self.master.resizable(False, False)


    def create_widgets(self):
        self.master.menubar = tk.Menu(self)

        filemenu = tk.Menu(self.master.menubar, tearoff=0)
        # filemenu.add_separator()
        filemenu.add_command(label="Import Elephants", command=self.read_elephants_prompt)
        filemenu.add_command(label="Quit", command=self.quit)
        self.master.menubar.add_cascade(label="File", menu=filemenu)
        self.master.menubar.entryconfig("File", state='disabled')

        searchmenu = tk.Menu(self.master.menubar, tearoff=0)
        searchmenu.add_command(label="Find an elephant", command=self.gofindeleph)
        searchmenu.add_command(label="Advanced search", command=self.gofindeleph)
        self.master.menubar.add_cascade(label="Search", menu=searchmenu)
        self.master.menubar.entryconfig("Search", state='disabled')

        dbmenu = tk.Menu(self.master.menubar, tearoff = 0)
        dbmenu.add_command(label="Connexion", command=self.goconnect)
        self.master.menubar.add_cascade(label="Database", menu=dbmenu)

        self.master.config(menu=self.master.menubar)

    def goconnect(self):
        dbconnect(self.master)

    def read_elephants_prompt(self):
        read_elephant_file(self.master)
#        name = askopenfilename(initialdir="~", filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an elephant definition file")
#        read_elephants(name, ',')

    def gofindeleph(self):
        findeleph(self.master, back = 0)

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
        self.userlabel = tk.Label(self.master, text="User:").grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.pwdlabel = tk.Label(self.master, text="Password:").grid(row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.hostlabel = tk.Label(self.master, text="Host:").grid(row=3, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.dblabel = tk.Label(self.master, text="Database:").grid(row=4, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master, show='*')
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)
        self.e3.insert(10,"localhost")
        self.e4.insert(10,"mep")
        self.e1.grid(row=1, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.e2.grid(row=2, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.e3.grid(row=3, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.e4.grid(row=4, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.connectbutton = tk.Button(self.master, text='Connect', command=self.connect_to_db)
        self.disconnectbutton = tk.Button(self.master, text='Disconnect', command=self.disconnect_from_db)
        self.connectbutton.grid(row=5, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.disconnectbutton.grid(row=5, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.disconnectbutton.config(state="disabled")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)

    def connect_to_db(self):
        try:
            self.master.db = mysqlconnect(self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get())
            self.master.stamp = self.master.db.stamp() #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            self.master.common_out.append(self.master.stamp)
            print("You are connected!")
        except: #still an error here.
            print("Impossible to connect to database.")
        self.master.menubar.entryconfig("File", state='normal')
        self.master.menubar.entryconfig("Search", state='normal')
        self.disconnectbutton.config(state="normal")
        self.connectbutton.config(state="disabled")

    def disconnect_from_db(self):
        try:
            del self.master.db
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
        self.numlabel = tk.Label(self.master, text="Number:").grid(row=1, column=1, padx=5, pady=5)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=1, column=2, padx=5, pady=5)
        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1).grid(row=2, column=1, padx=5, pady=5)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2).grid(row=2, column=2, padx=5, pady=5)
        self.findbutton = tk.Button(self.master, text='Find', command=self.call_get_elephant).grid(row=3, column=1, padx=5, pady=5)
        self.treebutton = tk.Button(self.master, text='Show tree', command=self.call_show_matriline).grid(row=3, column=2, padx=5, pady=5)
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=4, column = 1, columnspan=2, padx=5, pady=5)

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
        matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

################################################################################
## Display matriline                                                          ##
################################################################################

class show_matriline(tk.Frame):

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
        img = Image.open('./tree.png','r')
        img_w, img_h = img.size
        if img_h > img_w:

            newsize= round(600*(600/img_h)),600
            img = img.resize(newsize, Image.ANTIALIAS)
            img.save('./tree.png')
        img_w, img_h = img.size
        background = Image.new('RGBA', (600, 600), (255, 255, 255, 255))
        bg_w, bg_h = background.size
        offset = (round((bg_w - img_w) / 2), round((bg_h - img_h) / 2))
        background.paste(img, offset)
        background.save('./tree.png')
        self.treebox = tk.Text(self.master, height=50, width=100)
        self.tree=tk.PhotoImage(file='./tree.png')
        self.treebox.image_create(tk.END, image=self.tree)
        self.treebox.grid(row=2, column = 1, columnspan=4)

        self.backbutton = tk.Button(self.master, text='Back', command=self.back_to_find)
        self.backbutton.grid(row=1, column=1, sticky=tk.NSEW, padx=5, pady=5)


    def call_show_matriline(self):
        matriline_tree(id=self.eleph[0], db=self.master.db)
        show_matriline(self.master)

    def back_to_find(self):
        findeleph(self.master, back = 1)


################################################################################
## Batch read an elephant file                                                ##
################################################################################

class read_elephant_file(tk.Frame):

    def __init__(self, master):
        self.name = None
        self.master = master
        tk.Frame.__init__(self, self.master)
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
        self.result.grid(row=1, column = 1, columnspan=2, padx=5, pady=5)
        self.reloadbutton = tk.Button(self.master, text='Reload', command=self.reload_file).grid(row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.analysebutton = tk.Button(self.master, text='Analyse', command=self.call_analyse).grid(row=2, column=2, sticky=tk.NSEW, padx=5, pady=5)

    def call_read_elephants(self):
        if self.name is None:
            self.name = askopenfilename(initialdir="~", filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an elephant definition file")
        shortname=self.name.rpartition('/')[2]
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
            +"\t"+shortname.partition('.')[0]+"_accepted.reads\n"
            +"\t"+shortname.partition('.')[0]+"_accepted.log\n"
            +"\t"+shortname.partition('.')[0]+"_rejected.reads\n"
            +"\t"+shortname.partition('.')[0]+"_rejected.log")
        self.result.insert(tk.END, self.result_text)
        # self.result.config(state=tk.DISABLED)

    def reload_file(self):
        if self.name is None:
            text = "You haven't loaded any file yet."
            text.insert(tk.END, self.result_text)
        else:
            self.call_read_elephants()

    def call_analyse(self):
        analyse_elephant_file(self.master)

################################################################################
## Batch analyse an elephant file                                                ##
################################################################################

class analyse_elephant_file(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.name = None
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
        self.result = tk.Text(self.master, height=25, width=55)
        self.result.grid(row=1, column = 1, columnspan=2, padx=5, pady=5)
        self.writebutton = tk.Button(self.master, text='Write an SQL file', command=self.write_sql)
        self.stopbutton = tk.Button(self.master, text='Stop', command=self.stop_loop)
        self.writebutton.grid(row=2, column=2, sticky=tk.NSEW, padx=5, pady=5)
        self.stopbutton.grid(row=2, column=1, sticky=tk.NSEW, padx=5, pady=5)
        self.writebutton.config(state="disabled")

    def stop_loop(self):
        self.break_loop = 1

    def call_analyse_elephants(self):
        self.elephants = self.master.file_content[1]
        del self.master.file_content
        n_elephs = self.elephants[1:].__len__()
        for i,row in enumerate(self.elephants[1:]):
            if self.break_loop != 0:
                break
            num = row[0]
            name = row[1]
            calf_num = row[2]
            sex = row[3]
            birth = row[4]
            cw = row[5]
            caught = row[6]
            camp = row[7]
            alive = row[8]
            research = row[9]
            ele = elephant(num,name,calf_num,sex,birth,cw,caught,camp,alive,research, solved='N')
            ele.source(self.master.db)
            ele.check()
            w = ele.write(self.master.db)
            if re.search(r"^INSERT", str(w)):
                say = 'valid'
            elif re.search(r"^UPDATE", str(w)):
                say = 'valid'
            elif re.search(r"^[Conflict]", str(w)):
                say = 'conflicting'
            else:
                say = 'known'
            self.master.common_out.append(w)
            self.result.insert(tk.END, ("Analysing elephant number "+num+"\t\t("+str(i)+" of "+str(n_elephs)+"): "+say+"\n"))
            self.result.update()
            self.result.see(tk.END)

        if self.break_loop == 0:
            self.result.insert(tk.END, ("\nFinished..!\n"))
            self.writebutton.config(state="normal")
            self.stopbutton.config(state="disabled")
        else:
            self.result.insert(tk.END, ("\nStopped.\n"))
            self.stopbutton.config(state="disabled")
        self.result.update()
        self.result.see(tk.END)

    def write_sql(self):
        parse_output(self.master.common_out,self.master.db)

################################################################################
## Call the main application                                                  ##
################################################################################

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root).grid(sticky="nsew")
   root.grid_rowconfigure(0, weight=1)
   root.grid_columnconfigure(0, weight=1)
   root.grid_rowconfigure(6, weight=1)
   root.grid_columnconfigure(3, weight=1)
   root.mainloop()
