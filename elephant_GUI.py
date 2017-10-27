from tkinter import *
from elephant_classes import *

def connect_to_db():
    db = mysqlconnect(e1.get(), e2.get(), e3.get(), e4.get())
    db.stamp()
    print("Connected!")


# def source_eleph():
#     ele = elephant(num=e1.get(), birth=e2.get(), mysql_usr=e3.get(), mysql_pwd=e4.get())
#     ele.source()
#     return(ele)
#
# def check_eleph():
#     ele.check()
#     return(ele)

class dbconnect(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Myanmar Elephant Tools")
        Label(self, text="User:").grid(row=0)
        Label(self, text="Password:").grid(row=1)
        Label(self, text="Host:").grid(row=2)
        Label(self, text="Database:").grid(row=3)
        e1 = Entry(self)
        e2 = Entry(self, show='*')
        e3 = Entry(self)
        e4 = Entry(self)
        e3.insert(10,"localhost")
        e4.insert(10,"mep")
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        e4.grid(row=3, column=1)
        Button(self, text='Quit', command=self.quit).grid(row=5, column=1, sticky=W, pady=4)
        Button(self, text='Connect', command=connect_to_db).grid(row=5, column=0, sticky=W, pady=4)

a = dbconnect()

mainloop()
