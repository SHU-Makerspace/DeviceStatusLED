# DeviceStatusLED
RGB LED notification light for API call to FabApp for device status.

### Installation
To install the program cd into the cloned folder use the bash script setup with
`sh setup`
From here you will be prompted to enter the device number (as stored in the database) and the API key (also in the DB).
Following this, the setup script will create, enable, and start the service for Device Status.  From this point on reboot and start up the python script will run automatically.  

DeviceStatusLED.py POSTs to ~/api/flud.php, which queries the database for service issues and last transaction for device.  This data is echoed by ~/api/flud.php to DeviceStatusLED.py as a JSON.  Reading this data, the python script will select a color, maintaining service issues as priority.  Statuses and color correspond as follow:
- Service issue greater than 7: **RED**
- Service issues =< 7: **YELLOW**
- Last ticket status is ended: **GREEN**
- Last ticket status is *active* (being used): **BLUE**
- Last ticket status is *moveable* (job done but not ended): **PURPLE**
