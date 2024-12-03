import customtkinter
import serial
import serial.tools.list_ports
import time
import re
from tktooltip import ToolTip
from functools import partial
from customtkinter import filedialog
import subprocess
import tkinter


customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


ESP_ROM_BAUD = 115200


class ToplevelWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = customtkinter.CTkLabel(self, text="Upgrading Firmware. Do not switch off or unplug your device")
        self.label.pack(padx=20, pady=20)
        
class AutoConnectWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x100")

        self.label = customtkinter.CTkLabel(self, text="Scanning for connected devices")
        self.label.pack(padx=20, pady=20)

Version = 0

VariableRow = 0

VariableNameArray =[]
VariableIDArray =[]
ToolTipArray =[]
Channelid = []

BoxFgColour = "white"

colourlist = ["Blank", "Green","Yellow","Orange","Red","Blue","Purple","White"]


CLTnamearray = ["Coolant Temp LED", "CLT Max", "CLT Min", "Hold time"]
CLTIDarray = [100,12,13,133]
CLTtooltip = ["Coolant temperature above which the LED lights red","Coolant temperature below which the LED lights blue","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(CLTnamearray)
VariableIDArray.append(CLTIDarray)
ToolTipArray.append(CLTtooltip)
Channelid.append(14)

OilTnamearray = ["Oil Temp LED", "Oil T Max", "Oil T Min", "Hold time"]
OilTIDarray = [101,15,16,134]
OilTtooltip = ["Oil temperature above which the LED lights red","Oil temperature below which the LED lights blue","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(OilTnamearray)
VariableIDArray.append(OilTIDarray)
ToolTipArray.append(OilTtooltip)
Channelid.append(17)

OilPnamearray = ["Oil Pressure LED", "Oil P Max", "Oil P Min", "Oil P relief RPM", "Oil P cranking", "Hold time"]
OilPIDarray = [102,18,19,20,21,135]
OilPtooltip = ["Oil pressure above which the LED lights red","Oil pressure below which the LED lights blue if RPM exceeds the Oil P relief RPM","The RPM beyond which oil pressure should remain constant (the relief valve opens). Below this RPM, the minimum pressure threshold is interpolated between Oil P min and Oil P cranking","Base oil pressure expected when RPM is very low. The the minimum pressure threshold is interpolated between Oil P min and Oil P cranking from 0RPM to the relief RPM","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(OilPnamearray)
VariableIDArray.append(OilPIDarray)
ToolTipArray.append(OilPtooltip)
Channelid.append(22)

MAPnamearray = ["MAP/Boost LED", "MAP abs. Max", "MAP allowable error", "MAP error delay", "Hold time"]
MAPIDarray = [103,33,34,35,139]
MAPtooltip = ["Manifold air pressure above which the LED instantly lights red. Set this below your over boost protection threshold in the ECU.","Maximum MAP/boost error above target pressure before the LED lights orange.","The delay in milliseconds between the target error threshold being exceeded and the light showing. Allow enough time for boost to stabilise.","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(MAPnamearray)
VariableIDArray.append(MAPIDarray)
ToolTipArray.append(MAPtooltip)
Channelid.append(37)

AFRnamearray = ["AFR Error LED", "Max AFR Error", "AFR Warning Delay", "AFR Warning Min TPS", "Hold time"]
AFRIDarray = [104,48,49,51,143]
AFRtooltip = ["Maximum AFR error from target before the LED lights red for lean or blue for rich.","The delay in milliseconds between the target error threshold being exceeded and the light showing. Allow enough time for AFR to stabilise.", "Minimum TPS value at which a warning will trigger. Ensure this is above the overrun fuel cut threshold.","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(AFRnamearray)
VariableIDArray.append(AFRIDarray)
ToolTipArray.append(AFRtooltip)
Channelid.append(46)

IATnamearray = ["Intake Temp LED", "IAT Max", "IAT Min", "Hold time"]
IATIDarray = [105,28,29,137]
IATtooltip = ["Intake temperature above which the LED lights red","Intake temperature below which the LED lights blue","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(IATnamearray)
VariableIDArray.append(IATIDarray)
ToolTipArray.append(IATtooltip)
Channelid.append(30)

FuelPnamearray = ["Fuel Pressure LED", "Fuel P Nominal", "Fuel P allowable error", "Fuel MAP referenced?", "Hold time"]
FuelPIDarray = [106,23,24,27,136]
FuelPtooltip = ["Expected fuel pressure when the intake manifold is at atmospheric pressure","Allowable error between nominal and measured fuel pressure", "Is your fuel pressure regulator MAP referenced? Set 1 for yes, 0 for no.","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(FuelPnamearray)
VariableIDArray.append(FuelPIDarray)
ToolTipArray.append(FuelPtooltip)
Channelid.append(22)

Battnamearray = ["Batt Voltage LED", "Batt V Max", "Batt V Min", "Hold time"]
BattIDarray = [107,39,40,140]
Batttooltip = ["Battery voltage above which the LED lights red","Battery voltage below which the LED lights blue","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(Battnamearray)
VariableIDArray.append(BattIDarray)
ToolTipArray.append(Batttooltip)
Channelid.append(41)

Injnamearray = ["Injector Duty LED", "Inj. Duty Max", "Hold time"]
InjIDarray = [108,42,141]
Injtooltip = ["Injector Duty above which the LED lights red","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(Injnamearray)
VariableIDArray.append(InjIDarray)
ToolTipArray.append(Injtooltip)
Channelid.append(43)

Knocknamearray = ["Knock Detection LED", "Knock TPS Min", "Knock MAP Min", "Hold time"]
KnockIDarray = [109,58,59,142]
Knocktooltip = ["Minimum throttle position for knock warning", "Minimum manifold pressure for knock warning","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(Knocknamearray)
VariableIDArray.append(KnockIDarray)
ToolTipArray.append(Knocktooltip)
Channelid.append(44)

EGTnamearray = ["EGT LED", "EGT Max", "Hold time"]
EGTIDarray = [110,31,138]
EGTtooltip = ["Exhaust Gas Temperature above which the LED lights red","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(EGTnamearray)
VariableIDArray.append(EGTIDarray)
ToolTipArray.append(EGTtooltip)
Channelid.append(32)

GPT1namearray = ["GPT1 LED", "GPT1 Min", "GPT1 Max", "Hold time"]
GPT1IDarray = [131,52, 53,144]
GPT1tooltip = ["Minimum allowable value for GPT1","Maximum allowable value for GPT1","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(GPT1namearray)
VariableIDArray.append(GPT1IDarray)
ToolTipArray.append(GPT1tooltip)
Channelid.append(56)

GPT2namearray = ["GPT2 LED", "GPT2 Min", "GPT2 Max", "Hold time"]
GPT2IDarray = [132,54, 55,145]
GPT2tooltip = ["Minimum allowable value for GPT2","Maximum allowable value for GPT2","Time for which warning LED is held after going beyond limits"]
VariableNameArray.append(GPT2namearray)
VariableIDArray.append(GPT2IDarray)
ToolTipArray.append(GPT2tooltip)
Channelid.append(57)


ser = serial.Serial()
serFlag = 0
def serial_connect(self,com_port,baud_rate):
    Version = 0
    Sentinel=0
    try:
        ser.close()
        ser.baudrate = 115200
        ser.port = com_port
        ser.timeout = 1
        ser._xonxoff=1
        ser.bytesize=serial.EIGHTBITS
        ser.parity=serial.PARITY_NONE
        ser.stopbits=serial.STOPBITS_ONE
        ser.close()
        ser.open()
        global serFlag
        
        serFlag = 1
        
        mycommand = "<0?>"
        ser.write(mycommand.encode())
        for i in range(2):
            response = str(ser.readline())
            if 'Sentinel' in response:
                Sentinel = 1
                break
        
    except:
        print("Failed to open "+com_port)
        
    if Sentinel ==1:
        time.sleep(0.25)
        ser.flush()
        print("Sentinel Found!")
        Version = send("<301?>",1)
        print("Version " + '%.2f' % Version)
        
        if int(Version) >=1:
            self.com_menu.set(com_port)
            print("com set")
            self.com_menu.configure(fg_color="green")
            CANread(self)
            getAllLEDcol(self)
            getbrightness(self)
            getConfigVals(self)
            ReadVariables(self)
            if Version >=1.1:
                createESPcontrols(self)
                readESPvariables(self, Version)
    
        
    return Version
    

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DigiTune Sentinel Configurator V1.13")
        self.geometry(f"{1340}x{700}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(15, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DigiTune Sentinel", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(10, 5))
        

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="sw")
        self.appearance_mode_label.grid(row=8, column=0, padx=20, pady=(5, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["System", "Light", "Dark"],
                                                                       command=self.change_appearance_mode_event, anchor = "nw")
        self.appearance_mode_optionemenu.grid(row=9, column=0, padx=20, pady=(5, 5))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="sw")
        self.scaling_label.grid(row=10, column=0, padx=20, pady=(5, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event, anchor = "nw")
        self.scaling_optionemenu.grid(row=11, column=0, padx=20, pady=(5, 5))
        

        self.entry = customtkinter.CTkEntry(self, placeholder_text="Command")
        self.entry.grid(row=4, column=1, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.entry.bind(sequence='<Return>',command=self.sendbuttonenter)

        self.send_button = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text="Send Command", text_color=("gray10", "#DCE4EE"), command = self.sendbuttonpress)
        self.send_button.grid(row=4, column=2, padx=(20, 20), pady=(20, 20), sticky="nsew")
        

        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        
        
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select COM Port")
        self.com_list_label = customtkinter.CTkLabel(self.sidebar_frame, text="COM Port:", anchor="w")
        self.com_list_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.com_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=[*com_port_list],command=self.change_com_port_event)
        self.com_menu.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.com_menu.bind(sequence='<Enter>',command=self.updateports)
        
        self.baud_list_label = customtkinter.CTkLabel(self.sidebar_frame, text="CAN bitrate (kbps):", anchor="sw")
        self.baud_list_label.grid(row=2, column=0, padx=20, pady=(10, 5))
        self.baud_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["250","500"],command=self.change_can_baud_event, anchor = "nw")
        self.baud_menu.grid(row=3, column=0, padx=20, pady=(5, 10))
        

        
        self.shift_frame = customtkinter.CTkFrame(self, fg_color="transparent",height=50)
        self.shift_frame.grid(row=0, column=1, columnspan=2, padx=(20, 0), pady=(5, 0), sticky="new")

        
        self.led_label=[]
        self.led_label=[0 for i in range(10)]
        self.ledcol=[]
        self.ledcol=[0 for i in range(10)]
        
        for i in range(10):
            
            self.led_label[i] = customtkinter.CTkLabel(self.shift_frame, text=f"LED {i+1}", anchor="w",width=90)
            self.led_label[i].grid(row=2, column=i, padx=(1, 1), pady=(0, 0))
            self.ledcol[i] = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],width=90,command=self.change_led_colour_event)
            self.ledcol[i].grid(row=3, column=i, padx=(1, 1), pady=(1, 1))
            

        self.brightness_label = customtkinter.CTkLabel(self.shift_frame, text="Brightness:", anchor="w",width=90)
        self.brightness_label.grid(row=4, column=0, padx=(1, 1), pady=(0, 0))
        self.brightness_slider = customtkinter.CTkSlider(self.shift_frame, from_=0.05, to=1, number_of_steps=100,command = self.change_brightness)
        self.brightness_slider.grid(row=4, column=1, columnspan=9, padx=(20, 10), pady=(0, 0), sticky="ew")
        
        self.show_shift_switch = customtkinter.CTkSwitch(master=self.shift_frame, text="Demo Shift Lights",command = self.change_showshift)
        self.show_shift_switch.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 10))
        
        self.Pattern_label = customtkinter.CTkLabel(self.shift_frame, text="LED direction:", anchor="e",width=80)
        self.Pattern_label.grid(row=1, column=3, columnspan=2, padx=(10, 10), pady=(0, 10))
        
        self.pattern_menu = customtkinter.CTkOptionMenu(self.shift_frame, values=["Left to Right","Outside to Inside"],command=self.change_direction,)
        self.pattern_menu.grid(row=1, column=4, columnspan=3, padx=20, pady=(0, 10))
        
        
        self.Priority_label = customtkinter.CTkLabel(self.shift_frame, text="LED priority:", anchor="e",width=80)
        self.Priority_label.grid(row=1, column=7, columnspan=1, padx=(10, 0), pady=(0, 10))
        
        self.Priority_menu = customtkinter.CTkOptionMenu(self.shift_frame, values=["Shift","Warning"],command=self.change_priority,anchor="w")
        self.Priority_menu.grid(row=1, column=8, columnspan=2, padx=0, pady=(0, 10))
        

        self.start_offset_label = customtkinter.CTkLabel(self.shift_frame, text="Start Offset RPM:", anchor="ne",width=90)
        self.start_offset_label.grid(row=6, column=0, padx=(1, 1), pady=(0, 0))
        self.shift_start_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="Start Offset",width=80,)
        self.shift_start_offset.grid(row=6, column=1, columnspan=1, padx=(5, 0), pady=(00, 10), sticky="nsew")
        ToolTip(self.shift_start_offset, msg="How many RPM before the hard cut limiter do you want the first shift light to appear?", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        self.end_offset_label = customtkinter.CTkLabel(self.shift_frame, text="End Offset RPM:", anchor="ne",width=90)
        self.end_offset_label.grid(row=6, column=3, padx=(1, 1), pady=(0, 0))
        self.shift_end_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="End Offset",width=80)
        self.shift_end_offset.grid(row=6, column=4, columnspan=1, padx=(5, 0), pady=(0, 10), sticky="nsew")
        ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        self.flash_offset_label = customtkinter.CTkLabel(self.shift_frame, text="Flash Offset RPM:", anchor="ne",width=80)
        self.flash_offset_label.grid(row=6, column=5,columnspan = 2, padx=(75, 1), pady=(0, 0))
        self.flash_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="Flash Offset",width=80)
        self.flash_offset.grid(row=6, column=7, columnspan=1, padx=(5, 0), pady=(0, 10), sticky="nsew")
        ToolTip(self.flash_offset, msg="How many RPM before the hard cut limiter do you want all lights to flash? Note: consider soft cut offset", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        self.shift_start_offset.bind(sequence='<Return>',command=self.change_offsets)
        self.shift_end_offset.bind(sequence='<Return>',command=self.change_offsets)
        self.flash_offset.bind(sequence='<Return>',command=self.change_offsets)
        
        self.param_frame = customtkinter.CTkScrollableFrame(self, label_text="Warning Configuration Parameters",height=400)
        self.param_frame.grid(row=1, rowspan=3, column=1, columnspan=2, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.param_frame.grid_columnconfigure(12, weight=1)
        
        self.reset_button = customtkinter.CTkButton(master=self, text="Reset All to Defaults", command = self.resetAll)
        self.reset_button.grid(row=4, column=0, padx=(20, 20), pady=(0, 00))
        
        self.firmware_button = customtkinter.CTkButton(master=self.sidebar_frame, anchor='w', text="Upgrade Firmware", command = self.WriteFirmware)
        self.firmware_button.grid(row=14, column=0, padx=(40, 40), pady=(45, 0), sticky="nsew")

                
        self.toplevel_window = None


        
        
        self.VariableDropdowns=[]
        self.VariableDropdowns=[0 for i in range(20)]
        self.VariableEntries=[]
        self.VariableEntries=[ [0]*5 for i in range(20)]
        

        
        

        numRows = len(VariableIDArray)
        
        for i in range(numRows):
            Names = VariableNameArray[i]
            IDs = VariableIDArray[i]
            NumFields = len(Names)
            self.New_label = customtkinter.CTkLabel(self.param_frame, text=Names[0], anchor="e",width=40)
            self.New_label.grid(row=i, column=0, columnspan=1, padx=(1, 1), pady=(5, 5))
            self.New_label.bind("<Button-1>", lambda e,i=i:label_click_handler(self,i))
            
            self.VariableDropdowns[i] = customtkinter.CTkOptionMenu(self.param_frame, values=["Disabled","1","2","3","4","5","6","7","8","9","10"],width=87)
            self.VariableDropdowns[i].grid(row=i, column=1, columnspan=1, padx=20, pady=(5, 5))
            self.VariableDropdowns[i].configure(command= partial(AssignLED, self,IDs[0],i))
            
            for j in range(NumFields-1):
                self.New_label = customtkinter.CTkLabel(self.param_frame, text=Names[j+1], anchor="e",width=80)
                self.New_label.grid(row=i, column=2*j+2, columnspan=1, padx=(1, 1), pady=(5, 5))
                self.VariableEntries[i][j] = customtkinter.CTkEntry(self.param_frame, width=90)
                self.VariableEntries[i][j].grid(row=i, column=2*j+3, columnspan=1, padx=(1, 1), pady=(5, 5), sticky="nsew")
                self.VariableEntries[i][j].bind(sequence='<Return>',command=partial(SetVariable,self,IDs[j+1],i,j))
                self.VariableEntries[i][j].bind(sequence='<FocusOut>',command=partial(SetVariable,self,IDs[j+1],i,j))
                # ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
                # parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
                # fg="white", bg="orange", padx=7, pady=7)
                
                ToolTip(self.VariableEntries[i][j], msg=ToolTipArray[i][j], delay=0, follow=True,
                parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
                fg="white", bg="blue", padx=7, pady=7)
        
        
        Theme = customtkinter.get_appearance_mode()
        global BoxFgColour
        if(Theme=="Dark"):
            BoxFgColour = "grey20"
        else:
            BoxFgColour = "white"

        self.update()
        autoconnect(self)
        
        
        
        

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        global BoxFgColour
        if new_appearance_mode == "Dark":
            BoxFgColour = "grey20"
        else:
            BoxFgColour = "white"
        
        
        
    def change_com_port_event(self, new_com_port: str):
        self.com_menu.configure(fg_color="yellow")
        serial_connect(self,new_com_port,"115200")

    def resetAll(self):
        print("RESET")
        send("<300?>",0)
        time.sleep(1)
        ser.flush()
        CANread(self)
        getAllLEDcol(self)
        getbrightness(self)
        getConfigVals(self)
        ReadVariables(self)
        if Version >= 1.1:
            readESPvariables(self, Version)
        
    def change_can_baud_event(self, new_baud_rate: str):
        CANwrite(self)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        CANread(self)
        
    def change_led_colour_event(self,colour):
        writeAllLEDcol(self)
        
    def change_flash_colour_event(self,colour):
        
        colnum=(colour_to_number(self.flashcol.get()))
        command = ("<121,"+str(colnum)+">")
        send(command,0)
        
        try:
            self.flashcol.configure(fg_color=colour)
        except:
            self.flashcol.configure(fg_color="grey")

    def change_dynamic_shift(self,mode):
        if (mode == "Dynamic Shift"):
            send("<206,1>",0)
        else:
            send("<206,0>",0)
            
        SetShiftLabels(self)
        
    def change_brightness(self,brightness):
        scaled_brightness = 100*pow(brightness,1.5)
        send("<201,"+str(scaled_brightness)+">",0)
        time.sleep(0.1)
        
    def change_showshift(self):
        state=self.show_shift_switch.get()
        if state==1:
            show_lights()
        else:
            hide_lights()
            
    def change_direction(self,directionstr):
        if directionstr=="Outside to Inside":
            send("<8,1>",0)
        else:
            send("<8,0>",0)
            
    def change_priority(self,directionstr):
        if directionstr=="Warning":
            send("<205,1>",0)
        else:
            send("<205,0>",0)
        
    def change_offsets(self,value):
        
        startoffset = self.shift_start_offset.get()
        endoffset = self.shift_end_offset.get()
        flashoffset = self.flash_offset.get()
        if self.start_offset_label.cget("text") == "Start Offset RPM:":
            send("<7,"+str(startoffset)+">", 0)
            send("<5,"+str(endoffset)+">", 0)
            send("<6,"+str(flashoffset)+">", 0)
        else:
            send("<1,"+str(startoffset)+">", 0)
            send("<2,"+str(endoffset)+">", 0)
            send("<3,"+str(flashoffset)+">", 0)

        self.shift_start_offset.configure(fg_color="green")
        self.shift_end_offset.configure(fg_color="green")
        self.flash_offset.configure(fg_color="green")
        root.update()
        time.sleep(0.2)
        self.shift_start_offset.configure(fg_color=BoxFgColour)
        self.shift_end_offset.configure(fg_color=BoxFgColour)
        self.flash_offset.configure(fg_color=BoxFgColour)
        
        def change_thresholds(self,value):
            
            startoffset = self.shift_start_offset.get()
            endoffset = self.shift_end_offset.get()
            flashoffset = self.flash_offset.get()
            send("<1,"+str(startoffset)+">", 0)
            send("<2,"+str(endoffset)+">", 0)
            send("<3,"+str(flashoffset)+">", 0)

            self.shift_start_offset.configure(fg_color="green")
            self.shift_end_offset.configure(fg_color="green")
            self.flash_offset.configure(fg_color="green")
            root.update()
            time.sleep(0.2)
            self.shift_start_offset.configure(fg_color=BoxFgColour)
            self.shift_end_offset.configure(fg_color=BoxFgColour)
            self.flash_offset.configure(fg_color=BoxFgColour)
        
    
    def sendbuttonpress(self):
        command = self.entry.get()
        print(send(command,1))
        self.entry.delete(0, 'end')
        
    def sendbuttonenter(self,event):
        command = self.entry.get()
        send(command,0)
        self.entry.delete(0, 'end')
        
    def updateports(self,event):
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        self.com_menu.configure(values = com_port_list)
        
    def WriteFirmware(self):
        
        print('%.2f' % Version)
        if ((Version<1.1) & (Version>0.0)):
            FirmwareFile = filedialog.askopenfilename(filetypes=[("Hex files", "*.hex")],title="Select Firmware File")
            ser.close()
            com_port=self.com_menu.get()
            shellcommand = "avrdude -p m328p -c arduino -P "+com_port+" -C avrdude.conf -U flash:w:"+'"'+FirmwareFile+'":i'
            
        else:
            print("ESP")
            FirmwareFile = filedialog.askopenfilename(filetypes=[("Bin files", "*.bin")],title="Select Firmware File")
            com_port = self.com_menu.get()
            ser.close()
            shellcommand = "esptool.exe --chip esp32c3 --port "+com_port+" --baud 921600  --before default_reset --after hard_reset write_flash  -z --flash_mode dio --flash_freq 80m --flash_size 4MB 0x0 "+'"esp.ino.bootloader.bin" 0x8000 "esp.ino.partitions.bin" 0xe000 "boot_app0.bin" 0x10000 '+'"'+FirmwareFile+'"' 
            
            
        self.firmware_button.configure(fg_color="yellow")
        root.update()
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it
        self.toplevel_window.focus()
        self.toplevel_window.title = "Upgrading Firmware"
        self.toplevel_window.grab_set()
        self.toplevel_window.update_idletasks()
        self.toplevel_window.update()
        
        window = customtkinter.CTkToplevel()
        window.geometry("400x90")
        window.wm_title("Process is Running")
        window.update_idletasks() # show the window
        # time.sleep(2)
        print(shellcommand)
        subprocess.run(shellcommand,shell=False)
        
        self.toplevel_window.destroy()
        window.destroy()
        
        
            
        self.firmware_button.configure(fg_color="green")
        root.update()
        time.sleep(1)
        serial_connect(self,com_port,"115200")
        
    def change_auto_brightness(self,mode):
        if mode == "Auto Brightness":
            send("<207,1>",0)
        else:
            send("<207,0>",0)
            
    def change_termination(self,state):
        if state == "Enabled":
            send("<202,1>",0)
        else:
            send("<202,0>",0)
            
            
    def change_units(self,state):
        if state == "°F":
            send("<209,1>",0)
        else:
            send("<209,0>",0)
            
    def change_ECU(self,state):
        match state:
            case "Auto Detect":
                send("<213,0>",0)
            case "OBD":
                send("<213,1>",0)
            case "ME":
                send("<213,2>",0)
            case "Megasquirt":
                send("<213,3>",0)
            case "Haltech":
                send("<213,4>",0)
            case "MaxxECU":
                send("<213,5>",0)
            case "Link":
                send("<213,6>",0)
            case _:
                send("<213,0>",0)
            
            
    
        
    def com_port_update():
        global ports
        global com_port_list
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select COM Port")
        


def SetVariable(self,ID,i,j,event):
    Value = self.VariableEntries[i][j].get()
    send("<"+str(ID)+","+str(Value)+">",0)
    self.VariableEntries[i][j].configure(fg_color="green")
    root.update()
    time.sleep(0.2)
    self.VariableEntries[i][j].configure(fg_color=BoxFgColour)
    
def AssignLED(self,ID,VariableRow,LED):
    if LED == "Disabled":
        LED = 0
    command = "<"+str(ID)+","+str(int(LED)-1)+">"
    send(command,0)

        
    
def ReadVariables(self):
    global VariableNameArray
    global VariableIDArray
    numRows = len(VariableIDArray)
    
    for i in range(numRows):
        Names = VariableNameArray[i]
        IDs = VariableIDArray[i]
        NumFields = len(Names)
        
        # if IDs[0] < 111 or  Version > 1.02:
        
        AssignedLED = send("<"+str(IDs[0])+"?>",1)+1
        if AssignedLED >10:
            AssignedLED = AssignedLED-10
        if AssignedLED == 0:
            AssignedLED = "Disabled"
        self.VariableDropdowns[i].set(str(AssignedLED))
        for j in range(NumFields-1):
            Value = send("<"+str(IDs[j+1])+"?>",1)  
            self.VariableEntries[i][j].delete(0, 'end')
            self.VariableEntries[i][j].insert(0,str(Value))
            
    
        
def send(mycommand,response):
   ser.flushInput()
   resultnum=0;
   if serFlag==1:
       ser.write(mycommand.encode())
       if response == 1:
           result = ser.readline()
           if len(result)>0:
               if re.search(r'\d', str(result)):
                   nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
                   floatresult = float(nums.search(result.decode()).group(0))
                   intonlyresult = int(floatresult)                  
                   if (intonlyresult == floatresult):
                       resultnum = intonlyresult
                   else:
                       resultnum = floatresult
               else:
                   resultnum = -1
           
   return resultnum
   
def show_lights():
    MaxRPM = (send("<2?>",1))
    send('<11,'+str(MaxRPM)+'>',0)
    send('<204,1>',0)
def hide_lights():
    send('<11,0>',0)
    send('<204,0>',0)
    
def getAllLEDcol(self):
    LEDcol=["0" for i in range(10)]
    for i in range(10):
        LEDcol[i] = getLEDcol(i)
        self.ledcol[i].set(LEDcol[i])
        try:
            self.ledcol[i].configure(fg_color=getLEDcol(i))
        except:
            self.ledcol[i].configure(fg_color="grey")
    Direction = send('<8?>',1)
    
    if Direction ==1:
        self.pattern_menu.set("Outside to Inside")
    else:
        self.pattern_menu.set("Left to Right")
    LEDPriority = send('<205?>',1)
    if LEDPriority ==1:
        self.Priority_menu.set("Warning")
    else:
        self.Priority_menu.set("Shift")
        
    
        
def getbrightness(self):
    brightness = send("<201?>",1)
    brightness_scaled = pow(brightness/100,1/1.5)
    self.brightness_slider.set(brightness_scaled)


    
    
def getLEDcol(led):
    colnum = int(send("<1"+str(led+11)+"?>",1))
    colstr = numbers_to_colour(colnum)

    return colstr
    

def writeAllLEDcol(self):
    for i in range(10):
        writeLEDcol(i,self.ledcol[i].get())
        try:
            colorname = self.ledcol[i].get()
            self.ledcol[i].configure(fg_color=colorname)
        except:
            self.ledcol[i].configure(fg_color="grey")

    
def writeLEDcol(led,colour):
    colnum=(colour_to_number(colour))
    command = ("<1"+str(led+11)+","+str(colnum)+">")
    send(command,0)
    


    
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

def getConfigVals(self):
    ser.flushInput()
    send("<1?>",1)
    if self.start_offset_label.cget("text")== "Start Offset RPM:":
        startoffset = send("<7?>", 1)
        endoffset = send("<5?>", 1)
        flashoffset = send("<6?>", 1)
        
    else:
        startoffset = send("<1?>", 1)
        endoffset = send("<2?>", 1)
        flashoffset = send("<3?>", 1)
    
    
    self.shift_start_offset.delete(0, 'end')
    self.shift_end_offset.delete(0, 'end')
    self.flash_offset.delete(0, 'end')
    
    self.shift_start_offset.insert(0,str(startoffset))
    self.shift_end_offset.insert(0,str(endoffset))
    self.flash_offset.insert(0,str(flashoffset))
    


def CANwrite(self):
    baud = int(self.baud_menu.get())
    send("<200,"+str(baud)+">",0)
    
    
def CANread(self):
    self.baud_menu.set(send("<200?>",1))
    
def autoconnect(self):
    self.com_menu.configure(fg_color="yellow")
    self.update()
    self.update_idletasks()
    self.focus()
    if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
        self.toplevel_window = AutoConnectWindow(self)  # create window if its None or destroyed
    else:
        self.toplevel_window.focus()  # if window exists focus it
    self.toplevel_window.focus()
    self.toplevel_window.title = "Scanning for devices"
    self.toplevel_window.grab_set()
    self.toplevel_window.update_idletasks()
    self.toplevel_window.update()

    window = customtkinter.CTkToplevel()
    window.geometry("400x90")
    window.wm_title("Process is Running")
    window.update_idletasks() # show the window
    self.update_idletasks()
    self.update()
    window.destroy()
    ports = serial.tools.list_ports.comports()
    com_port_list = [com[0] for com in ports]
    self.com_menu.configure(values = com_port_list)
    global Version
    Version = 0
    for com_port in com_port_list:
        Version = serial_connect(self,com_port,115200)
        if Version >=1:
            break
    
    
    self.toplevel_window.destroy()
    if Version==0:
        self.com_menu.configure(fg_color="red")
    if Version >=1:    
        self.logo_label.configure(text = ("DigiTune Sentinel \n" + '%.2f' % Version))
        
def get_units(self):
    unitInt = send("<209?>",1)
    if unitInt == 1:
        unit = "°F"
    else:
        unit = "°C"            
    self.units.set(unit)
    
def get_ECU(self):
    unitInt = send("<213?>",1)
    match unitInt:
        case -1:
            ECU = "None"
        case 0:
            ECU = "Auto Detect"
        case 1:
            ECU = "OBD"
        case 2:
            ECU = "ME"
        case 3:
            ECU = "Megasquirt"
        case 4:
            ECU = "Haltech"
        case 5:
            ECU = "MaxxECU"
        case 6:
            ECU = "Link"
        case _:
            ECU = "Unknown"
            
                    
         
    self.ECU.set(ECU)

    

    
def createESPcontrols(self):
    self.flashcollabel = customtkinter.CTkLabel(self.shift_frame, text="Flash Colour", anchor="w",width=90)
    self.flashcollabel.grid(row=2, column=10, padx=(1, 1), pady=(0, 0))
    self.flashcol = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],width=90,command=self.change_flash_colour_event)
    self.flashcol.grid(row=3, column=10, padx=(1, 1), pady=(1, 1))
    self.dynamicshift = customtkinter.CTkOptionMenu(self.shift_frame, values=["Static Shift", "Dynamic Shift"],width=90,command=self.change_dynamic_shift)
    self.dynamicshift.grid(row=6, column=10, padx=(1, 1), pady=(0, 0))
    self.autobrightness = customtkinter.CTkOptionMenu(self.shift_frame, values=["Auto Brightness", "Fixed Brightness"],width=90,command=self.change_auto_brightness)
    self.autobrightness.grid(row=4, column=10, padx=(1, 1), pady=(0, 0))
    
    self.term_label = customtkinter.CTkLabel(self.sidebar_frame, text="CAN 120 ohm termination:", anchor="sw")
    self.term_label.grid(row=4, column=0, padx=20, pady=(5, 0))
    self.term = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Enabled","Disabled"],command=self.change_termination, anchor="nw")
    self.term.grid(row=5, column=0, padx=20, pady=(5, 5))
    self.baud_menu.configure(values = ["250", "500", "1000"])
    
    self.units_label = customtkinter.CTkLabel(self.sidebar_frame, text="Temperature Units:", anchor="sw")
    self.units_label.grid(row=6, column=0, padx=20, pady=(5, 5))
    self.units = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["°C","°F"],command=self.change_units, anchor="nw")
    self.units.grid(row=7, column=0, padx=20, pady=(0, 5))
    
    self.ECU_label = customtkinter.CTkLabel(self.sidebar_frame, text="ECU:", anchor="sw")
    self.ECU_label.grid(row=12, column=0, padx=20, pady=(5, 5))
    self.ECU = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Auto Detect", "OBD", "ME", "Megasquirt", "Haltech", "MaxxECU", "Link"],command=self.change_ECU, anchor="nw")
    self.ECU.grid(row=13, column=0, padx=20, pady=(0, 5))
    
def readESPvariables(self, Version):
    
    getflashcol(self)
    getshiftmode(self)
    getCANterm(self)
    SetShiftLabels(self)
    get_units(self)
    if Version > 1.14:
        get_ECU(self)
    
def SetShiftLabels(self):
    if self.dynamicshift.get()=="Dynamic Shift":
       self.start_offset_label.configure(text="Start Offset RPM:")
       ToolTip(self.shift_start_offset, msg="How many RPM before the hard cut limiter do you want the first shift light to appear?", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.end_offset_label.configure(text="End Offset RPM:")
       ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.flash_offset_label.configure(text="Flash Offset RPM:")
       ToolTip(self.flash_offset, msg="How many RPM before the hard cut limiter do you want all lights to flash? Note: consider soft cut offset", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.shift_start_offset.bind(sequence='<Return>',command=self.change_offsets)
       self.shift_end_offset.bind(sequence='<Return>',command=self.change_offsets)
       self.flash_offset.bind(sequence='<Return>',command=self.change_offsets)
       
    else:
       self.start_offset_label.configure(text="Start RPM:")
       ToolTip(self.shift_start_offset, msg="How many RPM before the hard cut limiter do you want the first shift light to appear?", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.end_offset_label.configure(text="End RPM:")
       ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.flash_offset_label.configure(text="Flash RPM:")
       ToolTip(self.flash_offset, msg="How many RPM before the hard cut limiter do you want all lights to flash? Note: consider soft cut offset", delay=0, follow=True,
       parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
       fg="white", bg="blue", padx=7, pady=7)
       
       self.shift_start_offset.bind(sequence='<Return>',command=self.change_offsets)
       self.shift_end_offset.bind(sequence='<Return>',command=self.change_offsets)
       self.flash_offset.bind(sequence='<Return>',command=self.change_offsets)
       
    getConfigVals(self)
           
    
    def com_port_list(self):
        global ports
        global com_port_list
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select an Option")
        # if dbg == 1:
        self.com_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=[*com_port_list])
        
def label_click_handler(self,i):
    value = send("<"+str(Channelid[i])+"?>",1);
    
    
    displaymessage = "Current channel value is " + str(value)
    print(displaymessage)
    tkinter.messagebox.showinfo(title="Value check", message=displaymessage)
    
def getflashcol(self):
    colnum = send("<121?>",1)
    colstr = numbers_to_colour(colnum)
    self.flashcol.set(colstr)
    try:
        self.flashcol.configure(fg_color=colstr)
    except:
        self.flashcol.configure(fg_color="grey")
        
def getshiftmode(self):
    ShiftModeInt = send("<206?>",1)
    
    if ShiftModeInt ==1:
        self.dynamicshift.set("Dynamic Shift")
    else:
        self.dynamicshift.set("Static Shift")
        
    self.dynamicshift.configure(command=self.change_dynamic_shift)
    
def autobright(self):
    AutoBrightnessInt = send("<207?>",1)
    if AutoBrightnessInt == 1:
        self.autobrightness.set("Auto Brightness")
    else:
        self.autobrightness.set("Fixed Brightness")
        
def getCANterm(self):
    CAN120Int = send("<202?>",1)
    if CAN120Int == 1:
        self.term.set("Enabled")
    else:
        self.term.set("Disabled")
    

        
def serial_close():
    global ser
    global serFlag
    try:
        hide_lights()
    except:
        print("no serial")
    serFlag = 0
    ser.close()
    
def on_closing():
    serial_close()
    root.destroy()
        

if __name__ == "__main__":
    
    root = App()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
