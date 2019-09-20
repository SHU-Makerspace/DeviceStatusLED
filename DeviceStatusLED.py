#!/usr/bin/python3

###########################################################################
#
#	Printer State Light Client
#
#	@author MPZinke on 09.13.19
#
#	DESCRIPTION: Light addon for Raspberry Pi running octopuppet.  Using FabApp API,
#	 query last transaction for device_id and see if ticket is still active.  Combine this with 
#	 unresolved service tickets to see device status.
#	 After data queried, if device has a service level of unusable, RED is chosen for the light
#	 color.  Otherwise, a GREEN light is if the device is available for a new ticket.  BLUE if it 
#	 the ticket is active. PURPLE if the ticket is 'moveable' and needs to be removed/stored.
#	 With the chosen color [R, G, B], GPIO pins are set
#	FUTURE:	-Device is not fully functional IE YELLOW light used.  This could be 
#				 implemented now, however, it was decided that it should not be displayed
#	BUGS:
#
###########################################################################


from datetime import datetime  # used to write time for error
import requests  # make post request
from time import sleep  # used to suspend process

# ———— SQL ———–
FLUD_API = "https://~/api/flud.php"  #EDIT: edit for makerspace API URL
DEVICE_ID = "21"  #EDIT: UTA poly-printers start at 21
API_KEY = ""  #EDIT: DB site_variable API_KEY value

# — POWER FLOW ——
# set flow of electricity in relation to LED type.  Anode LED requires 3.3V in, GPIO out while 
# cathodes require GPIO in, GND out
CATHODE = False  #EDIT: LED type used for setting high/low
ON = CATHODE
OFF = not ON



# ——— COLOR ———
# service
RED = [ON, OFF, OFF]  # broken
YELLOW = [ON, ON, OFF]  # connection issue or minor issue
# print
GREEN = [OFF, ON, OFF]  # free
BLUE = [OFF, OFF, ON]  # moveable
PURPLE = [ON, OFF, ON]  # active
# other
BLACK = [OFF, OFF, OFF]
WHITE = [ON, ON, ON]

# ——— GPIO ————
PINS = [11, 13, 15]  # [R, G, B]


# get the status for a printer (active, broken, free, finished) using MySQL
def query_printer_status():
	try:
		# make request
		header = {"authorization" : API_KEY}
		request_package = {"device_id" : DEVICE_ID, "type" : "device_status"}
		request = requests.post(FLUD_API, headers=header, json=request_package).json()

		if "ERROR" in request:
			return write_to_error_log("query_printer_status()::response: ", request["ERROR"])
		return request

	except Exception as error:
		return write_to_error_log("query_printer_status(): ", error)


# determine color for status of printer (service has color priority, then ticket)
def color_for_status(response):
	try:
		# print(response)  #TESTING
		if(response["service_issue"] and 7 < response["service_issue"]): return RED
		# elif(response["service_issue"]): return YELLOW  #FUTURE: known issue, but usable

		statuses = {"active": BLUE, "moveable": PURPLE}
		return statuses[response["transaction_state"]] if response["transaction_state"] in statuses else GREEN

	except Exception as error:
		return write_to_error_log("color_for_status(): ", error)


# set the color of a RGB LED with GPIO
def set_light_state(color):
	try:
		# set setup GPIO
		import RPi.GPIO as gpio
		gpio.setwarnings(False)
		gpio.setmode(gpio.BOARD)
		for pin in PINS:
			gpio.setup(pin, gpio.OUT)

		# set RGB values for color pins
		for x in range(3):
			gpio.output(PINS[x], color[x])

	except Exception as error:
		write_to_error_log("set_light_state(): ", error)


# if exception occurs, this function is called to document issue & return None
def write_to_error_log(function, error):
	with open("LED_error_log.txt", "a") as error_log:
		error_log.write("ERROR: " + str(error) + ", " + str(datetime.now()) + "\n")
	return None  # no valid value



def main():
	while(True):
		try:
			flud_response = query_printer_status()
			color = color_for_status(flud_response) if flud_response else YELLOW
			# print(color)  #TESTING
			if(color): set_light_state(color)
			sleep(5)

		except Exception as error:
			write_to_error_log("MAIN: ", error)

if __name__ == '__main__':
	main()
