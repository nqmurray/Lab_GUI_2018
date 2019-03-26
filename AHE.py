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
from datetime import datetime


root = Tk()
root.title('AHE Measurement')

def main():

    global display, H_dir_loop, field_loop, current_loop, DACz, DACx, directory

    # plot labels
    plot_title = "Realtime Resistance vs H Plot"
    x_axis_label = "Applied Field (Oe)"
    y_axis_label = "Hall Resistance (Ohm)"

    # fields of user set entries, first entry is the label text for the labelframe
    # field inputs should be a list with a label string and a default value for the entry widget
    mag_fields = 'Magnetic Settings', ['Hz Field (Oe)', 100], ['Hz Step (Oe)', 20], ['Hx Field (Oe)', 0], ['Hx Step (Oe)', 0], ['Hz (Oe)/DAC (V)', 123], ['Hx (Oe)/DAC (V)', 123], ['Output Time (s)', 1],   
    keith_fields = 'Keithley Settings', ['Current (mA)',   1.9], ['Current Step (mA)', 0], ['Delay (s)', 1]
    rows = len(mag_fields) + len(keith_fields) + 5 # extra rows from makeextras()

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

    # build the widgets 
    make_plot(plt_frame, plot_title, x_axis_label, y_axis_label)
    magnet = make_form(settings_frame, mag_fields)
    keith = make_form(settings_frame, keith_fields)  
    display = make_info(information_frame) # Listbox for displaying information
    H_dir_loop, field_loop, current_loop, DACz, DACx = make_extras(settings_frame, magnet, keith) # loop direction, field input type, current input type, DAC channels
    make_buttons(buttons_frame, magnet, keith, plot_title, x_axis_label, y_axis_label)

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
    directory = set_directory()






    root.protocol('WM_DELETE_WINDOW', quit) 
    root.mainloop()
#----------------------------------------END OF MAIN-------------------------------------------#


# takes a given frame and gives all columns a weight of 1
def weight(frame):

    for x in range(frame.grid_size()[0]):
        frame.columnconfigure(x, weight=1)


# function that creates labelframe and then label and entry widgets for a given list
# returns the list of labels and associated entries
def make_form(root, fields):

    lf = LabelFrame(root, text=fields[0])
    lf.grid(ipadx=2, ipady=2, sticky='nsew')
    entries = []
    for x in range(1, len(fields)):
        lab = Label(lf, width=15, text=fields[x][0], anchor='w')
        ent = Entry(lf, width=15); ent.insert(0, str(fields[x][1]))
        lab.grid(row=x-1, column=0, sticky='nsew')
        ent.grid(row=x-1, column=1, sticky='nsew')
        entries.append((fields[x][0], ent))

    return entries


