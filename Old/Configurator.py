from tkinter import *
from tkinter import ttk
import serial
import serial.tools.list_ports
import datetime
import threading
import multiprocessing
import os
import time
import re


#for printing debugging messages in console
dbg = 0

gRoot = Tk()
#gRoot.geometry("480x280")
gRoot.title("DigiTune Guardian Configurator")
sty = ttk.Style()
sty.theme_use("alt")
gRoot.columnconfigure(0,weight=1)
gRoot.rowconfigure(0,weight=1)
#sty.configure("gframe.TFrame",background="white")
gFrame = ttk.LabelFrame(gRoot,text="Connection Setting",padding=10)
gFrame.grid(column=1,row=1, sticky=(W,E))

#Frame for COM messages

gFrame21 = ttk.Frame(gRoot,padding=10)
gFrame21.grid(column=2,row=1, sticky=(W))
#gRoot.resizable(0,0)


for x in range(10):
    gFrame.columnconfigure(x,weight = x)
    gFrame.rowconfigure(x,weight = x)
    
# label1=ttk.Label(gFrame, text = "Serial Console")
# label1.grid(column=2,row=0)
gFrame.rowconfigure(0,weight=2)

# sty.configure("label2.TLabel",borderwidth=4,relief="ridge",foreground="red",ipadx=10)
# label2=ttk.Label(gFrame,sty="label2.TLabel", text = "Select Com Port:")
# label2.grid(column=1,row=1, sticky = (N,E,W,S))

"""
Com Port List
"""
#Start
ports = serial.tools.list_ports.comports()
com_port_list = [com[0] for com in ports]
com_port_list.insert(0,"Select COM Port")
if dbg == 1:
    print(com_port_list)
#END
com_value_inside = StringVar()
# baud_value_inside = StringVar()
# baud_menu = ttk.OptionMenu(gFrame,baud_value_inside,"select baud rate","9600",
#                            '19200','28800','38400','57600','76800',
#                            '115200','128000','153600','230400','256000','460800','921600')
# baud_menu.grid(column=3, row=1, sticky = (E))
def com_port_update():
    global ports
    global com_port_list
    ports = serial.tools.list_ports.comports()
    com_port_list = [com[0] for com in ports]
    com_port_list.insert(0,"Select COM Port")
    if dbg == 1:
        print(com_port_list)
    com_menu = ttk.OptionMenu(gFrame,com_value_inside,*com_port_list)
    com_menu.grid(column=2, row=1, sticky = (E))
    #Frame for the COM LIST
    # gRoot_com_list = Toplevel(gRoot)
    # x = gRoot.winfo_x()
    # y = gRoot.winfo_y()
    # gRoot_com_list.geometry("+%d+%d" %(x+200,y+200))
    
    
    # gFrame01 = ttk.Frame(gRoot_com_list,padding=10)
    # gFrame01.grid(column=0,row=1, sticky=(W))
    # #Create a horizontal scrollbar
    # scrollbar = ttk.Scrollbar(gFrame01, orient= 'horizontal')
    # scrollbar.grid(column=1,row=2, sticky=W+E)

    # Lb1 = Listbox(gFrame01, xscrollcommand = 1, width = 50, font= ('Helvetica 8 bold'))
    # counter = 0;
    # for x in ports:
    #     Lb1.insert(counter, str(x))
    # #print (counter)
    # counter += 1
    # Lb1.grid(column=1,row=1, sticky=W+E)
    # Lb1.config(xscrollcommand= scrollbar.set)

    # #Configure the scrollbar
    # scrollbar.config(command= Lb1.xview)
    
    
def com_port_list():
    global ports
    global com_port_list
    ports = serial.tools.list_ports.comports()
    com_port_list = [com[0] for com in ports]
    com_port_list.insert(0,"Select an Option")
    if dbg == 1:
        print(com_port_list)
    com_menu = ttk.OptionMenu(gFrame,com_value_inside,*com_port_list)
    com_menu.grid(column=2, row=1, sticky = (E))
    #Frame for the COM LIST
    gRoot_com_list = Toplevel(gRoot)
    x = gRoot.winfo_x()
    y = gRoot.winfo_y()
    gRoot_com_list.geometry("+%d+%d" %(x+200,y+200))
    
    
    gFrame01 = ttk.Frame(gRoot_com_list,padding=10)
    gFrame01.grid(column=0,row=1, sticky=(W))
    #Create a horizontal scrollbar
    scrollbar = ttk.Scrollbar(gFrame01, orient= 'horizontal')
    scrollbar.grid(column=1,row=2, sticky=W+E)

    Lb1 = Listbox(gFrame01, xscrollcommand = 1, width = 50, font= ('Helvetica 8 bold'))
    counter = 0;
    for x in ports:
        Lb1.insert(counter, str(x))
    #print (counter)
    counter += 1
    Lb1.grid(column=1,row=1, sticky=W+E)
    Lb1.config(xscrollcommand= scrollbar.set)

    #Configure the scrollbar
    scrollbar.config(command= Lb1.xview)

