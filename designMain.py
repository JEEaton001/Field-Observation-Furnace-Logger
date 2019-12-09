## GUI AND SENSOR SOFTWARE FOR FURNACE LOGGER
## By Kaitlyn Icopini, Franki Taylor, and James Eaton
##
## This software is designed to run a Rasberry Pi 3 B+ for the purpose of logging sensor information to a CSV file which is stored on a USB drive named "LOGGER"

# IMPORTS -------------------------------------------------------------------------------
from tkinter import *   # GUI functions
import os               # Used for system calls
from queue import *     # Imports Queue functionalit
import serial           # Allows for serial communication functions
import RPi.GPIO as GPIO # Enables communication with specific GPIO pins
import bme680           # BME680 communication and reading function

# For I2C communication to the analog to digital converter
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Used in config screen and reading from logger.ini
import subprocess
import configparser

from datetime import datetime   # Used for getting time from the system clock

# Used for graphing data on the Pi
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


# FUNCTIONS---------------------------------------------------------------------

# Turns on/off the backlight on the touchscreen when intrupt is triggered
def screenOnOff(channel):
    # when pin 19 is high, turn screen on
    if(GPIO.input(19)):
        os.system('sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"')
    # when pin 19 is low, turn screen off
    else:
        os.system('sudo bash -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"')

# Shows the config screen
def showConfig():
    forget()
    canvas.create_rectangle(0,0,800,600,fill="slate gray")
    back.place(x=20, y=380)
    dropMenu.place(x = 350, y = 150)
    config_label.place(x=280,y=120)

# When the dropdown menu in the config screen is click, the variable choice is changed depending on the selection
def config(*args):
    global choice
    global prevChoice    
    choice = tkvar.get()
    if choice != prevChoice:
        if choice == 'Celsius':
            prevChoice = choice
            setConfig(1)
        else:
            prevChoice = choice
            setConfig(2)

# Saves the selected config parameter in logger.ini
def setConfig(x):
    global choice
    configOp = configparser.ConfigParser()
    configOp.read('logger.ini')
    if x == 1:
        choice = configOp.get('User', 'tempUnit')
        configOp.set('User', 'tempUnit', 'Celsius')
        with open('logger.ini', "w") as configfile:
            configOp.write(configfile)
        print('Temp Unit After Change: ', configOp.get('User', 'tempUnit'))
    if x == 2:
        choice = configOp.get('User', 'tempUnit')
        configOp.set('User', 'tempUnit', 'Fahrenheit')
        with open('logger.ini', "w") as configfile:
            configOp.write(configfile)
        print('Temp Unit After Change: ', configOp.get('User', 'tempUnit'))

# Clears the screen
def forget():
    date_label.place_forget()
    date_line.place_forget()
    time_label.place_forget()
    time_line.place_forget()
    status.place_forget()
    gps_sensor_line.place_forget()
    gps_sensor.place_forget()
    ambient_line.place_forget()
    ambient.place_forget()
    air_line.place_forget()
    air.place_forget()
    temp1_line.place_forget()
    temp1.place_forget()
    temp2_line.place_forget()
    temp2.place_forget()
    press_line.place_forget()
    press.place_forget()
    current_line.place_forget()
    current.place_forget()
    usb_status.place_forget()
    start.place_forget()
    stop.place_forget()
    conf.place_forget()
    eject.place_forget()
    graphs.place_forget()
    end.place_forget()
    dropMenu.place_forget()
    config_label.place_forget()

    ambient_graph.place_forget()
    voc_graph.place_forget()
    temp1_graph.place_forget()
    temp2_graph.place_forget()
    press_graph.place_forget()
    current_graph.place_forget()
    back.place_forget()
    graph_title_label.place_forget()
    graph.clear()
    graph_canvas.get_tk_widget().place_forget()

# Places all the graph items
def graphGUI():
    forget()
    canvas.create_rectangle(0,0,800,600,fill="slate gray")
    ambient_graph.place(x=20, y=50)
    voc_graph.place(x=20, y=105)
    temp1_graph.place(x=20, y=160)
    temp2_graph.place(x=20, y=215)
    press_graph.place(x=20, y=270)
    current_graph.place(x=20, y=325)
    back.place(x=20, y=380)
    graph_title_label.place(x=380, y=10)
    # change to graph phase

