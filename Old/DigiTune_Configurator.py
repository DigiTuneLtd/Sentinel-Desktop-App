import customtkinter
import serial
import serial.tools.list_ports
import time
import re
from tktooltip import ToolTip
from functools import partial

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


VariableRow = 0

VariableNameArray =[]
VariableIDArray =[]


CLTnamearray = ["Coolant Temp LED", "CLT Max", "CLT Min"]
CLTIDarray = [100,12,13]
VariableNameArray.append(CLTnamearray)
VariableIDArray.append(CLTIDarray)

OilTnamearray = ["Oil Temp LED", "Oil T Max", "Oil T Min"]
OilTIDarray = [101,15,16]
VariableNameArray.append(OilTnamearray)
VariableIDArray.append(OilTIDarray)

OilPnamearray = ["Oil Pressure LED", "Oil P Max", "Oil P Min", "Oil P relief RPM", "Oil P cranking"]
OilPIDarray = [102,18,19,20,21]
VariableNameArray.append(OilPnamearray)
VariableIDArray.append(OilPIDarray)

MAPnamearray = ["MAP/Boost LED", "MAP abs. Max", "MAP allowable error", "MAP error delay"]
MAPIDarray = [103,33,34,35]
VariableNameArray.append(MAPnamearray)
VariableIDArray.append(MAPIDarray)

AFRnamearray = ["AFR Error LED", "Max AFR Error", "AFR Warning Delay", "AFR Warning Min TPS"]
AFRIDarray = [104,48,49,51]
VariableNameArray.append(AFRnamearray)
VariableIDArray.append(AFRIDarray)

IATnamearray = ["Intake Temp LED", "IAT Max", "IAT Min"]
IATIDarray = [105,28,29]
VariableNameArray.append(IATnamearray)
VariableIDArray.append(IATIDarray)

FuelPnamearray = ["Fuel Pressure LED", "Fuel P Nominal", "Fuel P allowable error", "Fuel MAP referenced?"]
FuelPIDarray = [106,23,24,27]
VariableNameArray.append(FuelPnamearray)
VariableIDArray.append(FuelPIDarray)

Battnamearray = ["Batt Voltage LED", "Batt V Max", "Batt V Min"]
BattIDarray = [107,39,40]
VariableNameArray.append(Battnamearray)
VariableIDArray.append(BattIDarray)

Injnamearray = ["Injector Duty LED", "Inj. Duty Max"]
InjIDarray = [108,42]
VariableNameArray.append(Injnamearray)
VariableIDArray.append(InjIDarray)

Knocknamearray = ["Knock Detection LED"]
KnockIDarray = [109]
VariableNameArray.append(Knocknamearray)
VariableIDArray.append(KnockIDarray)

