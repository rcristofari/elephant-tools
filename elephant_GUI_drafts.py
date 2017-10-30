import tkinter as tk
from tkinter import messagebox
from ElephantTools import *



class dbconnect(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title("Myanmar Elephant Tools")
        tk.Label(self, text="User:").grid(row=0)
        tk.Label(self, text="Password:").grid(row=1)
        tk.Label(self, text="Host:").grid(row=2)
        tk.Label(self, text="Database:").grid(row=3)
        self.e1 = Entry(self)
        self.e2 = Entry(self, show='*')
        self.e3 = Entry(self)
        self.e4 = Entry(self)
        self.e3.insert(10,"localhost")
        self.e4.insert(10,"mep")
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)
        self.e3.grid(row=2, column=1)
        self.e4.grid(row=3, column=1)
        tk.Button(self, text='Connect', command=self.connect_to_db).grid(row=5, column=0, sticky=W, pady=4)
        tk.Button(self, text='Disconnect', command=self.disconnect_from_db).grid(row=5, column=1, sticky=W, pady=4)
        tk.Button(self, text='Quit', command=self.quit).grid(row=5, column=2, sticky=W, pady=4)

    def connect_to_db(self):
        try:
            self.db = mysqlconnect(self.e1.get(), self.e2.get(), self.e3.get(), self.e4.get())
            self.stamp = self.db.stamp() #SEND THAT TO BE WRITTEN TO OUTPUT DIRECTLY
            messagebox.showinfo("", "You are connected!")
#            print("You are connected!")
        except: #still an error here.
            print("Impossible to connect to database.")

    def disconnect_from_db(self):
        try:
            del self.db
        except:
            print("You are not connected to any database.")


class gotoconnect(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)

        self.title("Myanmar Elephant Tools")
        tk.Button(self, text='Connect', command=self.goconnect).grid(row=1, column=0, sticky=W, pady=4)
        tk.Button(self, text='Quit', command=self.quit).grid(row=1, column=1, sticky=W, pady=4)


    def goconnect(self):
        dbconnect()


b = gotoconnect()

b.mainloop()
