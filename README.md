# Required Packages
### Apscheduler
 *sudo pip3 install apscheduler*

### Tkinter
  *sudo apt-get install python3-tk*
  
### Numpy
  *sudo pip3 install numpy*

# Overview
This will run a simple monitor which looks at two values, temperature and voltage.  Each one has a threshold which can be set by the user, and also a sample rate set by the user.  The script will then check these values at the sampling rate.  If either goes outside the set threshold, a fault is logged and shown on the GUI.  A count of the number of faults is shown on the GUI, as well as the current readings at whatever sampling rate was set.  A short pause is added after a fault is caught so that it doesn't catch multiple of the same fault with a high sample rate.  Temperature is also logged at a set interval in a CSV file, which can then be graphed or analyzed seperately.  Tkinter is used to create the GUI, and apscheduler is used to run the temperature logging at a certain interval.

### Temperature and Voltage Input
Currently the voltage and temperature are generated as random numbers, but the code in those functions can be changed to actually read the value from a sensor or ADC as is planned.