# Places all Main screen items
def initMain():
    forget()
    canvas.create_rectangle(15,25, 350, 115, fill="grey16")
    canvas.create_rectangle(365,25, 785, 450, fill="grey16")

    date_label.place(x=40, y=40)
    date_line.place(x=110, y=40)
    time_label.place(x=40, y=70)
    time_line.place(x=110, y=70)

    status.place(x=380, y=40)
    gps_sensor_line.place(x=380, y=90)
    gps_sensor.place(x=445, y=90)
    ambient_line.place(x=380, y=130)
    ambient.place(x=490, y=130)
    air_line.place(x=380, y=170)
    air.place(x=515, y=170)
    temp1_line.place(x=380, y=210)
    temp1.place(x=490, y=210)
    temp2_line.place(x=380, y=250)
    temp2.place(x=490, y=250)
    press_line.place(x=380, y=290)
    press.place(x=490, y=290)
    current_line.place(x=380, y=330)
    current.place(x=490, y=330)
    usb_status.place(x=380, y=410)

    start.place(x=35, y=150)
    stop.place(x=195, y=150)
    conf.place(x=35, y=240)
    graphs.place(x=195, y=240)
    eject.place(x=35, y=330)
    end.place(x=195, y=330)

# Closes the app
def close():
    order.put("end")

def takeData():
    # try to create a CSV file in this location, if there is an error, then nothing happens
    try:
        # Create a CSV file called test, then write the headers for each column to it
        ## TODO: make it so that the user can input their own file names and use whatever usb they would like
        with open("/media/pi/LOGGER/test.csv", "w") as log:
            log.write("Time,Date,GPS Location,Ambient Temp (C),Air Quality,Air Quality (Ohm),Temp 1 (C), Temp 2 (C),Pressure (kPa), Current (A)")
            log.close()
        conf.config(state=DISABLED, background = "gray")    # Disables the config button
        order.put("start")  # trigger main loop to start taking data
    except:
        pass
        ## TODO: through an error if the file cannot be created

# Stop taking data
def stopTakingData():
    conf.config(state=NORMAL, background = "deep sky blue") # Reactivate config button
    order.put("stop")   # Stop taking data

# Takes raw GPS data and gets the time, GPS location, and date from it
def formatGPS(data):
    split_data = data.split(",")
    time_data = split_data[1][0:2] + ":" + split_data[1][2:4] + ":" + split_data[1][4:6] + " UTC"
    lat = numbers(split_data[3])
    long = numbers(split_data[5])
    gps_data = lat + " " + split_data[4] + ", " + long + " " +  split_data[6]
    date_data = split_data[9][2:4] + "/" + split_data[9][0:2] + "/" +split_data[9][4:6]
    return time_data,gps_data,date_data

# Used for converting GPS location data
def numbers(coords):
    #converts the numbers for coords into proper format
    x = coords.split(".")
    head = x[0]
    tail = x[1]
    deg = head[0:-2]
    return deg + "." + tail

# Displays the Ambient temperature graph
def ambientGraph():
    displayGraphs("Ambient Temperature", ambient_array)

# Displays the VOC resistace graph
def airGraph():
    displayGraphs("Air Quality", air_array)

# Displays the Temp1 temperature graph
def temp1Graph():
    displayGraphs("Temperature Sensor 1", temp1_array)

# Displays the Temp2 temperature graph
def temp2Graph():
    displayGraphs("Temperature Sensor 2", temp2_array)

# Displays the Current measurement graph
def currentGraph():
    displayGraphs("Current Sensor", current_array)

# Displays the Pressure measurement graph
def pressureGraph():
    displayGraphs("Pressure Sensor", pressure_array)

