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

    def configure_gui(self):
        self.master.title("Myanmar Elephant Tools")
        self.master.geometry("600x600")
        self.master.resizable(False, False)


    def create_widgets(self):
        menubar = tk.Menu(self)
        # create a pulldown menu, and add it to the menu bar
        filemenu = tk.Menu(menubar, tearoff=0)
        # filemenu.add_command(label="Open", command=hello)
        # filemenu.add_separator()
        filemenu.add_command(label="Import Elephants", command=self.read_elephants_prompt)
        filemenu.add_command(label="Quit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        #
        dbmenu = tk.Menu(menubar, tearoff = 0)
        dbmenu.add_command(label="Connexion", command=self.goconnect)
        dbmenu.add_command(label="Find an elephant", command=self.gofindeleph)
        menubar.add_cascade(label="Database", menu=dbmenu)
        # # create more pulldown menus
        # editmenu = tk.Menu(menubar, tearoff=0)
        # editmenu.add_command(label="Blah", command=hello)
        # menubar.add_cascade(label="Edit", menu=editmenu)
        #
        # helpmenu = tk.Menu(menubar, tearoff=0)
        # helpmenu.add_command(label="About", command=hello)
        # menubar.add_cascade(label="Help", menu=helpmenu)
        self.master.config(menu=menubar)

    def goconnect(self):
        dbconnect(self.master)
    def read_elephants_prompt(self):
        name = askopenfilename(initialdir="~", filetypes =(("CSV File", "*.csv"),("All Files","*.*")), title = "Choose an elephant definition file")
        read_elephants(name, ',')
    def gofindeleph(self):
        findeleph(self.master)

################################################################################
## SQL connexion window                                                       ##
################################################################################

class dbconnect(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        global db
        global stamp
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
        self.userlabel = tk.Label(self.master, text="User:").grid(row=0)
        self.pwdlabel = tk.Label(self.master, text="Password:").grid(row=1)
        self.hostlabel = tk.Label(self.master, text="Host:").grid(row=2)
        self.dblabel = tk.Label(self.master, text="Database:").grid(row=3)
        self.e1 = tk.Entry(self.master)
        self.e2 = tk.Entry(self.master, show='*')
        self.e3 = tk.Entry(self.master)
        self.e4 = tk.Entry(self.master)
        self.e3.insert(10,"localhost")
        self.e4.insert(10,"mep")
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        self.connectbutton = tk.Button(self.master, text='Connect', command=self.connect_to_db).grid(row=5, column=0)
        self.disconnectbutton = tk.Button(self.master, text='Disconnect', command=self.disconnect_from_db).grid(row=5, column=1)

    def connect_to_db(self):
        try:
            self.db = mysqlconnect(self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get())
            self.stamp = self.db.stamp() #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            print("You are connected!")
        except: #still an error here.
            print("Impossible to connect to database.")
        global db
        db = self.db

    def disconnect_from_db(self):
        try:
            del db
        except:
            print("You are not connected to any database.")

################################################################################
## Search for an elephant                                                     ##
################################################################################

class findeleph(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.age = tk.IntVar()
        self.age.set(1)
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
        self.numlabel = tk.Label(self.master, text="Number:").grid(row=0)
        self.e1 = tk.Entry(self.master)
        self.e1.grid(row=0, column=1)
        self.radio1 = tk.Radiobutton(self.master, text="Adult", variable=self.age, value=1).grid(row=1, column=0)
        self.radio2 = tk.Radiobutton(self.master, text="Calf", variable=self.age, value=2).grid(row=1, column=1)
        self.findbutton = tk.Button(self.master, text='Find', command=self.call_get_elephant).grid(row=2, column=0)
        self.treebutton = tk.Button(self.master, text='Show tree', command=self.call_show_matriline).grid(row=2, column=1)
        self.result = tk.Text(self.master, height=15, width=45)
        self.result.grid(row=3, column = 0, columnspan=2)

    def call_get_elephant(self):
        self.result.config(state=tk.NORMAL)
        if self.age.get() == 1:
            self.eleph = db.get_elephant(num = self.e1.get())
        elif self.age.get() == 2:
            self.eleph = db.get_elephant(calf_num = self.e1.get())
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
        self.result.config(state=tk.DISABLED)

    def call_show_matriline(self):
        matriline_tree(id=self.eleph[0], db=db)
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
        background = Image.new('RGBA', (600, 600), (255, 255, 255, 255))
        bg_w, bg_h = background.size
        offset = (round((bg_w - img_w) / 2), round((bg_h - img_h) / 2))
        background.paste(img, offset)
        background.save('./tree.png')
        self.treebox = tk.Text(self.master, height=50, width=100)
        self.tree=tk.PhotoImage(file='./tree.png')
        self.treebox.image_create(tk.END, image=self.tree)
        self.treebox.grid(row=0, column = 0, columnspan=4)

################################################################################
## Call the main application                                                  ##
################################################################################

if __name__ == '__main__':
   root = tk.Tk()
   main_app =  MainApplication(root)
   root.mainloop()
