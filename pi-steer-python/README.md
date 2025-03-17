# Python app
This Python app is deprecated. It should work, maybe.

### Install Python app (deprecated)

From fresh Raspberry PI OS.
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install pip
pip install smbus2
pip install pyserial
```

Configure raspberry:
```
sudo raspi-config
```
From System Options set Wireless LAN, from Interface Options enable I2C, disable login console on serial port, enable serial port hardware.

Edit `/boot/firmaware/config.txt`
```
sudo nano /boot/firmaware/config.txt
```
Add the line `dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4`
Save the file and reboot.

## Run program 
Run program by:

`python pi-steer-python/autosteer.py`

To start automatically at boot enter `crontab -e` and add following line.
```
@reboot python /home/pi/pi-steer/autosteer.py & > /dev/null 2>&1
```

sudo crontab -e
@reboot /bin/sleep 5; /usr/bin/python /home/pi/pi-steer/autosteer.py &