# Sets the values for the different graphs then displays them 
def displayGraphs(title, array):
    graph.clear()  
    temp = []
    for i in range(len(array)):
        temp.append(len(array) - i)              
    graph.add_subplot(111).plot(temp,array)
    graph_canvas.get_tk_widget().place(x=135, y=50)
    graph_canvas.draw()
    graph_title_label.config(text=title)
    
# Unmounts USB for safe removal
# This function DOES NOT WORK, an error is thrown saying that unmount doesn't exist
def ejectUSB():
    os.system('sudo unmount /media/pi/LOGGER')


# GUI VARIABLE DECLARATIONS---------------------------------------------------------

# Tkinter canvas set up
root = Tk()
width = 800
height = 480
root.title("Furnace Logger Control")
root.attributes('-fullscreen', True)    # Makes window full screen so that the status and start bars are not visible
canvas = Canvas(root, width=width, height=height, background="slate gray")
canvas.pack()

# Common colors used in the GUI
red = "red3"
green = "green3"
orange = "DarkOrange1"

# GRAPH SCREEN DECLARATIONS
ambient_graph = Button(root, font=("Arial", 16), text="Ambient", width=7, height=1, background="deep sky blue", command=ambientGraph)
voc_graph = Button(root, font=("Arial", 16), text="VOC", width=7, height=1, background="deep sky blue", command=airGraph)
temp1_graph = Button(root, font=("Arial", 16), text="Temp 1", width=7, height=1, background="deep sky blue", command=temp1Graph)
temp2_graph = Button(root, font=("Arial", 16), text="Temp 2", width=7, height=1, background="deep sky blue", command=temp2Graph)
press_graph = Button(root, font=("Arial", 16), text="Pressure", width=7, height=1, background="deep sky blue", command=pressureGraph)
current_graph = Button(root, font=("Arial", 16), text="Current", width=7, height=1, background="deep sky blue", command=currentGraph)
back = Button(root, font=("Arial", 16), text="Back", width=7, height=1, background="red3", command=initMain)
graph_title_label = Label(root, bg="slate gray", font=("Arial", 18, "bold"), fg="White")
graph = Figure(figsize=(8, 5), dpi=80)
graph_canvas = FigureCanvasTkAgg(graph, master=root)
plt.locator_params(axis='x', nbin=5)

# CONFIG OPTION SETUP
tkvar = StringVar(root)
choices = {'Fahrenheit', 'Celsius'}
tkvar.set('Celsius')
tkvar.trace('w', config)
dropMenu = OptionMenu(canvas, tkvar, *choices, command = config)
config_label = Label(root, bg='slate grey', font = ("Arial", 16), fg = 'deep sky blue', text='Temperature display unit')
prevChoice = 0
choice = 0

# MAIN SCREEN ITEMS
# Date and time
date_label = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Date:")
date_line = Label(root, bg="grey16", font=("Arial", 16), fg=green)
time_label = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Time:")
time_line = Label(root, bg="grey16", font=("Arial", 16), fg=green)

# Status Box
status = Label(root, bg="grey16", font=("Arial", 20, "underline"), fg="deep sky blue", text="Sensor Status")
gps_sensor_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="GPS:")
gps_sensor = Label(root, bg="grey16", font=("Arial", 16), fg=green)
ambient_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Ambient:")
ambient = Label(root, bg="grey16", font=("Arial", 16), fg=red)
air_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="VOC Levels:")
air = Label(root, bg="grey16", font=("Arial", 16), fg=red)
temp1_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Temp 1:")
temp1 = Label(root, bg="grey16", font=("Arial", 16), fg=red)
temp2_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Temp 2:")
temp2 = Label(root, bg="grey16", font=("Arial", 16), fg=red)
press_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Pressure:")
press = Label(root, bg="grey16", font=("Arial", 16), fg=red)
current_line = Label(root, bg="grey16", font=("Arial", 16), fg="deep sky blue", text="Current:")
current = Label(root, bg="grey16", font=("Arial", 16), fg=red)

data_status = Label(root, bg="grey16", font=("Arial", 16), fg=green, text="Collecting Data")
usb_status = Label(root, bg="grey16", font=("Arial", 16))