def serial_print():
    global serFlag
    global ser
    global counter1
    global lastx
    global lasty
    x =""
    #print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
    #print("ID of process running task 1: {}".format(os.getpid()))
    if(serFlag):
        if(ser.in_waiting>0):
            #
            try:
                x = ser.read(ser.in_waiting)
                lastx=x
                #x = ser.readline(ser.in_waiting)
                #x = ser.read_until(expected='\n', size=ser.in_waiting)
                #print(x)
                y = str(counter1)+": "+str(datetime.datetime.now())+" -> "+str(x.decode())
                lasty=y
                Lb2.insert(counter1, str(y))
                Lb2.see("end")
                #print (counter1)
                counter1 += 1
                #gFrame.after(100,serial_print)
            except:
                pass
        ser.flush()
        gFrame.after(100,serial_print)


ser = serial.Serial()
serFlag = 0
def serial_connect(com_port,baud_rate):
    global ser
    ser.baudrate = baud_rate
    ser.port = com_port
    ser.timeout = 1
    ser._xonxoff=1
    ser.bytesize=serial.EIGHTBITS
    ser.parity=serial.PARITY_NONE
    ser.stopbits=serial.STOPBITS_ONE
    ser.open()
    global serFlag
    serFlag = 1
    
    t1 = threading.Thread(target = serial_print, args = (), daemon=1)
    t1.start()
    #t1.join()
    """
    P1 = multiprocessing.Process(target = serial_print, args=())
    P1.start()
    P1.join()
    """
    #serial_print()
counter1 = 0;


    
def serial_close():
    global ser
    global serFlag
    serFlag = 0
    ser.close()
    
def submit_value():
    if dbg == 1:
        print("selected option: {}".format(com_value_inside.get()))
        # print(" Baud Rate {}".format(baud_value_inside.get()))
    serial_connect(com_value_inside.get(),'115200')
    
CAN_baud=StringVar()
CANbaudDrop = ttk.OptionMenu(gFrame,CAN_baud,"500","250","500")
CANbaudDrop.grid(column=6, row=1, sticky = (E))
CANBaudlabel=ttk.Label(gFrame, text = "CAN bitrate (kbps):")
CANBaudlabel.grid(column=5,row=1, sticky = (E))
    
    
def send(mycommand):
   ser.write(mycommand.encode())
   result = ser.readline()
   if len(result)>0:
       resultstrlist = re.findall(r'\b\d+\b',result.decode())
       resultnum = int(resultstrlist[0])
   else:
       resultnum=0;
   return resultnum
   
def show_lights():
    MaxRPM = (send("<2?>"))
    send('<11,'+str(MaxRPM)+'>')
def hide_lights():
    send('<11,0>')
    
def getAllLEDcol():
    LED1col = getLEDcol(1)
    LED1rgb.set(LED1col)
    
    LED2col = getLEDcol(2)
    LED2rgb.set(LED2col)
    
    LED3col = getLEDcol(3)
    LED3rgb.set(LED3col)
    
    LED4col = getLEDcol(4)
    LED4rgb.set(LED4col)
    
    LED5col = getLEDcol(5)
    LED5rgb.set(LED5col)
    
    LED6col = getLEDcol(6)
    LED6rgb.set(LED6col)
    
    LED7col = getLEDcol(7)
    LED7rgb.set(LED7col)
    
    LED8col = getLEDcol(8)
    LED8rgb.set(LED8col)
    
    LED9col = getLEDcol(9)
    LED9rgb.set(LED9col)
    
    LED10col = getLEDcol(10)
    LED10rgb.set(LED10col)

    
    
def getLEDcol(led):
    colnum = int(send("<1"+str(led+10)+"?>"))
    colstr = numbers_to_colour(colnum)

    return colstr
    

def writeAllLEDcol():
    writeLEDcol(1,LED1rgb.get())
    
def writeLEDcol(led,colour):
    colnum=(colour_to_number(colour))
    command = ("<1"+str(led+10)+","+str(colnum)+">")
    send(command)
    


    
def numbers_to_colour(argument):
    switcher = {
        -1: "Black",
        0: "Blank",
        1: "Green",
        2: "Yellow",
        3: "Orange",
        4: "Red",
        5: "Blue",
        6: "Purple",
        7: "White",
    }
    return switcher.get(argument, "nothing")

