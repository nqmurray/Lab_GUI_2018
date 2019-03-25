import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import os
import time

root = Tk()
root.title('GUI TITLE')
t
def main():

    # plot labels
    plot_title = "TITLE"
    x_lbl = "X LABEL"
    y_lbl = "Y LABEL"

    # dictionaries of GUI contents
    mag_dict = {'Hz Field (Oe)': 100,
                'Hz Step (Oe)': 20,
                'Hx Field (Oe)': 0,
                'Hx Step (Oe)': 0,
                'Hz/DAC (Oe/V)': 123,
                'Hx/DAC (Oe/V)': 123,
                'Output Time (s)': 1}

    keith_dict = {'Current (mA)': 1.9,
                'Current Step (mA)': 0,
                'Averages (s)': 1,
                'Delay (s)': 1}


    # frames for various widgets
    content = Frame(root)
    plt_frame = Frame(content, borderwidth=10, relief="sunken")
    settings_frame = Frame(content, borderwidth=5)
    information_frame = Frame(content, borderwidth=5)
    buttons_frame = Frame(content, borderwidth=5)

    # grid of above frames
    content.grid(column=0, row=0, sticky='nsew')
    plt_frame.grid(column=0, row=0, columnspan=3, rowspan=rows, sticky='nsew')
    settings_frame.grid(column=3, row=0, columnspan=2, rowspan=rows, sticky='nsew')
    information_frame.grid(column=0, row=rows, columnspan=3, sticky='nsew')
    buttons_frame.grid(column=3, row=rows, columnspan=2, sticky='nsew')

    root.protocol('WM_DELETE_WINDOW', quit) 
    root.mainloop()
#----------------------------------------END OF MAIN-------------------------------------------#


# initializes and grids matplotlib plot 
def make_plot(root, title, x_label, y_label):

    global ax, dataplot

    # matplotlib figure and axes 
    fig = plt.Figure(figsize=(6,5), dpi=100)
    ax = fig.add_subplot(111)
    plot_set(title, x_label, y_label)
    # canvas for matplotlib gui
    dataplot = FigureCanvasTkAgg(fig, root)
    dataplot.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, sticky='nsew')


# creates and grids the listbox and scroll bar
def make_info(root):

    listbox = Listbox(root, height=5)
    y_scroll = Scrollbar(root, orient=VERTICAL, command=listbox.yview)
    listbox['yscrollcommand'] = y_scroll.set
    listbox.grid(column=0, row=0, columnspan=3, sticky='nsew')
    y_scroll.grid(column=3, row=0, sticky='ns')

    return listbox

# does the matplotlib gui stuff to clear plot area
def plot_set(title, x_label, y_label):

    ax.clear()
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.axis([-1, 1, -1, 1]) 

# sets default save directory, returns directory path
def set_directory():

    test = os.path.expanduser('~/Documents')

    if os.path.isdir(test + '/Measurements'):
        os.chdir(test + '/Measurements')
    else:
        os.mkdir(test + '/Measurements')
        os.chdir(test + '/Measurements')

    cur_dir = os.getcwd()

    display.insert('end', 'The current directory is set to: %s' % cur_dir)
    display.see(END)

    return cur_dir


# changes the save directory
def change_directory():

    global directory

    directory = filedialog.askdirectory()
    display.insert('end', directory)
    display.see(END)
    

# clears and redraws the matplotlib gui
def clear_method(title, x_label, y_label):

    plot_set(title, x_label, y_label)
    dataplot.draw()
    display.delete(0, END)
    print("clear all")


# turns off all outputs and then quits the program
def quit_method():

    global root

    q = messagebox.askquestion('Quit', 'Are you sure you want to quit?')

    #amp = lockinAmp(func, sense, signal, freq)
    #amp.dacOutput(0, 1)
    #amp.dacOutput(0, 2)
    #amp.dacOutput(0, 3)
    #amp.dacOutput(0, 4)
    if q == 'yes':
        display.insert('end', "All fields set to zero.")
        display.see(END)
        time.sleep(.1)

        root.quit()


if __name__ == '__main__':
    main()