# Main buttons
start = Button(root, font=("Arial", 18), text="Start", width=8, height=2, background="green3", command=takeData)
stop = Button(root, font=("Arial", 18), text="Stop", width=8, height=2, background="red3", command=stopTakingData)
conf = Button(root, font=("Arial", 18), text="Config", width=8, height=2, background="deep sky blue", command=showConfig)
graphs = Button(root, font=("Arial", 18), text="Graphs", width=8, height=2, background="deep sky blue", command=graphGUI)
eject = Button(root, font=("Arial", 18), text="Eject USB", width=8, height=2, background="deep sky blue", command=ejectUSB)
end = Button(root, font=("Arial", 18), text="Shutdown", width=8, height=2, background=orange, command=close)


# BEGIN-------------------------------------------------------------------------------


# INTERRUPT PIN SETUP
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.IN, pull_up_down = GPIO.PUD_UP) # Sets GPIO pin 19 to be an active high input
GPIO.add_event_detect(19, GPIO.BOTH, callback = screenOnOff) # Sets the GPIO pin 19 interrupt to trigger on either rise or fall

# Reads from the logger.ini file to get the configuration parameters and sets the corresponding variables
configOp = configparser.ConfigParser()
configOp.read('logger.ini')
choice = configOp.get('User', 'tempUnit')   # Temperature units is the only config setting

# sets up the temperature sensors
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')

initMain()  # Display the tkinter elements needed for the main screen

# Default text fo the sensor data labels
ambient.config(text="Not Connected")
air.config(text="Not Connected")
temp1.config(text="Not Connected")
temp2.config(text="Not Connected")
press.config(text="Not Connected")
current.config(text="Not Connected")

# Flags for determining which state the GUI is in
go = True       # Main loop flag
gpsWait = True  # Inital state flag (waits for GPS and BME680 to connect)
idle = True     # Idle loop flag
run = False     # Controls when the program takes data

# Queue is used for transitioning between the different states of the program
order = Queue(maxsize=10)
order.put("connect")

# Connect to the GPS sensor
try:
    gps_com = serial.Serial(
                port = '/dev/ttyS0',
                baudrate = 115200,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                bytesize = serial.EIGHTBITS,
                timeout =1
                )
    gps_com.write(b'$PMTK253,0*2A<CR><LF>')     #configures the gps to output in NMEA format
except:
    gps_com = ""

# Connects tothe BME680 environmental sensor
try:
   bme_com = bme680.BME680(bme680.I2C_ADDR_SECONDARY)     #based on addresses saved in bme680 package
   bme_com.set_humidity_oversample(bme680.OS_2X)
   bme_com.set_pressure_oversample(bme680.OS_1X)
   bme_com.set_temperature_oversample(bme680.OS_1X)
   bme_com.set_filter(bme680.FILTER_SIZE_3)

   bme_com.set_gas_status(bme680.ENABLE_GAS_MEAS)
   bme_com.set_gas_heater_temperature(320)
   bme_com.set_gas_heater_duration(150)
   bme_com.select_gas_heater_profile(0)
except IOError:
   bme_com = ""

# Configures the I2C channels for the current and pressure sensors
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1015(i2c)
    chan0 = AnalogIn(ads, ADS.P0) # Current sensor
    chan1 = AnalogIn(ads, ADS.P1) # PRessure sensor
except:
    chan0 = ""
    chan1 = ""

samples = 60 # number of samples that will be saved and displayed for on the graphs

# arrays for storing the grpah data
time_array = []
ambient_array = []
air_array = []
temp1_array = []
temp2_array = []
current_array = []
pressure_array = []

