#!/usr/bin/python

# python 2
# import Tkinter as tk
# from tkFont import Font

# run using python 3
# python 3
import tkinter as tk
from tkinter.font import Font
import tk_tools

import os
import time
import serial
import math

import RPi.GPIO as GPIO # To use GPIO pins

from datetime import datetime

# Import the ADS1x15 module.
import Adafruit_ADS1x15

# Create an ADS1115 ADC (16-bit) instance.
adc = Adafruit_ADS1x15.ADS1115()

# See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
GAIN = 1
mq135_raw = 500 # initialize value

import Adafruit_DHT
# set variables to valid numbers
tF=75
tC=21
humid=50
concPM1_0_ATM=30

rawGt0_3um = 10000
rawGt0_5um = 3000
rawGt1_0um = 1000
rawGt2_5um = 100
rawGt5_0um = 50
rawGt10_0um = 2

concPM1_0_ATM = 50
concPM2_5_ATM = 100
concPM10_0_ATM = 450

# Sensor should be set to Adafruit_DHT.DHT11,
# Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
dht22_sensor1 = Adafruit_DHT.DHT22
dht22_sensor1_pin = 21

dht22_sensor2 = Adafruit_DHT.DHT22
dht22_sensor2_pin = 20

# initialize all the sensor arrays
DHT22_sensors = [dht22_sensor1, dht22_sensor2]
DHT22_pins = [dht22_sensor1_pin, dht22_sensor2_pin]
tempF = [0,0]
tempC = [0,0]
humid = [0,0]
outsideTemp = 0

global end_seconds
global start_seconds
end_seconds = int(0)
start_seconds = int(0)

# data logging file: /home/pi/projects/data_log.csv
data_file = "/home/pi/projects/data_log.csv"

physicalPort = '/dev/ttyS0' # for the serial sensor (PMS7003)
serialPort = serial.Serial(physicalPort)  # open serial port

# For optional LED
GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)
GPIO.output(40, GPIO.LOW)

win = tk.Tk()
win.geometry('800x600')


particle_label_Font = Font(family="Ariel", size=12)
particle_data_Font = Font(family="Ariel", size=16)
tempurature_Font = Font(family="Ariel", size=82)
tempurature_label_Font = Font(family="Ariel", size=32)
mq135Font = Font(family="Ariel", size=56)
mq135_label_Font = Font(family="Ariel", size=16)
myFont1 = Font(family="Times New Roman", size=14)
myFont2 = Font(family="Ariel", size=14)
myFont3 = Font(family="Ariel", size=18)

win.title("PMS7003 Sensor")
win.config(bg="black")

bar_PM1_width = concPM1_0_ATM
bar_PM1_height = 25
bar_PM1 = tk.Canvas(win, width=bar_PM1_width, height=bar_PM1_height, bg= 'green')
bar_PM1.grid(row=1, column=1, columnspan=5, sticky=tk.NW)

bar_PM2_5_width = concPM2_5_ATM
bar_PM2_5_height = 25
bar_PM2_5 = tk.Canvas(win, width=bar_PM2_5_width, height=bar_PM2_5_height, bg= 'yellow')
bar_PM2_5.grid(row=2, column=1, columnspan=5, sticky=tk.NW)

bar_PM10_0_width = concPM10_0_ATM
bar_PM10_0_height = 25
bar_PM10_0 = tk.Canvas(win, width=bar_PM10_0_width, height=bar_PM10_0_height, bg= 'red')
bar_PM10_0.grid(row=3, column=1,  columnspan=5, sticky=tk.NW)

# fix total grid to be 750 px wide
bar_750_width = 700
bar_750_height = 1
bar_750 = tk.Canvas(win, width=bar_750_width, height=bar_750_height, bg='red')
bar_750.grid(row=0, column=0, columnspan=6, sticky=tk.N)

particleCount_1_0_label = tk.Label (win, text=" 1.0 um: ", fg="white", bg="black", font=particle_label_Font)
particleCount_1_0_label.grid(row=1,column=0,  sticky=tk.W)
particleCount_2_5_label = tk.Label (win, text=" 2.5 um: ", fg="white", bg="black", font=particle_label_Font)
particleCount_2_5_label.grid(row=2,column=0,  sticky=tk.W)
particleCount_10_0_label = tk.Label (win, text=" 10.0 um: ", fg="white", bg="black", font=particle_label_Font)
particleCount_10_0_label.grid(row=3,column=0,  sticky=tk.W)