def colour_to_number(argument):
    colourlist = ["Blank", "Green","Yellow","Orange","Red","Blue","Purple","White"]
    
    return colourlist.index(argument)

def CANwrite():
    baud = int(CAN_baud.get())
    send("<200,"+str(baud)+">")
    
    
def CANread():
    CAN_baud.set(send("<200?>"))


Lb2 = Listbox(gFrame21, width = 70, xscrollcommand = 1)
Lb2.grid(column=1, row = 1, sticky = W+E)
Sb2 = ttk.Scrollbar(gFrame21,orient = 'vertical')
Sb2.config(command=Lb2.yview)
Sb2.grid(column = 2,row =1, sticky=N+S)
Sb2v = ttk.Scrollbar(gFrame21,orient = 'horizontal')
Sb2v.grid(column = 1,row =2, sticky=W+E)
Sb2v.config(command = Lb2.xview)
Lb2.configure(xscrollcommand = Sb2v.set, yscrollcommand = Sb2.set)

def clear_listbox():
    Lb2.delete(0,END)
    
subBtn = ttk.Button(gFrame,text="Connect",command = submit_value)
subBtn.grid(column=3,row=1, sticky = (E))

RefreshBtn = ttk.Button(gFrame,text="Refresh",command = com_port_update)
RefreshBtn.grid(column=2,row=2, sticky = (E))

RefreshBtn = ttk.Button(gFrame,text="List Ports",command = com_port_list)
RefreshBtn.grid(column=1,row=2, sticky = (E))



closeBtn = ttk.Button(gFrame,text="Disconnect",command = serial_close)
closeBtn.grid(column=3,row=2, sticky = (E))

# clearBtn = ttk.Button(gFrame,text="Clear Messages",command = clear_listbox)
# clearBtn.grid(column=3,row=2, sticky = (E))


CANwriteBtn = ttk.Button(gFrame,text="Write CAN Baud",command = CANwrite)
CANwriteBtn.grid(column=6,row=2, sticky = (E))

CANreadBtn = ttk.Button(gFrame,text="Read CAN Baud",command = CANread)
CANreadBtn.grid(column=5,row=2, sticky = (E))



gFrameShift = ttk.LabelFrame(gRoot,text="Shift Light Settings",padding=10)
gFrameShift.grid(column=1,row=2, sticky=(W,E))


clearBtn = ttk.Button(gFrameShift,text="Show Shift Lights",command = show_lights)
clearBtn.grid(column=1,row=4, sticky = (E))

clearBtn = ttk.Button(gFrameShift,text="Hide Shift Lights",command = hide_lights)
clearBtn.grid(column=2,row=4, sticky = (E))

clearBtn = ttk.Button(gFrameShift,text="Read LED colours",command = getAllLEDcol)
clearBtn.grid(column=3,row=4, sticky = (E))

clearBtn = ttk.Button(gFrameShift,text="Write LED colours",command = writeAllLEDcol)
clearBtn.grid(column=4,row=4, sticky = (E))



colourOptions = ("Green","Yellow","Orange","Red","Blue","Purple","White")
LED1rgb = StringVar()
LED1_menu = ttk.OptionMenu(gFrameShift,LED1rgb,"Green",*colourOptions)
LED1_menu.grid(column=1, row=6, sticky = (E))
LED1label=ttk.Label(gFrameShift, text = "LED 1 colour")
LED1label.grid(column=1,row=5, sticky = (E))

LED2rgb = StringVar()
LED2_menu = ttk.OptionMenu(gFrameShift,LED2rgb,"Green",*colourOptions)
LED2_menu.grid(column=2, row=6, sticky = (E))
LED2label=ttk.Label(gFrameShift, text = "LED 2 colour")
LED2label.grid(column=2,row=5, sticky = (E))

LED3rgb = StringVar()
LED3_menu = ttk.OptionMenu(gFrameShift,LED3rgb,"Green",*colourOptions)
LED3_menu.grid(column=3, row=6, sticky = (E))
LED3labe1=ttk.Label(gFrameShift, text = "LED 3 colour")
LED3labe1.grid(column=3,row=5, sticky = (E))

LED4rgb = StringVar()
LED4_menu = ttk.OptionMenu(gFrameShift,LED4rgb,"Green",*colourOptions)
LED4_menu.grid(column=4, row=6, sticky = (E))
LED4label=ttk.Label(gFrameShift, text = "LED 4 colour")
LED4label.grid(column=4,row=5, sticky = (E))

