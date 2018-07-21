import tkinter as tk
import numpy as np
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler
import json
import serial
import traceback

# Setup logger
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
FORMAT = logging.Formatter('%(asctime)-15s - %(levelname)s -  %(message)s')
fh = logging.FileHandler(filename='log.log')
fh.setFormatter(FORMAT)
fh.setLevel(logging.INFO)
sh = logging.StreamHandler()
sh.setFormatter(FORMAT)
sh.setLevel(logging.DEBUG)
logger.addHandler(fh)
logger.addHandler(sh)

######################################################
################# PARAMETERS #########################
sampleRate = 200  # Sampling rate in Hz
guiRate = 0.3 # Number of seconds between gui updates
tempLogRate = 10  # Number of seconds between temperature logs
depthLogRate = 0.5 # Number of seconds between depth logs

tempThreshold = 100  # Threshold for temperature to throw fault
voltThreshold = 0.1  # Threshold for voltage difference to throw fault
depthThreshold = 100 # Threshold for depth (meters)

splitTime = 1 # Number of seconds between trips to log

# Logging file parameters
tempLog = 'temp.csv'
tempFaultLog = 'tempFault.csv'
voltFaultLog = 'voltFault.csv'
depthLog = 'depth.csv'

# ARDUINO SERIAL PORT
arduinoSerialPort = '/dev/ttyACM0'
######################################################
######################################################


# Setup arduino serial
try:
    ser = serial.Serial(arduinoSerialPort, 9600, timeout=0.01)
except:
    logger.fatal('Could not find arduino')
    logger.fatal(traceback.print_exc())

# Define function to randomly generate a number to emulate voltage readings
def getValues():
    # positive 12, negative 12, temp, depth
    
    # Read datafrom arduino
    try:
        ser.write('data'.encode('ascii', 'ignore')) # Tell the arduino to send data
        dataIn = str(ser.readline().decode('ascii')) # get the data from the arduino
        #logger.debug(dataIn)
    except:
        logger.warning('Could not get data first try')
        logger.warning(traceback.print_exc())
        try:
            ser.write('data')
            dataIn = str(ser.readline().decode('ascii'))
        except:
            logger.fatal('Could not get data second try')
            
    try:
        logger.debug("before: " + dataIn)
        dataIn = dataIn.replace('$', '"')
        logger.debug("after: " + dataIn)
        dataJSON = json.loads(str(dataIn))
        logger.debug(dataJSON)
    except:
        dataJSON = json.loads('{"temp":"0.0", "depth":"0.0", "n12":"0.0", "p12":"0.0"}')
        logger.warning("Didn't load JSON")
        logger.warning(traceback.print_exc())
    
    positive12 = dataJSON['p12']
    negative12 = dataJSON['n12']
    temp = dataJSON['temp']
    depth = dataJSON['depth']
    
    return positive12, negative12, temp, depth


#####################################################
################ TEMPRATURE LOG #####################
# Setup scheduler to log temperature values
s = BackgroundScheduler(coalescing=True, misfire_grace_time=5, max_instances=1, timezone='America/New_York')
s.start()

# Define function to log temperature
global newTemp
newTemp = 0
def logTemp():
    global newTemp
    with open(tempLog, 'a') as f:
        f.write('\n' + str(time.time()) + ',' + str(newTemp))

# Setup ten second timer to log temperature
s.add_job(logTemp, 'interval', seconds=tempLogRate, id='tempLog')
logger.info('Setup job for temperature logging')

######################################################
######################################################


#####################################################
################ DEPTH LOG #####################
# Define function to log depth
global depth
depth = 0
def logDepth():
    global depth
    with open(depthLog, 'a') as f:
        f.write('\n' + str(time.time()) + ',' + str(depth))

# Setup ten second timer to log temperature
s.add_job(logDepth, 'interval', seconds=depthLogRate, id='depthLog')
logger.info('Setup job for depth logging')

######################################################
######################################################


# Define tkinter objects
N = tk.N
S = tk.S
E = tk.E
W = tk.W

# Set global flags and timers for voltage fault and temperature fault
global voltFault
global tempFault
global voltTimer
global tempTimer
global guiTimer

voltFault = 0
tempFault = 0
voltTimer = 0
tempTimer = 0
guiTimer = 0

