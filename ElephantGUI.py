#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from PIL import Image
import os
import re
from datetime import datetime
from eletools import *
from eletools_gui import *


################################################################################
## Call the main application                                                  ##
################################################################################

if __name__ == '__main__':
   root = tk.Tk(className='eletools')
   main_app =  MainApplication(root).grid(sticky="nsew")
   root.grid_rowconfigure(0, weight=1)
   root.grid_columnconfigure(0, weight=1)
   root.grid_rowconfigure(9, weight=1)
   root.grid_columnconfigure(9, weight=1)
   root.mainloop()
