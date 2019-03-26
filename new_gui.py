import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import os
import time

root = Tk()
root.title('GUI TITLE')

def main():

    # plot labels
    plot_title = "TITLE"
    x_lbl = "X LABEL"
    y_lbl = "Y LABEL"

    # dictionaries of GUI contents
    # default initial values
    mag_dict = {'Hz Field (Oe)': 100,
                'Hz Step (Oe)': 20,
                'Hx Field (Oe)': 0,
                'Hx Step (Oe)': 0,
                'Output Time (s)': 1
                }

    keith_dict = {'Current (mA)': 1.9,
                'Current Step (mA)': 0,
                'Averages (s)': 1,
                'Delay (s)': 1
                }

    # values set by various functions, define measurement settings
    control_dict = {'Field Step': 'Step', # set with make_extras()
                    'I_app Step': 'Step', # set with make_extras()
                    'H Scan Direction': 'Hx', # set with make_extras()
                    'H Output Direction': 'Hz', # set with make_buttons()
                    'Hz DAC Channel': 2, # displayed in make_extras()
                    'Hx DAC Channel': 3, # displayed in make_extras()
                    'Hz/DAC (Oe/V)': 123, # displayed in make_extras()
                    'Hx/DAC (Oe/V)': 123, # displayed in make_extras()
                    'Display': '', # set with make_info()
                    'Directory': ''# set with set_directory(), updated with change_directory()
                    }


    # frames for various widgets
    content = Frame(root)
    plt_frame = Frame(content, borderwidth=10, relief="sunken")
    settings_frame = Frame(content, borderwidth=5)
    information_frame = Frame(content, borderwidth=5)
    buttons_frame = Frame(content, borderwidth=5)
    rows =20

    # grid of above frames
    content.grid(column=0, row=0, sticky='nsew')
    plt_frame.grid(column=0, row=0, columnspan=3, rowspan=rows, sticky='nsew')
    settings_frame.grid(column=3, row=0, columnspan=2, rowspan=rows, sticky='nsew')
    information_frame.grid(column=0, row=rows, columnspan=3, sticky='nsew')
    buttons_frame.grid(column=3, row=rows, columnspan=2, sticky='nsew')

    control_dict['Display'] = make_info(information_frame)
    mag_dict = make_form(settings_frame, mag_dict, 'Magnetic Settings')
    keith_dict = make_form(settings_frame, keith_dict, 'Current Settings')
    make_extras(settings_frame, mag_dict, keith_dict, control_dict)
    make_plot(plt_frame, plot_title, x_lbl, y_lbl)
    make_buttons(buttons_frame, mag_dict, keith_dict, control_dict, plot_title, x_lbl, y_lbl)

    #weights columns for all multiple weight=1 columns
    weight(buttons_frame)
    weight(information_frame)
    weight(settings_frame)

    # weights for all rows and columns with weight!=1
    content.columnconfigure(0, weight=3)
    content.columnconfigure(1, weight=3)
    content.columnconfigure(2, weight=3)
    content.columnconfigure(3, weight=1)
    content.columnconfigure(4, weight=1)
    content.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    plt_frame.columnconfigure(0, weight=1)
    plt_frame.rowconfigure(0, weight=1)   
    information_frame.columnconfigure(3, weight=0) # necessary to keep the scroll bar tiny
    information_frame.rowconfigure(0, weight=1)    
    buttons_frame.rowconfigure(0, weight=1)
    #--------end of GUI settings-----------#

    # sets current directory to default (~/Documents/Measurements)
    control_dict['Directory'] = set_directory(control_dict['Display'])

    root.protocol('WM_DELETE_WINDOW', quit) 
    root.mainloop()
#----------------------------------------END OF MAIN-------------------------------------------#


# takes a given frame and gives all columns a weight of 1
def weight(frame):

    for x in range(frame.grid_size()[0]):
        frame.columnconfigure(x, weight=1)


# takes a dictionary and makes labels and entry widgets for key/value pairs
# returns updated dictionary with entry values
def make_form(root, dictionary, frametxt):

    lf = LabelFrame(root, text=frametxt)
    lf.grid(ipadx=2, ipady=2, sticky='nsew')
    for counter, x in enumerate(dictionary.items()):
        lab = Label(lf, width=15, text=x[0], anchor='w')
        ent = Entry(lf, width=15); ent.insert(0, str(x[1]))
        lab.grid(row=counter, column=0, sticky='nsew')
        ent.grid(row=counter, column=1, sticky='nsew')
        dictionary[x[0]] = ent # set dictionary value to entry widget

    return dictionary


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


