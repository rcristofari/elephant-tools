#! /usr/bin/python3
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
import tkinter.ttk as ttk
from eletools.Utilities import *
import numpy as np
import csv
from datetime import datetime
from PIL import Image
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import pylab
import seaborn
import pandas

##################################################################################################
## plot_measure class, first version (static plot embedded in tkInter)                          ##
##################################################################################################
# Deprecated. Rename to plot_measures if re-activated

class plot_measures_deprecated(tk.Frame):

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


        # Set main and axis labels
        graph.set_title(str(chosen_measure) + ' ~ time for ' + str(self.details[2]) + ' (' + str(self.details[1])
                        + ', ' + str(self.details[4]) + ')')
        graph.set_ylabel(str(chosen_measure) + ' (' + str(unit[0]) + ')')

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        canvas.draw()
        canvas.get_tk_widget().grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)
        canvas._tkcanvas.grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)

    def save_plot(self):
        pass ## TO DO

##################################################################################################
## plot_relatedness class, pop-up window showing the relatedness matrix                         ##
##################################################################################################

class plot_relatedness(tk.Frame):

    def __init__(self, master, rdataframe):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.rdataframe = rdataframe
        self.configure_gui()
        self.clear_frame()
        self.create_widgets()
        self.call_draw()

    def configure_gui(self):
        self.master.title("Relatedness cluster map")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self):
        # Save button:
        self.savebutton = tk.Button(self.master, text='Save', command=self.call_save, width=20, bg=self.master.lightcolour, fg=self.master.darkcolour, highlightthickness=0, activebackground=self.master.darkcolour, activeforeground=self.master.lightcolour)
        self.savebutton.grid(row=1, column=4, columnspan=1, sticky = tk.EW, padx=5, pady=5)

        # Create the plot canvas
        self.canvas = tk.Canvas(self.master, width=600, height=600)
        self.canvas.grid(row=2, column=1, columnspan=4, sticky = tk.EW, padx=5, pady=5)

    def call_draw(self):
        clusmap = seaborn.clustermap(self.rdataframe, cmap='inferno_r', yticklabels=False)
        clusmap.ax_row_dendrogram.set_visible(False)
        clusmap.cax.set_visible(False)
        clusmap.savefig('plot.png')
        # img = Image.open('./plot.png','r')
        self.mapbox = tk.Text(self.master, height=60, width=100)
        self.map = tk.PhotoImage(file='./plot.png')
        self.mapbox.image_create(tk.END, image=self.map)
        self.mapbox.grid(row=2, column=1, columnspan=4)

    def call_save(self):
        mapfile = asksaveasfilename(title='Save map image...', defaultextension='.png')
        clusmap.savefig(mapfile)

##################################################################################################
## plot_measure class, second version (using the PyPlot window directly for interactivity)      ##
##################################################################################################

