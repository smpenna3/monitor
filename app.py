import tkinter as tk
import numpy as np
import time
import logging
from apscheduler.schedulers.background import BackgroundScheduler

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
sampleRate = 5  # Sampling rate in Hz
tempLogRate = 10  # Number of seconds between temperature logs

tempThreshold = 65  # Threshold for temperature to throw fault
voltThreshold = 0.35  # Threshold for voltage difference to throw fault

tempLog = 'temp.csv'
tempFaultLog = 'tempFault.csv'
voltFaultLog = 'voltFault.csv'
######################################################
######################################################


# Define function to randomly generate a number to emulate voltage readings
def readVoltage():
	return '%.3f'%(np.random.normal(12, 0.25))

# Define function to randomly generate a number to emulate temperature readings
def readTemp():
	return '%.3f'%(np.random.normal(60, 4))


#####################################################
################ TEMPRATURE LOG #####################
# Setup scheduler to log temperature values
s = BackgroundScheduler(coalescing=True, misfire_grace_time=5, max_instances=1, timezone='America/New_York')
s.start()

# Define function to log temperature
def logTemp():
	with open(tempLog, 'a') as f:
		f.write('\n' + str(time.time()) + ',' + str(readTemp()))

# Setup ten second timer to log temperature
s.add_job(logTemp, 'interval', seconds=tempLogRate, id='tempLog')

######################################################
######################################################


# Define tkinter objects
N = tk.N
S = tk.S
E = tk.E
W = tk.W

# Set global flags for voltage fault and temperature fault
global voltFault
global tempFault

voltFault = 0
tempFault = 0

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
voltage = tk.Label(root, text=readVoltage(), font="Times 20")
voltage.grid(row=0, column=1, sticky=N+S+E+W, columnspan=2)
voltF = tk.Label(root, text='Voltage Good', font='Times 20', padx=10, pady=40, bg='green')
voltF.grid(row=2, column=0, sticky=N+S+E+W)

t = tk.Label(root, text='Temp (F): ', font="Times 35 bold", padx=10, pady=10)
t.grid(row=1, column=0, sticky=N+S+E+W)
temp = tk.Label(root, text=readTemp(), font="Times 20")
temp.grid(row=1, column=1, sticky=N+S+E+W, columnspan=2)
tempF = tk.Label(root, text='Temp Good  ', font='Times 20', padx=10, pady=40, bg='green')
tempF.grid(row=2, column=1, sticky=N+S+E+W)

refresh = tk.Button(root, text='Reset', font="Times 15", padx=10, pady=40, command=refresh)
refresh.grid(row=2, column=2, sticky=N+S+E+W)

# Define function to update GUI
def updateGUI():
	# Grab global variables
	global tempFault
	global voltFault

	# Read new sensor values
	newVolt = readVoltage()
	newTemp = readTemp()
	
	# Update the GUI
	voltage.config(text=newVolt) # Update the voltage
	temp.config(text=newTemp) # Update the temp

	# Check for faults
	faultFlag = False
	if(float(newTemp) > tempThreshold):
		faultFlag = True
		tempFault = tempFault + 1
		logger.warning('TEMP FAULT #' + str(tempFault))
		temp.config(bg='red')
		tempF.config(bg='red', text='Temp Fault x'+str(tempFault))
	else:
		temp.config(bg='white')

	if(abs(float(newVolt) - 12) > voltThreshold):
		faultFlag = True
		voltFault = voltFault + 1
		logger.warning('VOLT FAULT #' + str(voltFault))
		voltage.config(bg='red')
		voltF.config(bg='red', text='Voltage Fault x'+str(voltFault))
	else:
		voltage.config(bg='white')
	
	root.update()
	
	if(faultFlag):
		time.sleep(1)

	root.after(int(1000/int(sampleRate)), updateGUI) # Set to update itself

# Update for the first time
updateGUI()

# Run the GUI
root.mainloop()