# initializes and grids matplotlib plot 
def make_plot(root, title, x_label, y_label):

    global ax, dataplot

    # matplotlib figure and axes 
    fig = plt.Figure(figsize=(6,5), dpi=100)
    ax = fig.add_subplot(111)
    plot_set(title, x_label, y_label)
    ax.axis([-1, 1, -1, 1])
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
def make_extras(root, magnet_list, keith_list):

    lf = LabelFrame(root, text='Measurement Loop Options')
    lf.grid(ipadx=2, ipady=2, sticky='nsew')

    # radiobutton to determine scanning field vs. set field
    loop_select = StringVar()
    Hz = Radiobutton(lf, text="Scan Hz", variable=loop_select, value='Hz', width=12, anchor='w',\
        command = lambda: xz_loop(loop_select.get()))
    Hx = Radiobutton(lf, text="Scan Hx", variable=loop_select, value='Hx', width=12, anchor='w',\
        command = lambda: xz_loop(loop_select.get()))

    # radiobutton to determine loop via step or user defined values
    field_loop_var = StringVar()
    current_loop_var = StringVar()
    fstep = Radiobutton(lf, text="Field Step Loop", variable=field_loop_var, value='Step', width=12, anchor='w',\
        command = lambda: field_input(field_loop_var.get(), magnet_list))
    fuser = Radiobutton(lf, text="Field User Input", variable=field_loop_var, value='User', width=12, anchor='w',\
        command = lambda: field_input(field_loop_var.get(), magnet_list))
    cstep = Radiobutton(lf, text="Iapp Step Loop", variable=current_loop_var, value='Step', width=12, anchor='w',\
        command = lambda: Iapp_input(current_loop_var.get(), keith_list))
    cuser = Radiobutton(lf, text="Iapp User Input", variable=current_loop_var, value='User', width=12, anchor='w',\
        command = lambda: Iapp_input(current_loop_var.get(), keith_list))             

    # spinboxes that show the current lock-in channel controlling the electromagnetics
    dacz = IntVar()
    dacx = IntVar()
    options = ['1', '2', '3', '4']
    Hz_channel = OptionMenu(lf, dacz, *options, command=dac_method(magnet_list, 'z')); Hz_lbl = Label(lf, width=15, text='Hz DAC', anchor='w')
    Hx_channel = OptionMenu(lf, dacx, *options, command=dac_method(magnet_list, 'x')); Hx_lbl = Label(lf, width=15, text='Hx DAC', anchor='w')

    # grid created buttons
    Hz.grid(row=0, column=0, sticky='nsew')
    Hx.grid(row=0, column=1, sticky='nsew')
    fstep.grid(row=1, column=0, sticky='nsew')
    fuser.grid(row=1, column=1, sticky='nsew')
    cstep.grid(row=2, column=0, sticky='nsew')
    cuser.grid(row=2, column=1, sticky='nsew')
    Hz_lbl.grid(row=3, column=0, sticky='nsew')
    Hz_channel.grid(row=3, column=1, sticky='nsew')
    Hx_lbl.grid(row=4, column=0, sticky='nsew')
    Hx_channel.grid(row=4, column=1, sticky='nsew')

    # select default values
    loop_select.set('Hz')
    field_loop_var.set('Step')
    current_loop_var.set('Step')
    dacz.set(2)
    dacx.set(3)

    return loop_select.get(), field_loop_var.get(), current_loop_var.get(), dacz.get(), dacx.get()


#creates and grids the buttons
def make_buttons(root, magnet, keith, plot_title, x_label, y_label):

    # radio button command
    xz = StringVar()

    # button list
    measure_button = Button(root, text='Measure', command= lambda: measure_method(magnet, keith, plot_title, x_label, y_label))
    dir_button = Button(root, text='Change Directory', command=change_directory)
    quit_button = Button(root, text='Quit', command=quit_method)
    clear_button = Button(root, text='Clear', command= lambda: clear_method(plot_title, x_label, y_label))
    output_button = Button(root, text='Output', command= lambda: output_method(xz.get(), magnet))
    z_select = Radiobutton(root, text='Hz', variable=xz, value='Z', \
        command= lambda: output_direction(xz.get()))
    x_select = Radiobutton(root, text='Hx', variable=xz, value='X', \
        command= lambda: output_direction(xz.get()))
    
    # grid buttons
    output_button.grid(row=0, column=0, columnspan=1, sticky='nsew')
    x_select.grid(row=0, column=1, sticky='e')
    z_select.grid(row=0, column=1, sticky='w')
    measure_button.grid(row=1, column =0, columnspan=2, sticky='nsew')
    clear_button.grid(row = 3, column = 0, columnspan=1, sticky='nsew')
    dir_button.grid(row=2, column=0, columnspan=2, sticky='nsew')
    quit_button.grid(row=3, column=1, columnspan=1, sticky='nsew')
    
    # set intial value of radiobutton
    xz.set('Z')


# does the matplotlib gui stuff to clear plot area
def plot_set(title, x_label, y_label):

    ax.clear()
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
     

# fetches the entry value for a given label, returns error if no matching value found    
def fetch_entry(var, entry_list):

    for x in entry_list:
        if var == x[0]:
            return x[1].get()
        else:
            pass
    return 'ERROR! No entry called %s found.' % var


# displays the current applied field that will be used to scan
def xz_loop(loop_field):

    global H_dir_loop

    H_dir_loop = loop_field
    display.insert('end', 'Scan in the %s direction.' % H_dir_loop)
    display.see(END)


