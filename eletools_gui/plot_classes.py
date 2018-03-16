#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from eletools.Utilities import *
import numpy as np
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import matplotlib.dates as mdates
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook

class plot_measures(tk.Frame):

    def __init__(self, master, measures, details):
        self.master = master
        self.measures = self.parse_measures(measures)
        self.all_measures = measures
        self.details = details
        self.selected_measure = tk.StringVar()
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_draw()

    def configure_gui(self):
        self.master.title("Data plot")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        # Dropdown menu to choose the measure
        self.selected_measure.set(self.measure_list[0])
        self.measure_menu = tk.OptionMenu(self.master, self.selected_measure, *self.measure_list)
        self.measure_menu.config(bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.measure_menu.grid(row=1, column=2, columnspan=1, sticky = tk.W, padx=5, pady=5)
        self.measure_menu_label = tk.Label(self.master, text='Choose measure:', bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.measure_menu_label.grid(row=1, column=1, columnspan=1, sticky = tk.W, padx=5, pady=5)

        # Plot button:
        self.plotbutton = tk.Button(self.master, text='Draw', command=self.call_draw, width=20, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.plotbutton.grid(row=1, column=3, columnspan=1, sticky = tk.EW, padx=5, pady=5)

        # Save button:
        self.plotbutton = tk.Button(self.master, text='Save', command=self.call_draw, width=20, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.plotbutton.grid(row=1, column=4, columnspan=1, sticky = tk.EW, padx=5, pady=5)

        # Create the plot canvas
        self.canvas = tk.Canvas(self.master, width=600, height=300)
        self.canvas.grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)

    def parse_measures(self, measures):
        self.measure_name, self.unit = [], []
        for row in measures:
            self.measure_name.append(row[1])
            self.unit.append(row[4])
        self.measure_list = list(set(self.measure_name))

    def call_draw(self):
        # Select only the measure lines needed for that graph
        chosen_measure = self.selected_measure.get()
        measure_array = np.array(self.all_measures)
        r = np.where(measure_array == chosen_measure)
        measure_index = r[0].tolist()
        these_measures = []
        for i in measure_index:
            these_measures.append(self.all_measures[i])

        # Extract dates and values for that measure
        dates, dates_datetime, values, units = [], [], [], []
        for row in these_measures:
            dates.append(matplotlib.dates.date2num(row[2]))
            dates_datetime.append(row[2])
            values.append(row[3])
            units.append(row[4])
        unit = list(set(units))

        # Prepare the figure formatting:
        years = mdates.YearLocator()   # every year
        months = mdates.MonthLocator()  # every month
        yearsFmt = mdates.DateFormatter('%Y')

        fig = Figure(figsize=(5, 4), dpi=100)
        graph = fig.add_subplot(111) # The numbers describe the tiling. Could be used for plotting several measures...
        graph.plot_date(np.array(dates), values, marker = 'o', linestyle = ':', color = 'r')

        # format the ticks
        graph.xaxis.set_major_locator(years)
        graph.xaxis.set_major_formatter(yearsFmt)
        graph.xaxis.set_minor_locator(months)

        max_date_in_data = max(dates_datetime)
        min_date_in_data = min(dates_datetime)
        birthdays, ages = [], []
        birthday = self.details[5]
        while birthday < max_date_in_data:
            birthday = add_years(birthday, 1)
            if birthday > min_date_in_data:
                birthdays.append(matplotlib.dates.date2num(birthday))
                ages.append(round((birthday - self.details[5]).days / 365.25))
        birthdays.pop() # remove the last values to avoid empty space on the plot
        ages.pop()

        # get the Y coordinate for annotations:
        y_coord = graph.get_ylim()[1] - (graph.get_ylim()[1] - graph.get_ylim()[0]) / 40
        x_offset = (graph.get_xlim()[1] - graph.get_xlim()[0]) / 40
        for i, xc in enumerate(birthdays):
            graph.axvline(x=xc, linestyle = '--', color = 'k')
            graph.annotate(str(ages[i]) + 'y.o.', xy = (xc + x_offset, y_coord), verticalalignment='top', rotation=90)

        graph.grid(ls='dotted')

        # Start the graph at the elephant's birth
        # datemin = self.details[5]
        # graph.set_xlim(left=datemin)

        # Set main and axis labels
        graph.set_title(str(chosen_measure) + ' ~ time for ' + str(self.details[2]) + ' (' + str(self.details[1])
                        + ', ' + str(self.details[4]) + ')')
        graph.set_ylabel(str(chosen_measure) + ' (' + str(unit[0]) + ')')

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)
        canvas._tkcanvas.grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)