# extra radio buttons and selectors
def make_extras(root, mag_dict, keith_dict, control_dict):

    lf = LabelFrame(root, text='Measurement Options')
    lf.grid(ipadx=2, ipady=2, sticky='nsew')

    # radiobutton to determine scanning field vs. set field
    control_dict['H Scan Direction'] = StringVar(); control_dict['H Scan Direction'].set('Hx')
    Hz = Radiobutton(lf, text="Scan Hz", variable=control_dict['H Scan Direction'], value='Hz', width=12, anchor='w', \
        command = lambda: Hscan_select(control_dict['H Scan Direction'].get(), control_dict['Display']))
    Hx = Radiobutton(lf, text="Scan Hx", variable=control_dict['H Scan Direction'], value='Hx', width=12, anchor='w', \
        command = lambda: Hscan_select(control_dict['H Scan Direction'].get(), control_dict['Display']))

    # radiobutton to determine loop via step or user defined values
    control_dict['Field Step'] = StringVar(); control_dict['Field Step'].set('Step')
    control_dict['I_app Step'] = StringVar(); control_dict['I_app Step'].set('Step')
    fstep = Radiobutton(lf, text="Field Step Loop", variable=control_dict['Field Step'], value='Step', width=12, anchor='w', \
        command = lambda: field_input(control_dict['Field Step'].get(), mag_dict, control_dict['Display']))
    fuser = Radiobutton(lf, text="Field User Input", variable=control_dict['Field Step'], value='User', width=12, anchor='w', \
        command = lambda: field_input(control_dict['Field Step'].get(), mag_dict, control_dict['Display']))
    cstep = Radiobutton(lf, text="Iapp Step Loop", variable=control_dict['I_app Step'], value='Step', width=12, anchor='w', \
        command = lambda: I_app_input(control_dict['I_app Step'].get(), keith_dict, control_dict['Display']))
    cuser = Radiobutton(lf, text="Iapp User Input", variable=control_dict['I_app Step'], value='User', width=12, anchor='w', \
        command = lambda: I_app_input(control_dict['I_app Step'].get(), keith_dict, control_dict['Display']))       

    Hz_lbl = Label(lf, width=15, text=('Hz DAC: %s' % control_dict['Hz DAC Channel']), anchor='w')
    Hx_lbl = Label(lf, width=15, text=('Hx DAC: %s' % control_dict['Hx DAC Channel']), anchor='w')
    Hz_conv_lbl = Label(lf, width=15, text=('Hz DAC: %s' % control_dict['Hz/DAC (Oe/V)']), anchor='w')
    Hx_conv_lbl = Label(lf, width=15, text=('Hx DAC: %s' % control_dict['Hx/DAC (Oe/V)']), anchor='w')
    
    # grid created buttons 
    Hz.grid(row=0, column=0, sticky='nsew')
    Hx.grid(row=0, column=1, sticky='nsew')
    fstep.grid(row=1, column=0, sticky='nsew')
    fuser.grid(row=1, column=1, sticky='nsew')
    cstep.grid(row=2, column=0, sticky='nsew')
    cuser.grid(row=2, column=1, sticky='nsew')
    # labels for DAC channels and conversion values, now only editable back end.
    Hz_lbl.grid(row=3, column=0, sticky='nsew')    
    Hz_conv_lbl.grid(row=3, column=1, sticky='nsew')
    Hx_lbl.grid(row=4, column=0, sticky='nsew')
    Hx_conv_lbl.grid(row=4, column=1, sticky='nsew')


# creates and grids buttons
def make_buttons(root, mag_dict, keith_dict, control_dict, plot_title, x_lbl, y_lbl):

    control_dict['H Output Direction'] = StringVar(); control_dict['H Output Direction'].set('Hz')

    # button list
    measure_button = Button(root, text='Measure', \
        command=lambda:measure_method(mag_dict, keith_dict, control_dict, plot_title, x_lbl, y_lbl))
    dir_button = Button(root, text='Change Directory', \
        command=lambda:change_directory(control_dict['Directory'], control_dict['Display']))
    quit_button = Button(root, text='Quit', \
        command=lambda:quit_method(control_dict['Display']))
    clear_button = Button(root, text='Clear', \
        command=lambda:clear_method(plot_title, x_lbl, y_lbl, control_dict['Display']))
    output_button = Button(root, text='Output', \
        command=lambda:output_method(control_dict['H Output Direction'].get(), mag_dict, control_dict['Display']))
    z_select = Radiobutton(root, text='Hz', variable=control_dict['H Output Direction'], value='Hz', \
        command= lambda: output_direction(control_dict['H Output Direction'].get(), control_dict['Display']))
    x_select = Radiobutton(root, text='Hx', variable=control_dict['H Output Direction'], value='Hx', \
        command= lambda: output_direction(control_dict['H Output Direction'].get(), control_dict['Display']))

    # grid buttons
    output_button.grid(row=0, column=0, columnspan=1, sticky='nsew')
    x_select.grid(row=0, column=1, sticky='e')
    z_select.grid(row=0, column=1, sticky='w')
    measure_button.grid(row=1, column =0, columnspan=2, sticky='nsew')
    clear_button.grid(row = 3, column = 0, columnspan=1, sticky='nsew')
    dir_button.grid(row=2, column=0, columnspan=2, sticky='nsew')
    quit_button.grid(row=3, column=1, columnspan=1, sticky='nsew')


