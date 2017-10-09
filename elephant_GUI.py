from tkinter import *
from elephant_classes import *
import pymysql as pms

def source_eleph():
    ele = elephant(num=e1.get(), birth=e2.get(), mysql_usr=e3.get(), mysql_pwd=e4.get())
    ele.source()
    return(ele)

def check_eleph():
    ele.check()
    return(ele)

master = Tk()
master.title("Myanmar Elephant Tools")

Label(master, text="Elephant number:").grid(row=0)
Label(master, text="Birth data").grid(row=1)
Label(master, text="Unsername").grid(row=2)
Label(master, text="Password").grid(row=3)

e1 = Entry(master)
e2 = Entry(master)
e3 = Entry(master)
e4 = Entry(master)

e1.insert(10,"7071")

e1.grid(row=0, column=1)
e2.grid(row=1, column=1)
e3.grid(row=2, column=1)
e4.grid(row=3, column=1)

Button(master, text='Quit', command=master.quit).grid(row=5, column=0, sticky=W, pady=4)
#Button(master, text='OK', command=get_eleph).grid(row=5, column=1, sticky=W, pady=4)
Button(master, text='Source', command=source_eleph).grid(row=6, column=0, sticky=W, pady=4)
Button(master, text='Check', command=check_eleph).grid(row=6, column=1, sticky=W, pady=4)

mainloop()