particleCount_1_0_data = tk.Label (win, text=str(concPM1_0_ATM), fg="white", bg="black", font=particle_data_Font)
particleCount_1_0_data.grid(row=1,column=0,  sticky=tk.E)
particleCount_2_5_data = tk.Label (win, text=str(concPM2_5_ATM), fg="white", bg="black", font=particle_data_Font)
particleCount_2_5_data.grid(row=2,column=0,  sticky=tk.E)
particleCount_10_0_data = tk.Label (win, text=str(concPM10_0_ATM), fg="white", bg="black", font=particle_data_Font)
particleCount_10_0_data.grid(row=3,column=0,  sticky=tk.E)

gases_data = tk.Label(win, text=str(mq135_raw), fg="gold3", bg="black", font=mq135Font)
gases_data.grid(row=4, column=0, sticky=tk.E)
gases_label = tk.Label(win, text='NOx/COx', fg="gold3", bg="black", font=mq135_label_Font)
gases_label.grid(row=4, column=1, sticky=tk.W)

temp_data = tk.Label(win, text=str(tempF[0]), fg="thistle2", bg="black", font=tempurature_Font)
temp_data.grid(row=4, column=2, sticky=tk.E)
temp_label = tk.Label(win, text='F', fg="thistle2", bg="black", font=tempurature_label_Font)
temp_label.grid(row=4, column=3, sticky=tk.W)

humid_data = tk.Label(win, text=str(humid[0]), fg="dodger blue", bg="black", font=tempurature_Font)
humid_data.grid(row=4, column=4, sticky=tk.E)
humid_label = tk.Label(win, text='%', fg="dodger blue", bg="black", font=tempurature_label_Font)
humid_label.grid(row=4, column=5, sticky=tk.W)

status_label = tk.Label(win, text="Status messages...", fg="white", bg="black", font=myFont1)
status_label.grid(row=7,column=0, sticky=tk.NW)

outTemp_label = tk.Label(win, text="Outdoors:", fg="magenta", bg="black", font=myFont1)
outTemp_label.grid(row=8,column=1, sticky=tk.E)
outTemp_data = tk.Label(win, text="999", fg="magenta", bg="black", font=tempurature_Font)
outTemp_data.grid(row=8,column=2, sticky=tk.NE)
outTemp_label2 = tk.Label(win, text='F', fg="magenta", bg="black", font=tempurature_label_Font)
outTemp_label2.grid(row=8,column=3, sticky=tk.W)

# Read MCP3008 data
def getAnalogInput():
    # Read all the ADC channel values in a list.
    values = [0]*4
    for i in range(4):
        # Read the specified ADC channel using the previously set gain value.
        values[i] = adc.read_adc(i, gain=GAIN)
    # Print the ADC values.
    # print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
    return(values[0]) # just return the active sensors' value


def getDHT22():
        print("Check DHT22 Temp/Hum")
        # Try to grab a sensor reading.  Use the read_retry method which will retry up
        # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
        i=0
        for sensor in DHT22_sensors:
            humidity, tC = Adafruit_DHT.read_retry(sensor, DHT22_pins[i])
            # convert Celsius to F
            tF = ((tC*9)/5) + 32

            # Note that sometimes you won't get a reading and
            # the results will be null (because Linux can't
            # guarantee the timing of calls to read the sensor).
            # If this happens try again!
            currentsensor = str(i)
            print('Sensor ',currentsensor,' has been read')
            if humidity is not None and tempC is not None:
                print('Temp ={0:0.1f}*F {1:0.1f}*C'.format(tF, tC))
                print('Humidity={:3.0f}%'.format(humidity))
                tempF[i] = tF
                tempC[i] = tC
                humid[i] = humidity
            else:
                print('Failed to get reading. Try again!')
                tempF[i] = 0
                tempC[i] = 0
                humid[i] = 0
            i=i+1
        return (tempF, tempC, humid)


