# DeviceStatusLED
RGB LED notification light for API call to FabApp for device status.

### Installation
To install the program cd into the cloned folder use the bash script setup with
`sh setup`
From here you will be prompted to enter the device number (as stored in the database) and the API key (also in the DB).
Additionally, it will install needed dependencies (ie *Python3-pip package control* and *RPi.GPIO* to control GPIO pins).
Following this, the setup script will create, enable, and start the service for Device Status.  From this point on reboot and start up the python script will run automatically.  

### How it works
	#####API
	DeviceStatusLED.py POSTs to *~/api/flud.php*, which queries the database for service issues and last transaction for device.  This data is echoed by *~/api/flud.php* to *DeviceStatusLED.py* as a JSON.  

	#####Color
	Reading this data, the python script will select a color, maintaining service issues as priority.  Color values are stored in global variables that have the HIGH/LOW RGB values as an array—[R, G, B].
	Statuses and color correspond as follow:
	- Service issue greater than 7: **RED**
	- Service issues =< 7 or no connection: **YELLOW**
	- Last ticket status is ended: **GREEN**
	- Last ticket status is *active* (being used): **BLUE**
	- Last ticket status is *moveable* (job done but not ended): **PURPLE**

	#####GPIO
	GPIO is controlled through the module `RPi.GPIO`.
	Each color of RGB has its own pin.  Because cathode and anode LEDs have different current directions, color arrays use boolean variables called `ON` and `OFF` to indicate which color is being used.  The bool value for ON and OFF are set by the global bool `CATHODE`, which is set `True` if the LED is a cathode or `False` if it is an anode.  For example, Red (255,0,0) #FF0000 will have the corresponding python array `[ON, OFF, OFF]` and cathode values of [HIGH, LOW, LOW] and anaode values of [LOW, HIGH, HIGH].
	The GPIO pins are stored in a global variable called `PINS`.  When setting the output values, a for loop iterates [0-3) and sets the GPIO pin at `PIN[index]` to a value of the `<SELECTED_COLOR>[index]`.

	#####LED
	Depending on the LED used, this may change.  The RGB LEDs used were connected to (3) 200Ohm resistors on the R,G,B pins.  The lead pin was then connected to GPIO 3.3V pin.
	
#### Error
If an error occurs, the python error message will write to a text log called *LED_error_log.txt* and includes the function in which the error occured and the time.

The service created will start after dhcpcd, as it needs internet to connection to pull device status.
