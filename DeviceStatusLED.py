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
FLUD_API = "~/api/flud.php"  #EDIT: edit for makerspace API URL
DEVICE_ID = "21"  #EDIT: UTA poly-printers start at 21
API_KEY = ""  #EDIT: DB site_variable API_KEY value

# ——— COLOR ———
# service
RED = [255, 0, 0]  # broken
YELLOW = [255, 255, 0]  # issue
# print
GREEN = [0, 255, 0]  # free
BLUE = [0, 0, 255]  # moveable
PURPLE = [155, 0, 155]  # active
# other
BLACK = [0, 0, 0]
OFF = [0, 0, 0]
WHITE = [255, 255, 255]

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
			return write_to_error_log(request["ERROR"])
		return request

	except:
		return write_to_error_log("cannot get printer status")


# determine color for status of printer (service has color priority, then ticket)
def color_for_status(response):
	try:
		print(response)  #TESTING
		if(response["service_issue"] and 7 < response["service_issue"]): return RED
		# elif(response["service_issue"]): return YELLOW  #FUTURE: known issue, but usable

		statuses = {"active": PURPLE, "moveable": BLUE}
		return statuses[response["transaction_state"]] if response["transaction_state"] in statuses else GREEN

	except:
		return write_to_error_log("cannot get color status")


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

	except:
		write_to_error_log("cannot set state of LED")


# if exception occurs, this function is called to document issue & return None
def write_to_error_log(error_message):
	with open("LED_error_log.txt", "a") as error_log:
		error_log.write("ERROR: " + error_message + ", " + str(datetime.now()) + "\n")
	return None  # no valid value



def main():
	while(True):
		try:
			flud_response = query_printer_status()
			color = color_for_status(flud_response) if flud_response else None
			print(color)  #TESTING
			if(color): set_light_state(color)
			sleep(5)

		except:
			write_to_error_log("main loop error")

if __name__ == '__main__':
	main()