# Define function to reset the fault counts
def refresh():
	global tempFault
	global voltFault

	logger.info('Faults refreshed')

	tempFault = 0
	voltFault = 0

	tempF.config(bg='green', text='Temp Good')
	voltF.config(bg='green', text='Voltage Good')
	

# Setup a root window to show the monitor in
root = tk.Tk()
root.geometry('480x320') # Set the size of the window
root.resizable(width=False, height=False) # Set the window size to be fixed
root.title('Monitor') # Set a title for the window

# Setup the elements in the GUI
v = tk.Label(root, text='Voltage: ', font="Times 35 bold", padx=10, pady=10)
v.grid(row=0, column=0, sticky=N+S+E+W)
voltageP = tk.Label(root, text='0', font="Times 20") # Positive voltage
voltageP.grid(row=0, column=1, sticky=N+S+E+W)
voltageN = tk.Label(root, text='0', font="Times 20") # Negative voltage
voltageN.grid(row=0, column=2, sticky=N+S+E+W)
voltF = tk.Label(root, text='Voltage Good', font='Times 20', padx=10, pady=40, bg='green')
voltF.grid(row=3, column=0, sticky=N+S+E+W)

t = tk.Label(root, text='Temp (F): ', font="Times 35 bold", padx=10, pady=10)
t.grid(row=1, column=0, sticky=N+S+E+W)
temp = tk.Label(root, text='0', font="Times 20")
temp.grid(row=1, column=1, sticky=N+S+E+W, columnspan=2)
tempF = tk.Label(root, text='Temp Good  ', font='Times 20', padx=10, pady=40, bg='green')
tempF.grid(row=3, column=1, sticky=N+S+E+W)

d = tk.Label(root, text='Depth (m): ', font="Times 35 bold", padx=10, pady=10)
d.grid(row=2, column=0, sticky=N+S+E+W)
depthLabel = tk.Label(root, text='0', font="Times 20")
depthLabel.grid(row=2, column=1, sticky=N+S+E+W, columnspan=2)

refresh = tk.Button(root, text='Reset', font="Times 15", padx=10, pady=40, command=refresh)
refresh.grid(row=3, column=2, sticky=N+S+E+W)

logger.info('GUI frame setup')

# Define function to update GUI
def updateGUI():
	# Grab global variables
    global tempFault, tempTimer
    global voltFault, voltTimer
    global guiTimer
    global newTemp
    global depth

	# Read new sensor values
    p12, n12, newTemp, depth = getValues()
	
	# Update the GUI at the set rate
    if((time.time() - guiTimer) > guiRate):  
        voltageP.config(text=p12) # Update the positive voltage
        voltageN.config(text=n12) # Update the negative voltage
        temp.config(text=newTemp) # Update the temp
        depthLabel.config(text=depth) # Update the depth
        guiTimer = time.time()

	# Check for faults
    faultFlag = False
    if(float(newTemp) > tempThreshold):
        faultFlag = True
        temp.config(bg='red')
		
        if((time.time() - tempTimer) > splitTime):
            logger.warning('TEMP FAULT #' + str(tempFault))
            tempTimer = time.time()
            tempFault = tempFault + 1
            tempF.config(bg='red', text='Temp Fault x'+str(tempFault))
    else:
        temp.config(bg='white')
        
    if(float(depth) > depthThreshold):
        logger.warning('DEPTH FAULT')
        depthLabel.config(bg='red')
    else:
        depthLabel.config(bg='white')
    
    if(abs(float(p12) - 12) > voltThreshold):
        faultFlag = True
        voltageP.config(bg='red')
		
        if((time.time() - voltTimer) > splitTime):
            logger.warning('VOLT FAULT #' + str(voltFault))
            voltTimer = time.time()
            voltFault = voltFault + 1
            voltF.config(bg='red', text='Voltage Fault x'+str(voltFault))
    else:
        voltageP.config(bg='white')
        
    if(abs(float(n12) - 12) > voltThreshold):
        faultFlag = True
        voltageN.config(bg='red')
		
        if((time.time() - voltTimer) > splitTime):
            logger.warning('VOLT FAULT #' + str(voltFault))
            voltTimer = time.time()
            voltFault = voltFault + 1
            voltF.config(bg='red', text='Voltage Fault x'+str(voltFault))
    else:
        voltageN.config(bg='white')
	
    root.update()
	
    root.after(int(1000/int(sampleRate)), updateGUI) # Set to update itself

# Update for the first time
updateGUI()

# Run the GUI
root.mainloop()