EGTnamearray = ["EGT LED", "EGT Max"]
EGTIDarray = [110,31]
VariableNameArray.append(EGTnamearray)
VariableIDArray.append(EGTIDarray)


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
    time.sleep(0.8)
    response = ser.read(64)
    print(response.decode())
    

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("DigiTune Guardian Configurator")
        self.geometry(f"{1340}x{700}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="DigiTune Guardian", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        # self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
  
        # self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_event)
        # self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Command")
        self.entry.grid(row=4, column=1, columnspan=1, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.entry.bind(sequence='<Return>',command=self.sendbuttonenter)

        self.send_button = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text="Send Command", text_color=("gray10", "#DCE4EE"), command = self.sendbuttonpress)
        self.send_button.grid(row=4, column=2, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # create textbox
        # self.textbox = customtkinter.CTkTextbox(self, width=250)
        # self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # create tabview
        # self.tabview = customtkinter.CTkTabview(self, width=250)
        # self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.tabview.add("CTkTabview")
        # self.tabview.add("Tab 2")
        # self.tabview.add("Tab 3")
        # self.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        # self.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)

        # self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("CTkTabview"), dynamic_resizing=False,
        #                                                 values=["Value 1", "Value 2", "Value Long Long Long"])
        # self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        # self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("CTkTabview"),
        #                                             values=["Value 1", "Value 2", "Value Long....."])
        # self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        # self.string_input_button = customtkinter.CTkButton(self.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
        #                                                    command=self.open_input_dialog_event)
        # self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        # self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
        # self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

        # create radiobutton frame
        # self.radiobutton_frame = customtkinter.CTkFrame(self)
        # self.radiobutton_frame.grid(row=0, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.radio_var = tkinter.IntVar(value=0)
        # self.label_radio_group = customtkinter.CTkLabel(master=self.radiobutton_frame, text="CTkRadioButton Group:")
        # self.label_radio_group.grid(row=0, column=2, columnspan=1, padx=10, pady=10, sticky="")
        # self.radio_button_1 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=0)
        # self.radio_button_1.grid(row=1, column=2, pady=10, padx=20, sticky="n")
        # self.radio_button_2 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=1)
        # self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")
        # self.radio_button_3 = customtkinter.CTkRadioButton(master=self.radiobutton_frame, variable=self.radio_var, value=2)
        # self.radio_button_3.grid(row=3, column=2, pady=10, padx=20, sticky="n")

        # create slider and progressbar frame
        # self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        # self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        # self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        # self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        # self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        # self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")

        # self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        # self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        # self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        # self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        # create scrollable frame
        # self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="CTkScrollableFrame")
        # self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        # self.scrollable_frame.grid_columnconfigure(0, weight=1)
        # self.scrollable_frame_switches = []
        # for i in range(100):
        #     switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
        #     switch.grid(row=i, column=0, padx=10, pady=(0, 20))
        #     self.scrollable_frame_switches.append(switch)

        # create checkbox and switch frame
        # self.checkbox_slider_frame = customtkinter.CTkFrame(self)
        # self.checkbox_slider_frame.grid(row=1, column=3, padx=(20, 20), pady=(20, 0), sticky="nsew")
        # self.checkbox_1 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_1.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_2 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_2.grid(row=2, column=0, pady=(20, 0), padx=20, sticky="n")
        # self.checkbox_3 = customtkinter.CTkCheckBox(master=self.checkbox_slider_frame)
        # self.checkbox_3.grid(row=3, column=0, pady=20, padx=20, sticky="n")

        # set default values
        # self.sidebar_button_3.configure(state="disabled", text="Disabled CTkButton")
        # self.checkbox_3.configure(state="disabled")
        # self.checkbox_1.select()
        # self.scrollable_frame_switches[0].select()
        # self.scrollable_frame_switches[4].select()
        # # self.radio_button_3.configure(state="disabled")
        # self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")
        # self.optionmenu_1.set("CTkOptionmenu")
        # self.combobox_1.set("CTkComboBox")
        # self.slider_1.configure(command=self.progressbar_2.set)
        # self.slider_2.configure(command=self.progressbar_3.set)
        # self.textbox.insert("0.0", "CTkTextbox\n\n" + "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        # self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        # self.seg_button_1.set("Value 2")
        
        
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select COM Port")
        self.com_list_label = customtkinter.CTkLabel(self.sidebar_frame, text="COM Port:", anchor="w")
        self.com_list_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        self.com_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=[*com_port_list],command=self.change_com_port_event)
        self.com_menu.grid(row=1, column=0, padx=20, pady=(10, 10))
        
        self.baud_list_label = customtkinter.CTkLabel(self.sidebar_frame, text="CAN bitrate (kbps):", anchor="w")
        self.baud_list_label.grid(row=2, column=0, padx=20, pady=(10, 0))
        self.baud_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["250","500"],command=self.change_can_baud_event)
        self.baud_menu.grid(row=3, column=0, padx=20, pady=(10, 10))
        
        # self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Read CAN bitrate", command=self.sidebar_button_event)
        # self.sidebar_button_2.grid(row=4, column=0, padx=20, pady=10)
        
        self.shift_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.shift_frame.grid(row=0, column=1, columnspan=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.shift_frame.grid_columnconfigure(10, weight=1)
        self.shift_frame.grid_rowconfigure(4, weight=1)
        
        
        colourlist = ["Blank", "Green","Yellow","Orange","Red","Blue","Purple","White"]
        # self.led1_label = customtkinter.CTkLabel(self.shift_frame, text="LED 1", anchor="w",width=20)
        # self.led1_label.grid(row=2, column=0, padx=1, pady=(0, 0))
        # self.led1col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led1col.grid(row=3, column=0, padx=1, pady=(1, 1))
        
        # self.led2_label = customtkinter.CTkLabel(self.shift_frame, text="LED 2", anchor="w",width=20)
        # self.led2_label.grid(row=2, column=1, padx=1, pady=(0, 0))
        # self.led2col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led2col.grid(row=3, column=1, padx=1, pady=(1, 1))
        
        # self.led3_label = customtkinter.CTkLabel(self.shift_frame, text="LED 3", anchor="w",width=20)
        # self.led3_label.grid(row=2, column=2, padx=1, pady=(0, 0))
        # self.led3col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led3col.grid(row=3, column=2, padx=1, pady=(1, 1))
        
        # self.led4_label = customtkinter.CTkLabel(self.shift_frame, text="LED 4", anchor="w",width=20)
        # self.led4_label.grid(row=2, column=3, padx=1, pady=(0, 0))
        # self.led4col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led4col.grid(row=3, column=3, padx=1, pady=(1, 1))
        
        # self.led5_label = customtkinter.CTkLabel(self.shift_frame, text="LED 5", anchor="w",width=20)
        # self.led5_label.grid(row=2, column=4, padx=1, pady=(0, 0))
        # self.led5col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led5col.grid(row=3, column=4, padx=1, pady=(1, 1))
        
        # self.led6_label = customtkinter.CTkLabel(self.shift_frame, text="LED 6", anchor="w",width=20)
        # self.led6_label.grid(row=2, column=5, padx=1, pady=(0, 0))
        # self.led6col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led6col.grid(row=3, column=5, padx=1, pady=(1, 1))
        
        # self.led7_label = customtkinter.CTkLabel(self.shift_frame, text="LED 7", anchor="w",width=20)
        # self.led7_label.grid(row=2, column=6, padx=1, pady=(0, 0))
        # self.led7col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led7col.grid(row=3, column=6, padx=1, pady=(1, 1))
        
        # self.led8_label = customtkinter.CTkLabel(self.shift_frame, text="LED 8", anchor="w",width=20)
        # self.led8_label.grid(row=2, column=7, padx=1, pady=(0, 0))
        # self.led8col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led8col.grid(row=3, column=7, padx=1, pady=(1, 1))
        
        # self.led9_label = customtkinter.CTkLabel(self.shift_frame, text="LED 9", anchor="w",width=20)
        # self.led9_label.grid(row=2, column=8, padx=1, pady=(0, 0))
        # self.led9col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led9col.grid(row=3, column=8, padx=1, pady=(1, 1))
        
        # self.led10_label = customtkinter.CTkLabel(self.shift_frame, text="LED 10", anchor="w",width=20)
        # self.led10_label.grid(row=2, column=9, padx=1, pady=(0, 0))
        # self.led10col = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],command=self.change_led_colour_event,width=20)
        # self.led10col.grid(row=3, column=9, padx=1, pady=(1, 1))
        
        # self.led10_label = customtkinter.CTkLabel(self.shift_frame, text="LED 10", anchor="w",width=20)
        # self.led10_label.grid(row=2, column=9, padx=1, pady=(0, 0))
        
        self.led_label=[]
        self.led_label=[0 for i in range(10)]
        self.ledcol=[]
        self.ledcol=[0 for i in range(10)]
        
        for i in range(10):
            
            self.led_label[i] = customtkinter.CTkLabel(self.shift_frame, text=f"LED {i+1}", anchor="w",width=90)
            self.led_label[i].grid(row=2, column=i, padx=(1, 1), pady=(0, 0))
            self.ledcol[i] = customtkinter.CTkOptionMenu(self.shift_frame, values=[*colourlist],width=90,command=self.change_led_colour_event)
            self.ledcol[i].grid(row=3, column=i, padx=(1, 1), pady=(1, 1))
            
        # self.progressbar_1 = customtkinter.CTkProgressBar(self.shift_frame)
        # self.progressbar_1.grid(row=6, column=0,columnspan=10, padx=(20, 10), pady=(10, 10), sticky="ew")
        # self.progressbar_1.configure(mode="indeterminnate")
        # self.progressbar_1.start()
        self.brightness_label = customtkinter.CTkLabel(self.shift_frame, text="Brightness:", anchor="w",width=90)
        self.brightness_label.grid(row=4, column=0, padx=(1, 1), pady=(0, 0))
        self.brightness_slider = customtkinter.CTkSlider(self.shift_frame, from_=0.05, to=1, number_of_steps=100,command = self.change_brightness)
        self.brightness_slider.grid(row=4, column=1, columnspan=9, padx=(20, 10), pady=(0, 0), sticky="ew")
        
        self.show_shift_switch = customtkinter.CTkSwitch(master=self.shift_frame, text="Demo Shift Lights",command = self.change_showshift)
        self.show_shift_switch.grid(row=1, column=0, columnspan=4, padx=10, pady=(0, 20))
        
        self.Pattern_label = customtkinter.CTkLabel(self.shift_frame, text="LED direction:", anchor="w",width=80)
        self.Pattern_label.grid(row=1, column=4, columnspan=2, padx=(10, 10), pady=(0, 20))
        
        self.pattern_menu = customtkinter.CTkOptionMenu(self.shift_frame, values=["Left to Right","Outside to Inside"],command=self.change_direction,)
        self.pattern_menu.grid(row=1, column=5, columnspan=3, padx=20, pady=(0, 20))
        

        self.start_offset_label = customtkinter.CTkLabel(self.shift_frame, text="Start Offset RPM:", anchor="e",width=90)
        self.start_offset_label.grid(row=6, column=0, padx=(1, 1), pady=(0, 0))
        self.shift_start_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="Start Offset",width=90,)
        self.shift_start_offset.grid(row=6, column=1, columnspan=2, padx=(20, 0), pady=(00, 10), sticky="nsew")
        ToolTip(self.shift_start_offset, msg="How many RPM before the hard cut limiter do you want the first shift light to appear?", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        self.end_offset_label = customtkinter.CTkLabel(self.shift_frame, text="End Offset RPM:", anchor="e",width=90)
        self.end_offset_label.grid(row=6, column=3, padx=(1, 1), pady=(0, 0))
        self.shift_end_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="End Offset",width=90)
        self.shift_end_offset.grid(row=6, column=4, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")
        ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        self.flash_offset_label = customtkinter.CTkLabel(self.shift_frame, text="Flash Offset RPM:", anchor="e")
        self.flash_offset_label.grid(row=6, column=7, padx=(1, 1), pady=(0, 0))
        self.flash_offset = customtkinter.CTkEntry(self.shift_frame, placeholder_text="Flash Offset")
        self.flash_offset.grid(row=6, column=8, columnspan=2, padx=(20, 0), pady=(0, 10), sticky="nsew")
        ToolTip(self.flash_offset, msg="How many RPM before the hard cut limiter do you want all lights to flash purple? Note: consider soft cut offset", delay=0, follow=True,
        parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
        fg="white", bg="blue", padx=7, pady=7)
        
        
        self.shift_end_offset.bind(sequence='<Return>',command=self.change_offsets)
        self.flash_offset.bind(sequence='<Return>',command=self.change_offsets)
        
        self.param_frame = customtkinter.CTkScrollableFrame(self, label_text="Warning Configuration Parameters")
        self.param_frame.grid(row=1, rowspan=2, column=1, columnspan=2, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.param_frame.grid_columnconfigure(10, weight=1)
        
        
        self.VariableDropdowns=[]
        self.VariableDropdowns=[0 for i in range(20)]
        self.VariableEntries=[]
        self.VariableEntries=[ [0]*5 for i in range(20)]
        

        
        
        print(VariableNameArray)
        print(VariableIDArray)
        numRows = len(VariableIDArray)
        
        for i in range(numRows):
            Names = VariableNameArray[i]
            IDs = VariableIDArray[i]
            NumFields = len(Names)
            self.New_label = customtkinter.CTkLabel(self.param_frame, text=Names[0], anchor="e",width=40)
            self.New_label.grid(row=i, column=0, columnspan=1, padx=(1, 1), pady=(5, 5))
            
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
        
        

        
        
        
        
        
        
    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
        print("CTkInputDialog:", dialog.get_input())

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        
    def change_com_port_event(self, new_com_port: str):
        serial_connect(new_com_port,"115200")
        CANread(self)
        getAllLEDcol(self)
        getbrightness(self)
        getConfigVals(self)
        ReadVariables(self)
        
    def change_can_baud_event(self, new_baud_rate: str):
        CANwrite(self)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        CANread(self)
        
    def change_led_colour_event(self,colour):
        writeAllLEDcol(self)
        
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
        print(directionstr)
        if directionstr=="Outside to Inside":
            send("<8,1>",0)
        else:
            send("<8,0>",0)
        
    def change_offsets(self,value):
        startoffset = self.shift_start_offset.get()
        endoffset = self.shift_end_offset.get()
        flashoffset = self.flash_offset.get()
        print(startoffset)
        send("<7,"+str(startoffset)+">", 0)
        send("<5,"+str(endoffset)+">", 0)
        send("<6,"+str(flashoffset)+">", 0)
        self.shift_start_offset.configure(fg_color="green")
        self.shift_end_offset.configure(fg_color="green")
        self.flash_offset.configure(fg_color="green")
        root.update()
        time.sleep(0.2)
        self.shift_start_offset.configure(fg_color="white")
        self.shift_end_offset.configure(fg_color="white")
        self.flash_offset.configure(fg_color="white")
        
    
    def sendbuttonpress(self):
        command = self.entry.get()
        send(command,0)
        self.entry.delete(0, 'end')
        
    def sendbuttonenter(self,event):
        command = self.entry.get()
        send(command,0)
        self.entry.delete(0, 'end')
            
        
# def createConfigEntries(self,Names,IDs):
#     global VariableRow
#     NumFields = len(Names)
#     # self.New_label = customtkinter.CTkLabel(self.param_frame, text=Names[0], anchor="e",width=40)
#     # self.New_label.grid(row=VariableRow, column=0, columnspan=1, padx=(1, 1), pady=(5, 5))
    
#     # self.VariableDropdowns[VariableRow] = customtkinter.CTkOptionMenu(self.param_frame, values=["Disabled","1","2","3","4","5","6","7","8","9","10"])
#     # self.VariableDropdowns[VariableRow].grid(row=VariableRow, column=1, columnspan=1, padx=20, pady=(5, 5))
#     # self.VariableDropdowns[VariableRow].configure(command= partial(AssignLED, self,IDs,VariableRow))
    
#     # for i in range(NumFields-1):
#     #     self.New_label = customtkinter.CTkLabel(self.param_frame, text=Names[i+1], anchor="e",width=80)
#     #     self.New_label.grid(row=VariableRow, column=2*i+2, columnspan=1, padx=(1, 1), pady=(5, 5))
#     #     self.VariableEntries[VariableRow][i] = customtkinter.CTkEntry(self.param_frame, width=90)
#     #     self.VariableEntries[VariableRow][i].grid(row=VariableRow, column=2*i+3, columnspan=1, padx=(1, 1), pady=(5, 5), sticky="nsew")
#     #     self.VariableEntries[VariableRow][i].bind(sequence='<Return>',command=partial(SetVariable,self,IDs,VariableRow))
#     #     # ToolTip(self.shift_end_offset, msg="How many RPM before the hard cut limiter do you want the final shift light to appear? Note: consider soft cut offset", delay=0, follow=True,
#     #     # parent_kwargs={"bg": "black", "padx": 3, "pady": 3},
#     #     # fg="white", bg="orange", padx=7, pady=7)
#     # VariableRow=VariableRow+1
    
        
    def com_port_update():
        global ports
        global com_port_list
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select COM Port")
        

def SetVariable(self,ID,i,j,event):
    Value = self.VariableEntries[i][j].get()
    send("<"+str(ID)+","+str(Value)+">",0)
    print(i)
    print(j)
    self.VariableEntries[i][j].configure(fg_color="green")
    root.update()
    time.sleep(0.2)
    self.VariableEntries[i][j].configure(fg_color="white")
    
def AssignLED(self,ID,VariableRow,LED):
    if LED == "Disabled":
        LED = -1
    send("Test Command: <"+str(ID)+","+str(LED)+">",0)

        
    
def ReadVariables(self):
    print("Test Reading Variables")
    global VariableNameArray
    global VariableIDArray
    print(VariableNameArray)
    print(VariableIDArray)
    numRows = len(VariableIDArray)
    
    for i in range(numRows):
        Names = VariableNameArray[i]
        IDs = VariableIDArray[i]
        NumFields = len(Names)
        print(IDs)
        AssignedLED = send("<"+str(IDs[0])+"?>",1)
        if AssignedLED == -1:
            AssignedLED = "Disabled"
        print(AssignedLED)
        self.VariableDropdowns[i].set(str(AssignedLED))
        for j in range(NumFields-1):
            print("Test")
            Value = send("<"+str(IDs[j+1])+"?>",1)
            self.VariableEntries[i][j].delete(0, 'end')
            self.VariableEntries[i][j].insert(0,str(Value))
            
    
        
def send(mycommand,response):
   resultnum=0;
   if serFlag==1:
       print(mycommand)
       ser.write(mycommand.encode())
       if response == 1:
           result = ser.readline()
           if len(result)>0:
               nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
               resultnum = int(float(nums.search(result.decode()).group(0)))
               # resultstrlist = re.findall(r'\b\d+\b',result.decode())
               # resultnum = int(resultstrlist[0])
               print(resultnum)
           
   return resultnum
   
def show_lights():
    MaxRPM = (send("<2?>",1))
    send('<11,'+str(MaxRPM)+'>',0)
def hide_lights():
    send('<11,0>',0)
    
def getAllLEDcol(self):
    LEDcol=["0" for i in range(10)]
    for i in range(10):
        LEDcol[i] = getLEDcol(i)
        self.ledcol[i].set(LEDcol[i])
        try:
            self.ledcol[i].configure(fg_color=getLEDcol(i))
        except:
            self.ledcol[i].configure(fg_color="grey")
        
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
    # writeLEDcol(1,self.led1col.get())
    # writeLEDcol(2,self.led2col.get())
    # writeLEDcol(3,self.led3col.get())
    # writeLEDcol(4,self.led4col.get())
    # writeLEDcol(5,self.led5col.get())
    # writeLEDcol(6,self.led6col.get())
    # writeLEDcol(7,self.led7col.get())
    # writeLEDcol(8,self.led8col.get())
    # writeLEDcol(9,self.led9col.get())
    # writeLEDcol(10,self.led10col.get())
    
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
    startoffset = send("<7?>", 1)
    endoffset = send("<5?>", 1)
    flashoffset = send("<6?>", 1)
    
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

       
        
        
    def com_port_list(self):
        global ports
        global com_port_list
        ports = serial.tools.list_ports.comports()
        com_port_list = [com[0] for com in ports]
        com_port_list.insert(0,"Select an Option")
        # if dbg == 1:
        #     print(com_port_list)
        self.com_menu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=[*com_port_list])
        
        # #Frame for the COM LIST
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

    def serial_print():
        global serFlag
        global ser
        global counter1
        global lastx
        global lasty
        x =""
        #print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
        #print("ID of process running task 1: {}".format(os.getpid()))
        # if(serFlag):
        #     if(ser.in_waiting>0):
        #         #
        #         try:
        #             x = ser.read(ser.in_waiting)
        #             lastx=x
        #             #x = ser.readline(ser.in_waiting)
        #             #x = ser.read_until(expected='\n', size=ser.in_waiting)
        #             #print(x)
        #             y = str(counter1)+": "+str(datetime.datetime.now())+" -> "+str(x.decode())
        #             lasty=y
        #             Lb2.insert(counter1, str(y))
        #             Lb2.see("end")
        #             #print (counter1)
        #             counter1 += 1
        #             #gFrame.after(100,serial_print)
        #         except:
        #             pass
        #     ser.flush()
        #     gFrame.after(100,serial_print)


    
        
        # t1 = threading.Thread(target = serial_print, args = (), daemon=1)
        # t1.start()
        #t1.join()
        """
        P1 = multiprocessing.Process(target = serial_print, args=())
        P1.start()
        P1.join()
        """
        #serial_print()
    # counter1 = 0;


        
def serial_close():
    global ser
    global serFlag
    serFlag = 0
    ser.close()
    
def on_closing():
    serial_close()
    root.destroy()
        
    # def submit_value(self):
    #     # if dbg == 1:
    #     #     print("selected option: {}".format(com_value_inside.get()))
    #     #     # print(" Baud Rate {}".format(baud_value_inside.get()))
    #     serial_connect(self.com_menu.get(),'115200')


if __name__ == "__main__":
    
    root = App()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