class plot_measures(tk.Frame):

    def __init__(self, master, id):
        self.master = master
        self.__id = id
        # We also get details on the elephant (num, name, sex, and birth date):
        self.elephant = self.master.db.get_elephant(id=self.__id)
        self.plot_control = None
        self.multiple_select = []
        self.multiple_data = []
        tk.Frame.__init__(self, self.master)
        self.configure_gui()
        self.create_widgets()
        self.load_standards()

    def configure_gui(self):
        pass
        # self.master.title("Data plot")
        # self.master.resizable(False, False)

    def clear_frame(self):
        for widget in self.master.winfo_children():
                widget.grid_forget()

    def create_widgets(self, *args):
        self.plot_control = tk.Toplevel(self.master, bg=self.master.lightcolour)
        self.plot_control.title('Available measures for ' + str(self.elephant[2]) + ' (' + str(self.elephant[1]) + ')')
        self.plot_control.grid_columnconfigure(0, weight=1)
        self.plot_control.grid_columnconfigure(3, weight=1)
        self.plot_control.grid_rowconfigure(0, weight=1)
        self.plot_control.grid_rowconfigure(8, weight=1)
        # self.plot_control.geometry("400x300")
        self.plot_control.resizable(True, True)
        self.plot_control.lightcolour = self.master.lightcolour
        self.plot_control.darkcolour = self.master.darkcolour
        self.plot_control.db = self.master.db
        self.plot_control.id = self.__id
        self.plot_control.protocol("WM_DELETE_WINDOW", self.close_plot)

        self.tv = ttk.Treeview(self.plot_control, height=20, columns=('Unit','Description'), show="tree")
        self.tv.heading("#0", text='Class')
        self.tv.heading("#1", text='Type')
        self.tv.column("#0", width = 120, stretch=0)
        self.tv.column("#1", width = 20, stretch=0)
        self.tv.heading('Unit', text='Unit')
        self.tv.column('Unit', anchor='w', width=50)
        self.tv.heading('Description', text='Description')
        self.tv.column('Description', anchor='w', width=200)
        self.tv.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)

        # Add a scrollbar
        vsb = ttk.Scrollbar(self.plot_control, orient="vertical", command=self.tv.yview)
        vsb.grid(row=1, column=2, sticky=tk.NS)
        self.tv.configure(yscrollcommand=vsb.set)

        # Get the available measures:
        self.__classes_types = self.master.db.get_measure_list(id=self.__id)

        # Populate the available classes and the types within
        classes_all = []
        for c in self.__classes_types:
            classes_all.append(c[0])
        self.__classes = list(set(classes_all))
        self.__classes.sort(key=lambda k: (k[0]))

        self.__types = []
        for t in self.__classes_types:
            if t in self.__types:
                pass
            else:
                self.__types.append(t)

        self.__types_only = []
        for t in self.__types:
            self.__types_only.append(t[1])
        if all(x in self.__types_only for x in ['twbc', 'lympho', 'eosino', 'hetero', 'mono', 'baso']):
            self.__types.append(['immunology', 'Differential', 'count', 'Full differential WBC count'])

        for c in self.__classes:
            globals()[c] = self.tv.insert("", "end", text=c, open = True, tags = ('class',))
        for t in self.__types:
            name = t[0]
            self.tv.insert(globals()[name], "end", text=t[1], values=t[2:4], tags = ('type',))

        self.tv.bind("<Double-1>", self.OnDoubleClick1)
        self.tv.bind("<Shift-Double-1>", self.OnDoubleClick2)

    def OnDoubleClick1(self, event):
        item = self.tv.selection()[0]
        self.selection = self.tv.item(item, "text")
        if self.selection in ('sist', 'diast'):
            self.multiple_select = ['sist', 'diast']
            # We get the values for the selected measures:
            self.sist = self.master.db.get_measure_values(id=self.__id, measurelist='("sist")')
            self.diast = self.master.db.get_measure_values(id=self.__id, measurelist='("diast")')
            self.multiple_data = [self.sist, self.diast]
            self.call_draw(multiplot=True)

        # Special case of the Differential WBC count plot
        elif self.selection == 'Differential':
            self.multiple_select = ['twbc', 'lympho', 'eosino', 'hetero', 'mono', 'baso']
            self.multiple_data = []
            for s in self.multiple_select:
                self.multiple_data.append(self.master.db.get_measure_values(id=self.__id, measurelist='("' + s + '")'))
            self.call_draw()

        else:
            self.multiple_select = [self.selection]
            # We get the values for the selected measures:
            self.measures = self.master.db.get_measure_values(id=self.__id, measurelist='("'+str(self.selection)+'")')
            self.multiple_data = [self.measures]
            # Call the plot window:
            self.call_draw()

    def OnDoubleClick2(self, event):
        item = self.tv.selection()[0]
        self.selection = self.tv.item(item, "text")
        self.multiple_select.append(self.selection)
        self.measures = self.master.db.get_measure_values(id=self.__id, measurelist='("'+str(self.selection)+'")')
        self.multiple_data.append(self.measures)
        # Call the plot window:
        self.call_draw(multiplot=True)

    def close_plot(self):
        if self.plot_control:
            plt.close()
            self.plot_control.destroy()

    def load_standards(self):
        self.__stds = []
        with open('__resources/Standards') as stdfile:
            std = csv.reader(stdfile, delimiter = ',')
            for s in std:
                self.__stds.append(list(s))
        self.__std_avail = []
        for s in self.__stds:
            self.__std_avail.append(s[0])

    def call_draw(self, multiplot=False):
        # Close any previously open plot:
        plt.close()

        # If we are plotting a single series of values:
        if multiplot is False and self.selection != 'Differential':
            # Isolate the values:
            dates = []
            values = []
            for m in self.measures:
                dates.append(m[2])
                values.append(m[3])

            # Plot the values
            plt.plot_date(np.array(dates), values, marker = 'o', linestyle = ':', color = 'r')

            # Fix the scale specifically for some measures
            if self.multiple_data[0][0][4] == 'percent':
                plt.gca().set_ylabel('percent')
                plt.gca().set_ylim(0,100)
            elif self.multiple_data[0][0][4] == 'mmHg':
                plt.gca().set_ylabel('mmHg')
                plt.gca().set_ylim(0,200)

            # Add the standard area if available
            if self.selection in self.__std_avail:
                index = np.where(np.array(self.__std_avail) == self.selection)[0][0]
                lower = float(self.__stds[index][2])
                upper = float(self.__stds[index][3])
                # plt.axhline(y=lower, linestyle = '--', color = 'k', linewidth=.75)
                # plt.axhline(y=upper, linestyle = '--', color = 'k', linewidth=.75)
                plt.gca().axhspan(lower, upper, alpha=0.2, color='k')

            # Calculate the birthdays and corresponding add vertical lines to the plot
            max_date_in_data = max(dates)
            min_date_in_data = min(dates)
            birthdays, ages = [], []
            birthday = self.elephant[5]
            while birthday < max_date_in_data:
                birthday = add_years(birthday, 1)
                if birthday > min_date_in_data:
                    birthdays.append(matplotlib.dates.date2num(birthday))
                    ages.append(round((birthday - self.elephant[5]).days / 365.25))
            if birthdays.__len__() > 1:
                    birthdays.pop() # remove the last values to avoid empty space on the plot
                    ages.pop()

            # get the Y coordinate for annotations:
            y_coord = plt.gca().get_ylim()[1] - (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]) / 40
            for i, xc in enumerate(birthdays):
                plt.axvline(x=xc, linestyle = '--', color = 'k', linewidth=.75)
                plt.annotate(str(ages[i]) + 'y.o.', xy = (xc, y_coord), verticalalignment='top', backgroundcolor='w', ha='center', rotation=90, fontsize=8)

            plt.grid(ls='dotted')
            w = pylab.gcf()
            if self.elephant[1] is not None:
                w.canvas.set_window_title(self.selection + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[1]) + ')')
            else:
                w.canvas.set_window_title(self.selection + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[3]) + ')')

            w.set_facecolor("#E08E45")
            # Set axis labels
            plt.gca().set_ylabel(str(self.selection))

        # Special case: the Differential WBC count plot
        elif multiplot is False and self.selection == 'Differential':

            # Restructure the data to change the percentages into counts:
            dates = []
            twbc = []
            lympho, l_lympho = [], []
            eosino, l_eosino = [], []
            hetero, l_hetero = [], []
            mono, l_mono = [], []
            baso, l_baso = [], []

            # We need to check that the dates of TWBC match those of the differential.
            _twbc = self.multiple_data[0][:]
            _lympho = self.multiple_data[1][:]
            _twbc_dates, _lympho_dates = [], []
            for t in _twbc:
                _twbc_dates.append(t[2])
            for l in _lympho:
                _lympho_dates.append(l[2])

            for i, d in enumerate(_twbc_dates):
                if d not in _lympho_dates:
                    self.multiple_data[0].pop(i)


            for i, t in enumerate(self.multiple_data[0]):
                dates.append(t[2])
                twbc.append(t[3])
                hetero.append(t[3] * (self.multiple_data[3][i][3]/100))
                mono.append(t[3] * (self.multiple_data[4][i][3]/100))
                baso.append(t[3] * (self.multiple_data[5][i][3]/100))
                lympho.append(t[3] * (self.multiple_data[1][i][3]/100))
                eosino.append(t[3] * (self.multiple_data[2][i][3]/100))

                l_hetero.append(t[3]*(self.multiple_data[3][i][3]/100))
                l_mono.append(t[3]*(self.multiple_data[4][i][3]/100 + self.multiple_data[3][i][3]/100))
                l_baso.append(t[3]*(self.multiple_data[5][i][3]/100 + self.multiple_data[4][i][3]/100 + self.multiple_data[3][i][3]/100))
                l_lympho.append(t[3]*(self.multiple_data[1][i][3]/100 + self.multiple_data[5][i][3]/100 + self.multiple_data[4][i][3]/100 + self.multiple_data[3][i][3]/100))
                l_eosino.append(t[3]*(self.multiple_data[2][i][3]/100 + self.multiple_data[1][i][3]/100 + self.multiple_data[5][i][3]/100 + self.multiple_data[4][i][3]/100 + self.multiple_data[3][i][3]/100))


            y = np.vstack([hetero, mono, baso, lympho, eosino])
            labels = ["Heterophiles ", "Monocytes", "Basophiles", "Lymphocytes", "Eosinophiles"]

            plt.stackplot(dates, y, alpha=0.5, labels=labels)
            plt.legend()
            plt.plot_date(dates, twbc, marker='', linestyle='-', color='k', linewidth=1.5, label='Total')
            plt.plot_date(dates, l_lympho, marker='', linestyle='--', color='k', linewidth=0.75, label='lymphocytes')
            plt.plot_date(dates, l_eosino, marker='', linestyle='--', color='k', linewidth=0.75, label='eosinophiles')
            plt.plot_date(dates, l_hetero, marker='', linestyle='--', color='k', linewidth=0.75, label='heterophiles')
            plt.plot_date(dates, l_mono, marker='', linestyle='--', color='k', linewidth=0.75, label='monocytes')
            plt.plot_date(dates, l_baso, marker='', linestyle='--', color='k', linewidth=0.75, label='basophiles')

            max_date_in_data = max(dates)
            min_date_in_data = min(dates)
            birthdays, ages = [], []
            birthday = self.elephant[5]
            while birthday < max_date_in_data:
                birthday = add_years(birthday, 1)
                if birthday > min_date_in_data:
                    birthdays.append(matplotlib.dates.date2num(birthday))
                    ages.append(round((birthday - self.elephant[5]).days / 365.25))
            if birthdays.__len__() > 1:
                    birthdays.pop() # remove the last values to avoid empty space on the plot
                    ages.pop()

            # get the Y coordinate for annotations:
            y_coord = plt.gca().get_ylim()[1] - (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]) / 40
            #x_offset = (graph.get_xlim()[1] - graph.get_xlim()[0]) / 40
            for i, xc in enumerate(birthdays):
                plt.axvline(x=xc, linestyle = '--', color = 'k', linewidth=.75)
                plt.annotate(str(ages[i]) + 'y.o.', xy = (xc, y_coord), verticalalignment='top', backgroundcolor='w', ha='center', rotation=90, fontsize=8)

            plt.grid(ls='dotted')
            plt.gca().set_ylabel("million/L")
            plt.gca().autoscale(axis='x', tight=True)
            w = pylab.gcf()
            if self.elephant[1] is not None:
                w.canvas.set_window_title(self.selection + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[1]) + ')')
            else:
                w.canvas.set_window_title(self.selection + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[3]) + ')')

            w.set_facecolor("#E08E45")



        # If we are plotting several series:
        else:
            host = host_subplot(111, axes_class=AA.Axes)
            plt.subplots_adjust(right=0.8)

            host.set_xlabel("")
            host.set_ylabel(self.multiple_select[0])
            host_dates = []
            host_values = []
            for d in self.multiple_data[0]:
                host_dates.append(d[2])
                host_values.append(d[3])
            host.plot_date(np.array(host_dates), host_values, marker = 'o', linestyle = ':', label=self.multiple_select[0])

            print(self.multiple_data[0])

            # If the Host unit is percents of mmHg, we set the limit to the full range.
            which_layer_is_percent = None
            which_layer_is_mmHg = None

            if self.multiple_data[0][0][4] == 'percent':
                host.set_ylabel('percent')
                host.set_ylim(0,100)
                which_layer_is_percent = host
            elif self.multiple_data[0][0][4] == 'mmHg':
                host.set_ylabel('mmHg')
                host.set_ylim(0,200)
                which_layer_is_mmHg = None

            par = []
            offset = 50
            k = 0

            for i, m in enumerate(self.multiple_select[1:]):
                if self.multiple_data[(i+1)][0][4]=='percent' and which_layer_is_percent is not None:
                    dates = []
                    values = []
                    for d in self.multiple_data[(i+1)]:
                        dates.append(d[2])
                        values.append(d[3])
                    which_layer_is_percent.plot_date(np.array(dates), values, marker = 'o', linestyle = ':', label=m)

                elif self.multiple_data[(i+1)][0][4]=='mmHg' and which_layer_is_mmHg is not None:
                    dates = []
                    values = []
                    for d in self.multiple_data[(i+1)]:
                        dates.append(d[2])
                        values.append(d[3])
                    which_layer_is_mmHg.plot_date(np.array(dates), values, marker = 'o', linestyle = ':', label=m)

                else:
                    par.append(host.twinx())
                    par[k].axis["right"] = par[k].get_grid_helper().new_fixed_axis(loc="right", axes=par[k], offset=(offset, 0))
                    par[k].axis["right"].toggle(all=True)
                    par[k].set_ylabel(str(m))
                    dates = []
                    values = []
                    for d in self.multiple_data[(i+1)]:
                        dates.append(d[2])
                        values.append(d[3])
                    par[k].plot_date(np.array(dates), values, marker = 'o', linestyle = ':', label=m)

                    if self.multiple_data[(i+1)][0][4]=='percent':
                        which_layer_is_percent = par[k]
                        which_layer_is_percent.set_ylabel('percent')
                        which_layer_is_percent.set_ylim(0,100)
                    elif self.multiple_data[(i+1)][0][4]=='mmHg':
                        which_layer_is_mmHg = par[k]
                        which_layer_is_mmHg.set_ylabel('mmHg')
                        which_layer_is_mmHg.set_ylim(0,200)

                    k += 1
                    offset += 50


            # Calculate the birthdays and corresponding add vertical lines to the plot
            l = plt.gca().get_xlim()
            min_date_in_data = matplotlib.dates.num2date(l[0]).date()
            max_date_in_data = matplotlib.dates.num2date(l[1]).date()

            birthdays, ages = [], []
            birthday = self.elephant[5]
            while birthday < max_date_in_data:
                birthday = add_years(birthday, 1)
                if birthday > min_date_in_data:
                    birthdays.append(matplotlib.dates.date2num(birthday))
                    ages.append(round((birthday - self.elephant[5]).days / 365.25))
            if birthdays.__len__() > 1:
                    birthdays.pop() # remove the last values to avoid empty space on the plot
                    ages.pop()

            # # get the Y coordinate for annotations:
            y_coord = plt.gca().get_ylim()[1] - (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]) / 40
            for i, xc in enumerate(birthdays):
                plt.axvline(x=xc, linestyle = '--', color = 'k', linewidth=.75)
                plt.annotate(str(ages[i]) + 'y.o.', xy = (xc, y_coord), verticalalignment='top', backgroundcolor='w', ha='center', rotation=90, fontsize=8)

            host.legend()

            w = pylab.gcf()

            if self.multiple_select == ['sist', 'diast']:
                label = 'Blood pressure'
            elif all(x in ('lympho','hetero','eosino','baso','mono') for x in self.multiple_select):
                label = 'Differential WBC count'
            elif all(x in ('sed','fec') for x in self.multiple_select):
                label = 'Parasite load'
            elif all(x in ('belly','body_length','body_mass','body_mass_wm','chest', 'neck', 'foot', 'height', 'hind_limb') for x in self.multiple_select):
                label = 'Morphometry'
            else:
                label = 'Multiple data'

            if self.elephant[1] is not None:
                w.canvas.set_window_title(label + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[1]) + ')')
            else:
                w.canvas.set_window_title(label + ' for ' + str(self.elephant[2]) + ' (' + str(self.elephant[3]) + ')')
            w.set_facecolor("#E08E45")

            # The way to go to color the axis labels the same as the lines (not nneeded I think)
            # p1, = host.plot([0, 1, 2], [0, 1, 2], label="XX")
            # p2, = par1.plot([0, 1, 2], [0, 3, 2], label="YY")
            # ...
            # par1.set_ylim(0, 4)
            # host.axis["left"].label.set_color(p1.get_color())
            # par1.axis["right"].label.set_color(p2.get_color())
            # ...

        # Display plot
        plt.show()