LED5rgb = StringVar()
LED5_menu = ttk.OptionMenu(gFrameShift,LED5rgb,"Green",*colourOptions)
LED5_menu.grid(column=5, row=6, sticky = (E))
LED5label=ttk.Label(gFrameShift, text = "LED 5 colour")
LED5label.grid(column=5,row=5, sticky = (E))

LED6rgb = StringVar()
LED6_menu = ttk.OptionMenu(gFrameShift,LED6rgb,"Green",*colourOptions)
LED6_menu.grid(column=6, row=6, sticky = (E))
LED6label=ttk.Label(gFrameShift, text = "LED 6 colour")
LED6label.grid(column=6,row=5, sticky = (E))

LED7rgb = StringVar()
LED7_menu = ttk.OptionMenu(gFrameShift,LED7rgb,"Red",*colourOptions)
LED7_menu.grid(column=7, row=6, sticky = (E))
LED7label=ttk.Label(gFrameShift, text = "LED 7 colour")
LED7label.grid(column=7,row=5, sticky = (E))

LED8rgb = StringVar()
LED8_menu = ttk.OptionMenu(gFrameShift,LED8rgb,"Red",*colourOptions)
LED8_menu.grid(column=8, row=6, sticky = (E))
LED8label=ttk.Label(gFrameShift, text = "LED 8 colour")
LED8label.grid(column=8,row=5, sticky = (E))

LED9rgb = StringVar()
LED9_menu = ttk.OptionMenu(gFrameShift,LED9rgb,"Blue",*colourOptions)
LED9_menu.grid(column=9, row=6, sticky = (E))
LED9label=ttk.Label(gFrameShift, text = "LED 9 colour")
LED9label.grid(column=9,row=5, sticky = (E))

LED10rgb = StringVar()
LED10_menu = ttk.OptionMenu(gFrameShift,LED10rgb,"Blue",*colourOptions)
LED10_menu.grid(column=10, row=6, sticky = (E))
LED10label=ttk.Label(gFrameShift, text = "LED 10 colour")
LED10label.grid(column=10,row=5, sticky = (E))

Patternlabel=ttk.Label(gFrameShift, text = "Shift Pattern Direction:")
Patternlabel.grid(column=6,row=3, sticky = (E))
PatternStr = StringVar()
Pattern_menu = ttk.OptionMenu(gFrameShift,PatternStr,"Left To Right","Left To Right", "Outside to Inside")
Pattern_menu.grid(column=6, row=4, sticky = (E))

PatternStartlabel=ttk.Label(gFrameShift, text = "Shift Pattern Direction:")
PatternStartlabel.grid(column=6,row=3, sticky = (E))
PatternStartStr = StringVar()
PatternStart_menu = ttk.OptionMenu(gFrameShift,PatternStr,"Left To Right","Left To Right", "Outside to Inside")
PatternStart_menu.grid(column=6, row=4, sticky = (E))

"""
#Add a Listbox Widget
listbox = Listbox(win, width= 350, font= ('Helvetica 15 bold'))
listbox.pack(side= LEFT, fill= BOTH)

#Add values to the Listbox
for values in range(1,101):
   listbox.insert(END, values)
"""
def donothing():
   filewin = Toplevel(gRoot)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def About_me():
   filewin = Toplevel(gRoot)
   Label1 = Label(filewin, text = "EXASUB.COM").pack()
   button = Button(filewin, text="Quit", command = filewin.destroy)
   button.pack()

menubar = Menu(gRoot)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="New", command=donothing)
filemenu.add_command(label="Open", command=donothing)
filemenu.add_command(label="Save", command=donothing)
filemenu.add_command(label="Save as...", command=donothing)
filemenu.add_command(label="Close", command=donothing)

filemenu.add_separator()

filemenu.add_command(label="Exit", command=gRoot.quit)
menubar.add_cascade(label="File", menu=filemenu)
editmenu = Menu(menubar, tearoff=0)
editmenu.add_command(label="Undo", command=donothing)

editmenu.add_separator()

editmenu.add_command(label="Cut", command=donothing)
editmenu.add_command(label="Copy", command=donothing)
editmenu.add_command(label="Paste", command=donothing)
editmenu.add_command(label="Delete", command=donothing)
editmenu.add_command(label="Select All", command=donothing)

menubar.add_cascade(label="Edit", menu=editmenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
# menubar.add_command(label = "EXASUB.com", command = About_me)
menubar.add_separator()
menubar.add_command(label = "Quit", command = gRoot.destroy)

def on_closing():
    serial_close()
    gRoot.destroy()




gRoot.config(menu=menubar)
gRoot.protocol("WM_DELETE_WINDOW", on_closing)
com_port_update()
gRoot.mainloop()