# displays the current input type selected for applied fields
def field_input(input_type, magnet):

    global field_loop

    # updates entry formatting to match loop type (list vs int)
    if input_type == 'User':
        for x in magnet:
            if 'Field' in x[0]:
                x[1].delete(0, len(x[1].get())) # clear entry
                x[1].insert(0, '-1, 0, 1')
                x[1].update()
            elif 'Step' in x[0]:
                x[1].config(state=DISABLED)
                x[1].update()
            else:
                pass
    else:
        for x in magnet:
            if 'Field' in x[0]:
                x[1].delete(0, len(x[1].get())) # clear entry
                x[1].insert(0, '0')
                x[1].update()
            elif 'Step' in x[0]:
                x[1].config(state=NORMAL)
                x[1].update()
            else:
                pass

    #set so that if user input selected, step is made inactive
    field_loop = input_type
    display.insert('end', '%s loop type selected for applied fields.' % field_loop)
    display.see(END)


# displays the current input type selected for applied current
def Iapp_input(input_type, keith):

    global current_loop

    # updates entry formatting to match loop type (list vs int)
    if input_type == 'User':
        for x in keith:
            if 'Current (mA)' in x[0]:
                x[1].delete(0, len(x[1].get())) # clear entry
                x[1].insert(0, '-1, 0, 1')
                x[1].update()
            elif 'Step' in x[0]:
                x[1].config(state=DISABLED)
                x[1].update()
            else:
                pass
    else:
        for x in keith:
            if 'Current (mA)' in x[0]:
                x[1].delete(0, len(x[1].get())) # clear entry
                x[1].insert(0, '0')
                x[1].update()
            elif 'Step' in x[0]:
                x[1].config(state=NORMAL)
                x[1].update()
            else:
                pass

    #set so that if user input selected, step is made inactive
    current_loop = input_type
    display.insert('end', '%s loop type selected for applied currents.' % current_loop)
    display.see(END)


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


# displays the current output direction selected
def output_direction(output_dir):

    display.insert('end', 'Output direction set to the %s direction.' % output_dir)
    display.see(END)


# applies a field H in the given direction at a given strength
def output_method(Hdirection, magnet):
    time = fetch_entry('Output Time (s)', magnet)
    """
    i=float(_interval)
    signal=float(_signal)
    freq=int(_frequency)
    
    amp = lock inAmp(func, sense, signal, freq)
    """
    display.insert('end', 'Output in the %s director for %s second(s)' % (Hdirection, time))
    display.see(END)


# updates the DAC channel and prompts user to update the conversion value
def dac_method(magnet, string):

    for x in magnet:
        if ('H%s (Oe)/DAC (V)' % string) in x[0]:
                new_conversion = x[1]
        else:
            pass

    # necessary function that is what python expects for option menu
    def update(val):

        global DACz, DACx

        # takes entry value and prints to display, closes window
        def ok_button():

            new = ent.get()
            # updates conversion factor to user input
            new_conversion.delete(0, len(new_conversion.get())) # clear entry
            new_conversion.insert(0, '%s' % new)
            new_conversion.update()
            display.insert('end', 'New H%s conversion factor set to %s' % (string, new))
            display.see(END)
            top.destroy()

        top = Toplevel(width=60)
        top.title('Update H%s Conversion Factor' %string)

        lbl = Label(top, text="New Conversion Factor (Oe/V): ", anchor='w')
        ent = Entry(top, width=30)
        ok = Button(top, text='Ok', command=ok_button)

        lbl.grid(row=0, column=0, sticky='nsew')
        ent.grid(row=0, column=1, sticky='nsew')
        ok.grid(row=1, columnspan=2, sticky='ns')

        if string == 'z':
            DACz = val
            out = DACz
        else:
            DACx = val
            out = DACx

        display.insert('end', 'H%s DAC channel set to %s' % (string, out))
        display.see(END)

    return update


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


# takes maximum value and step size and creates a list of all values (floats) to run from low to high
def make_list(max_val, step_val):
    # checks to make sure inputs are valid (numbers)
    if max_val.lstrip('-').replace('.','',1).isdigit() and step_val.lstrip('-').replace('.','',1).isdigit():
        maximum = float(max_val)
        step = float(step_val)
        new_list = []
        # if step is zero, field is only measured at that value
        if step == 0.0:
            return [maximum]
        # if maximum is a positive value, build list from neg to positive
        elif maximum > 0.0:
            maximum = -maximum
            while maximum <= float(max_val):
                new_list.append(maximum)
                maximum += step
            return new_list
        # if maximum is a negative value, build the list
        else:
            while maximum <= -float(max_val):
                new_list.append(maximum)
                maximum += step
            return new_list
    else:
        messagebox.showwarning('Invalid Entry', 'Field or step input is not a digit')
        