# MAIN LOOP--------------------------------------------------------------------------------
while go:
    root.update()   # display GUI

    # Connect state, wait for GPS to connect
    while gpsWait:
        # Try to get data from GPS and BME680, if there is data, go to the idle state, if not keep trying
        try:
            if (gps_com.readline() is not None):
                try:
                    if(bme_com.get_sensor_data() and bme_com.data.heat_stable):
                        gpsWait = False
                        idle = True
                except:
                    gpsWait = False
                    idle = True
        except:
            pass

        #check for button, in case shutdown was pressed
        if(not order.empty()):
            next = order.get()
            if(next == "end"):  # Shutdown button was pressed, end loop
                go = False
                idle = False
                run = False    

        ## TODO: add a cutoff time, if the GPS or BME680 fails to connect after a certain period of time, diplay an error

    # Idle state. Contunually takes data from the sensors once a second.
    # This is the default state of the program.
    # If a sensor fails to read, the label that is supposed to diplay it's data will read "Not Connected"
    while idle:        
        # these variables store all the data needed to write to the CSV file
        time_text = gps_text = date_text = ambRead = vocRes = vocWords = ""
        color = temp1_text = temp2_text = pres_text = curr_text = ""

        read_gps = gps_com.readline().decode("utf-8") #gps outputs in binary, this converts into utf-8 for easy conversions
        
        # Checks to see if a USB drive called LOGGER is connected
        if(os.path.exists("/media/pi/LOGGER")):
            usb_status.config(fg=green, text="USB Connected")
            start.config(state=NORMAL)
        else:
            usb_status.config(fg=red, text="No USB")
            start.config(state=DISABLED)

        # when the GPS has the phrase $GNRMC as the first word, then update the screen. This phrase occurs every second
        # If the GPS sensor is on and has no signal, it will return a value when readline() is called, however most of the characters will be null except for the first word, so the system will keep updating data, but the GPS data will not show up.
        if(read_gps[0:6] == "$GNRMC"):  #update time and location and date
            try:
                #print(read_gps) # This line is for debugging purposes
                time_text,gps_text,date_text= formatGPS(read_gps)
                time_line.config(fg=green,text=time_text)
                gps_sensor.config(fg=green,text=gps_text)
                date_line.config(fg=green,text=date_text)
            except:
                time_text = datetime.now().strftime("%H:%M:%S") # if the GPS sensor has no signal, get the system time from the pi (this is mainly used for time stamping the graphs and the CSV files)
                time_line.config(fg=red,text=time_text)
                gps_sensor.config(fg=red,text="No Signal")
                date_line.config(fg=red,text="No Signal")

            # updates time array, used as x axis on all graphs on graph screen
            # THIS IS CURRENTLY UNUSED because all the times that are stored in the array are diplayed on the bottom of the graph and makes it unreadable
            time_array.append(time_text)
            if(len(time_array) >= samples):
                time_array.pop(0)
                
            root.update()

            # Read from the bme680, if the sensor cannot be read, display "No connection"
            try:
                # if the data is stable and there is data to get
                if bme_com.data.heat_stable and bme_com.get_sensor_data():
                    ambRead = bme_com.data.temperature

                    # Display in Celsius or Fahrenheit, depending on the configs setting
                    if (choice == "Celsius"):
                        ambient.config(fg=green,text=str(ambRead) + " C")
                    else:
                        ambRead = round(1.8 * ambRead + 32, 4)
                        ambient.config(fg=green,text=str(ambRead) + " F")                    
                    
                    # updates data for the graphs
                    ambient_array.append(ambRead)   
                    if (len(ambient_array) >= samples):
                        ambient_array.pop(0)

                    # The Air quality is based on a resistance range, the higher the resistance, the better the quality, the lower the VOCs are    
                    vocRes = bme_com.data.gas_resistance                        
                    if vocRes > 364478:
                        vocWords = "Great"
                        color = green
                    elif vocRes > 181094.5 and vocRes <= 364478:
                        vocWords = "Good"
                        color = green
                    elif vocRes > 91526 and vocRes <= 181094.5:
                        vocWords = "OKAY"
                        color = green
                    elif vocRes > 45990.5 and vocRes <= 91526:
                        vocWords = "Poor"
                        color = orange
                    elif vocRes > 22920.5 and vocRes <= 45990.5:
                        vocWords = "Bad"
                        color = orange
                    elif vocRes > 11299.5 and vocRes <= 22920.5:
                        vocWords = "Very Bad"
                        color = red
                    elif vocRes <= 11299.5:
                        vocWords = "Critical"
                        color = red
                    
                    air.config(fg=color,text=vocWords)

                    # updates data for the voc graph
                    air_array.append(vocRes)
                    if(len(air_array) >= samples):
                        air_array.pop(0)

            except:
                ambient.config(fg=red, text="Not Connected")
                air.config(fg=red, text="Not Connected")

            root.update()

            # Temp1 sensor
            try:
                sensor = "/sys/devices/w1_bus_master1/28-00000a9a03f4/w1_slave"
                f = open(sensor, "r")
                data = f.read()
                f.close()
                if "YES" in data:
                    (discard, sep, reading) = data.partition(' t=')
                    temp1_text = float(reading) / 1000.0  # temperature in degrees C

                    # Display in Celsius or Fahrenheit, depending on the configs setting
                    if (choice == "Celsius"):
                        temp1.config(fg=green, text=str(temp1_text) + " C")
                    else:
                        temp1_text = round(1.8 * temp1_text + 32, 4)
                        temp1.config(fg=green, text=str(temp1_text) + " F")

                    # updates data for the temp1 graph
                    temp1_array.append(temp1_text)
                    if (len(temp1_array) >= samples):
                        temp1_array.pop(0)
            except:
                temp1.config(fg=red, text="Not Connected")

            root.update()

            # Temp2 sensor
            try:
                sensor = "/sys/devices/w1_bus_master1/28-00000ab2fd81/w1_slave"
                f = open(sensor, "r")
                data = f.read()
                f.close()
                if "YES" in data:
                    (discard, sep, reading) = data.partition(' t=')
                    temp2_text = float(reading) / 1000.0  # temperature in degrees C

                    # Display in Celsius or Fahrenheit, depending on the configs setting
                    if (choice == "Celsius"):
                        temp2.config(fg=green, text=str(temp2_text) + " C")
                    else:
                        temp2_text = round(1.8 * temp2_text + 32, 4)
                        temp2.config(fg=green, text=str(temp2_text) + " F")

                    # updates data for the temp2 graph
                    temp2_array.append(temp2_text)
                    if(len(temp2_array) >= samples):
                        temp2_array.pop(0)
            except:
                temp2.config(fg=red, text="Not Connected")

            root.update()

            # current sensor
            try:
                curr_text = round(((chan0.voltage/.707)*30)*.826, 4) # Converts RMS value to Current measurement, then multiplies the calibration factor
                current.config(fg=green,text=str(curr_text) + " A")

                # updates data for the current graph
                current_array.append(curr_text)
                if(len(current_array) >= samples):
                    current_array.pop(0)
            except:
                current.config(fg=red,text="Not Connected")

            root.update()

            # pressure sensor
            try:
                error_factor = .25 #volt error (+-6.25%Vfss (3.5-4.5 volts))
                vpress = chan1.voltage + error_factor
                pres_text = round(((vpress-2.5) - .418) * 1.5, 4) # This includes our calibration factor 
                press.config(fg=green, text=str(pres_text) + " kPa")
                
                # updates data for the pressure graph
                pressure_array.append(pres_text)
                if (len(pressure_array) >= samples):
                    pressure_array.pop(0)

            except:
                press.config(fg=red, text="Not Connected")

            root.update()

            # Takes data and writes it to CSV file
            if run:
                with open("/media/pi/LOGGER/test.csv", "a") as log:
                    log.write("\n" + str(date_text) + "," + str(time_text) + "," + str(gps_text) + "," + str(ambRead) + "," + str(vocRes) + "," + str(vocWords) + "," + str(temp1_text) + "," + str(temp2_text) + "," + str(pres_text) + "," + str(curr_text))
                    log.close()


        # check queue
        if not order.empty():
            next = order.get()
            
            # Shutdown button was pressed, end loop
            if(next == "end"): 
                go = False
                idle = False
                run = False
            
            # Stop recording Data
            elif(next == "stop"): 
                data_status.place_forget()
                run = False

            # start recording data
            elif(next == "start"): 
                data_status.place(x=380, y=370)
                run = True            

        root.update()

# Closes GPS communication
gps_com.close()
# Closes the GUI
root.destroy()