# does the matplotlib gui stuff to clear plot area
def plot_set(title, x_label, y_label):

    ax.clear()
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.axis([-1, 1, -1, 1]) 


# command to change H scan direction
def Hscan_select(var, display):

    display.insert('end', 'Scan in the %s direction.' % var)
    display.see(END)


# command to change applied field loop/user input
def field_input(var, mag_dict, display):

    if var == 'User':
        mag_dict['Hx Field (Oe)'].delete(0, len(mag_dict['Hx Field (Oe)'].get())) # clear entry
        mag_dict['Hx Field (Oe)'].insert(0, '-1, 0, -1'); mag_dict['Hx Field (Oe)'].update() # list entry
        mag_dict['Hz Field (Oe)'].delete(0, len(mag_dict['Hz Field (Oe)'].get())) # clear entry
        mag_dict['Hz Field (Oe)'].insert(0, '-1, 0, -1'); mag_dict['Hz Field (Oe)'].update() # list entry
        mag_dict['Hx Step (Oe)'].config(state=DISABLED); mag_dict['Hx Step (Oe)'].update() # disable step function
        mag_dict['Hz Step (Oe)'].config(state=DISABLED); mag_dict['Hz Step (Oe)'].update() # disable step function
    else:
        mag_dict['Hx Field (Oe)'].delete(0, len(mag_dict['Hx Field (Oe)'].get())) # clear entry
        mag_dict['Hx Field (Oe)'].insert(0, '0'); mag_dict['Hx Field (Oe)'].update() # step entry
        mag_dict['Hz Field (Oe)'].delete(0, len(mag_dict['Hz Field (Oe)'].get())) # clear entry
        mag_dict['Hz Field (Oe)'].insert(0, '0'); mag_dict['Hz Field (Oe)'].update() # step entry
        mag_dict['Hx Step (Oe)'].config(state=NORMAL); mag_dict['Hx Step (Oe)'].update() # enable step function
        mag_dict['Hz Step (Oe)'].config(state=NORMAL); mag_dict['Hz Step (Oe)'].update() # enable step function    

    display.insert('end', '%s loop type selected for applied fields.' % var)
    display.see(END)


# command to change applied field loop/user input
def I_app_input(var, keith_dict, display):

    if var == 'User':
        keith_dict['Current (mA)'].delete(0, len(keith_dict['Current (mA)'].get())) # clear entry
        keith_dict['Current (mA)'].insert(0, '-1, 0, -1'); keith_dict['Current (mA)'].update() # list entry
        keith_dict['Current Step (mA)'].config(state=DISABLED); keith_dict['Current Step (mA)'].update() # disable step function
    else:
        keith_dict['Current (mA)'].delete(0, len(keith_dict['Current (mA)'].get())) # clear entry
        keith_dict['Current (mA)'].insert(0, '0'); keith_dict['Current (mA)'].update() # step entry
        keith_dict['Current Step (mA)'].config(state=NORMAL); keith_dict['Current Step (mA)'].update() # enable step function  

    display.insert('end', '%s loop type selected for applied currents.' % var)
    display.see(END)


# sets default save directory, returns directory path
def set_directory(display):

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
def change_directory(var, display):

    var = filedialog.askdirectory()
    display.insert('end', var)
    display.see(END)
    

# displays the current output direction selected
def output_direction(var, display):

    display.insert('end', 'Output direction set to the %s direction.' % var)
    display.see(END)


# applies a field H in the given direction at a given strength
def output_method(var, mag_dict, display):
    time = mag_dict['Output Time (s)'].get()

    display.insert('end', '%s output for %s second(s)' % (var, time))
    display.see(END)


# clears and redraws the matplotlib gui
def clear_method(title, x_label, y_label, display):

    plot_set(title, x_label, y_label)
    dataplot.draw()
    display.delete(0, END)
    print("clear all")


# turns off all outputs and then quits the program
def quit_method(display):

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


def animation(i, x_data, y_data):

    x_data = x_data[:-(len(x_data)-len(y_data))]

    ax.clear()
    ax.plot(x_data, y_data)


# measurement loop!
def measure_method(mag_dict, keith_dict, control_dict, plot_title, x_label, y_label):
    pass

    ani = animation.FuncAnimation(fig, animate, fargs=(x_data, y_data), interval=1000)
    plt.show()






if __name__ == '__main__':
    main()