# converts string to list, returns list (of floats), raises error if list is not all numeric
def convert_to_list(input_list):
    
    str_list = input_list.replace(",", ' ') # input list can have , and/or spaces to seperate values
    str_list = str_list.split()
    new_list = []
    for x in str_list:
        verify = x.lstrip('-')
        if verify.replace('.','',1).isdigit() == False:
            messagebox.showerror('Error', 'Formatting error with value %s.' % str(x))
        else:
            new_list.append(float(x))
    return(new_list)


# takes file parameters and results and saves the file, should have 5 lines before data is saved
def save_method(fix_val, current_val, x_values, y_values):

    stamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    file = open(str(directory)+"/"+"AHE_"+H_dir_loop+"_scan_"+str(fix_val)+"Oe_"+str(current_val)+"mA_"+str(stamp), "w")
    file.write(H_dir_loop+" field: "+str(fix_val)+"(Oe)\n")
    file.write("Applied current: "+str(current_val)+"(mA)\n")
    file.write("\n\n")
    file.write("Number"+" "+H_dir_loop+" Field(Oe)"+" "+"Resistance(Ohm)"+"\n")

    for counter, value in enumerate(y_values):
        file.write(str(counter)+" "+str(x_values[counter])+" "+str(value)+"\n")
        
    file.closed

    display.insert('end', stamp)
    display.insert('end', "The Measurement data is saved.")
    display.see(END)



# measurement function
def measure_method(magnet, keith, plot_title, x_axis_label, y_axis_label):

    # set the scan and fixed applied field directions
    if H_dir_loop == 'Hz':
        scan = 'Hz'
        fix = 'Hx'
    else:
        scan = 'Hx'
        fix = 'Hz'

    # create the lists of field values, scan loop is modified to include full loop
    if field_loop == 'Step':
        scan_field_output = make_list(fetch_entry('%s Field (Oe)' % scan, magnet), fetch_entry('%s Step (Oe)' % scan, magnet))
        inverse = reversed(scan_field_output[0:-1])
        for x in inverse:
            scan_field_output.append(x)

        print(scan_field_output)
        fix_field_output = make_list(fetch_entry('%s Field (Oe)' % fix, magnet), fetch_entry('%s Step (Oe)' % fix, magnet))
    else:
        scan_field_output = convert_to_list(fetch_entry('%s Field (Oe)' % scan, magnet))
        inverse = reversed(scan_field_output[0:-1])
        for x in inverse:
            scan_field_output.append(x)

        fix_field_output = convert_to_list(fetch_entry('%s Field (Oe)' % fix, magnet))

    # create the list of current values
    if current_loop == 'Step':
        current_output = make_list(fetch_entry('Current (mA)', keith), fetch_entry('Current Step (mA)', keith))
    else: 
        current_output = convert_to_list(fetch_entry('Current (mA)', keith))

    for fix_val in fix_field_output:

        for current_val in current_output:

            # intializes the measurement data list
            measured_values = []

            # reset the plot to be clear for graphing
            plot_set(plot_title, x_axis_label, y_axis_label)

            display.insert('end', 'Measurement at %s (mA)' % str(current_val))
            display.insert('end', 'Measurement at %s (Oe)' % str(fix_val))
            display.see(END)

            # loop over all scan values
            x = 0
            for scan_val in scan_field_output:
                tmp = scan_val * 2 + x
                x += 1
                measured_values.append(tmp)
                ax.plot(scan_field_output[0:len(measured_values)], measured_values,'b-o', ms=10, mew=0.5, alpha=0.5)
                dataplot.draw()
                display.insert('end', 'Applied %s Field Value: %s (Oe)      Measured Resistance: %s (Ohm)' %(scan, scan_val, tmp))
                display.see(END)
                time.sleep(0.1)

            # save data
            save_method(fix_val, current_val, scan_field_output, measured_values)






if __name__ == '__main__':
    main()