def ledON():
        print("LED button pressed")
        checkSerialSensor()
        if GPIO.input(40) :
                GPIO.output(40,GPIO.LOW)
                ledButton["text"] = "LED ON"
        else:
                GPIO.output(40,GPIO.HIGH)
                ledButton["text"] = "LED OFF"

def serialOn():
        print("Serial Comm Button pressed")
        checkSerialSensor()

def logData(dataArr):
        status_label.config(text="Logging data to "+data_file)
        print("Logging data to "+data_file)
        nowTime = time.strftime('%Y-%m-%d _ %H:%M:%S')
        file = open(data_file, "a")
        if os.stat(data_file).st_size == 0:
            file.write("Time::concPM1_0_CF1::concPM2_5_CF1::concPM10_0_CF1\n")
        file.write(str(nowTime)+"::"+str(dataArr[0])+"::"+str(dataArr[1])+"::"+str(dataArr[2])+"\n")
        file.flush()
        file.close()

def exitProgram():
        print("Exit Button pressed")
        GPIO.cleanup()
        win.quit()
        win.destroy()

def checkSerialSensor():
    # Check if we have enough data to read a payload
    # print("Checking PMS7003 Sensor")
    status_label.config(text="Checking PMS7003 Sensor...")
    global start_seconds
    global end_seconds
    # print("initialize start_seconds in beginning of checkSerialSensor")
    ms = time.time()
    start_seconds = int(ms)

    if serialPort.in_waiting >= 32:
        # Check that we are reading the payload from the correct place (i.e. the start bits)
        if ord(serialPort.read()) == 0x42 and ord(serialPort.read()) == 0x4d:
            # print("Reading the payload")
            status_label.config(text="Reading the payload")
            # Read the remaining payload data
            data = serialPort.read(30)
            # Extract the byte data by summing the bit shifted high byte with the low byte
            # Use ordinals in python to get the byte value rather than the char value
            frameLength = data[1] + (data[0] << 8)
            # Standard particulate values in ug/m3
            concPM1_0_CF1 = data[3] + (data[2] << 8)
            concPM2_5_CF1 = data[5] + (data[4] << 8)
            concPM10_0_CF1 = data[7] + (data[6] << 8)
            # Atmospheric particulate values in ug/m3
            concPM1_0_ATM = data[9] + (data[8] << 8)
            concPM2_5_ATM = data[11] + (data[10] << 8)
            concPM10_0_ATM = data[13] + (data[12] << 8)
            # Raw counts per 0.1l
            rawGt0_3um = data[15] + (data[14] << 8)
            rawGt0_5um = data[17] + (data[16] << 8)
            rawGt1_0um = data[19] + (data[18] << 8)
            rawGt2_5um = data[21] + (data[20] << 8)
            rawGt5_0um = data[23] + (data[22] << 8)
            rawGt10_0um = data[25] + (data[24] << 8)
            # Misc data
            version = data[26]
            errorCode = data[27]
            payloadChecksum = data[29] + (data[28] << 8)

            # Calculate the payload checksum (not including the payload checksum bytes)
            inputChecksum = 0x42 + 0x4d
            for x in range(0, 27):
                inputChecksum = inputChecksum + data[x]
            # print("PM1 Atmospheric concentration = " + str(concPM1_0_ATM) + " ug/m3")
            # print("PM2.5 Atmospheric concentration = " + str(concPM2_5_ATM) + " ug/m3")
            # print("PM10 Atmospheric concentration = " + str(concPM10_0_ATM) + " ug/m3")

            # print("Version = " + str(version))
            # print("Error Code = " + str(errorCode))
            if(str(errorCode) != 0):
                status_label.config(text="Error Code = " + str(errorCode))
            # print("Frame length = " + str(frameLength))
            # if we have new data, then clear and refresh

            # load and log the data array
            PMSdata = []
            PMSdata = [concPM1_0_CF1,concPM2_5_ATM,concPM10_0_ATM]

            particleCount_1_0_data.config(text=str(concPM1_0_CF1))
            particleCount_2_5_data.config(text=str(concPM2_5_CF1))
            particleCount_10_0_data.config(text=str(concPM10_0_CF1))

            #Set he bar color
            if(concPM1_0_CF1>=250):
                    bar_PM1.config(bg="brown4")
            elif(concPM1_0_CF1>=121):
                    bar_PM1.config(bg="red")
            elif(concPM1_0_CF1>=91):
                    bar_PM1.config(bg="orange3")           
            elif(concPM1_0_CF1>=61):
                    bar_PM1.config(bg="yellow")
            elif(concPM1_0_CF1>=31):
                    bar_PM1.config(bg="lawn green")
            else:
                    bar_PM1.config(bg="green4")

            if(concPM2_5_CF1>=250):
                    bar_PM2_5.config(bg="brown4")
            elif(concPM2_5_CF1>=121):
                    bar_PM2_5.config(bg="red")
            elif(concPM2_5_CF1>=91):
                    bar_PM2_5.config(bg="orange3")           
            elif(concPM2_5_CF1>=61):
                    bar_PM2_5.config(bg="yellow")
            elif(concPM2_5_CF1>=31):
                    bar_PM2_5.config(bg="lawn green")
            else:
                    bar_PM2_5.config(bg="green4")
                    
            if(concPM10_0_CF1>=430):
                    bar_PM10_0.config(bg="brown4")
            elif(concPM10_0_CF1>=351):
                    bar_PM10_0.config(bg="red")
            elif(concPM10_0_CF1>=251):
                    bar_PM10_0.config(bg="orange3")           
            elif(concPM10_0_CF1>=101):
                    bar_PM10_0.config(bg="yellow")
            elif(concPM10_0_CF1>=51):
                    bar_PM10_0.config(bg="lawn green")
            else:
                    bar_PM10_0.config(bg="green4")

            # base height
            bar_PM1.config(height=25)
            bar_PM2_5.config(height=25)
            bar_PM10_0.config(height=25)
            if(concPM1_0_CF1>=500):
                concPM1_0_CF1 = 500
            if(concPM2_5_CF1>=500):
                concPM2_5_CF1 = 500
            if(concPM10_0_CF1>=500):
                concPM10_0_CF1 = 500
            bar_PM1.config(width=concPM1_0_CF1)
            bar_PM2_5.config(width=concPM2_5_CF1)
            bar_PM10_0.config(width=concPM10_0_CF1)
            
            if inputChecksum != payloadChecksum:
                print("Warning! Checksums don't match!")
                print("Calculated Checksum = " + str(inputChecksum))
                print("Payload checksum = " + str(payloadChecksum))
    # time.sleep(0.7)
    # Maximum recommended delay (as per data sheet 700 ms)

    # try to get the temp and humidity every 30 sec
    if(end_seconds==0 or start_seconds-end_seconds >= 30):
        status_label.config(text="Reading DHT")
        print("Reading DHT")
        tempF,tempC,humid = getDHT22()
        # these are all arrays for multiple sensors
        # each array has two elements, inside reading [0] and outside reading [1]
        temp_data.config(text=str(int(tempF[0])))
        humid_data.config(text=str(int(humid[0])))
        outsideTemp = str(int(tempF[1]))
        outTemp_data.config(text=str(int(tempF[1])))
        ms = time.time()
        end_seconds = int(ms) # delay at least 2 seconds before re-polling sensor
        print("Setting end_seconds after reading DHT")
        

    # print("end_seconds: "+str(end_seconds))
    # print("start_seconds: "+str(start_seconds))
    print("start_second-send_seconds = " + str(start_seconds-end_seconds))

    # get the analog sensor(s) data
    mq135_raw = getAnalogInput()
    if(mq135_raw <=500):
        gases_data.config(fg='spring green')
    elif(mq135_raw >=800):
        gases_data.config(fg='red')
    else:
        gases_data.config(fg='yellow')

    gases_data.config(text=str(mq135_raw))
    
    startTime = time.strftime('%Y-%m-%d _ %H:%M:%S')
    status_label.config(text=str(startTime))
    win.after(700, checkSerialSensor)

exitButton  = tk.Button(win, text = "Exit", command = exitProgram, height =2 , width = 6) 
exitButton.grid(row=7,column=1)

serialOn = tk.Button(win, text = "Start", command = checkSerialSensor, height = 2, width =12)
serialOn.grid(row=7,column=2)

win.mainloop()
