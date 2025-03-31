# Python app
This Python app is deprecated. It should work, maybe.

## IMU

BNO055 and BNO085 are supported. Software detects and selects witch ever is connected. BNO085 is supposed to be better than BNO055. The problem is that at the moment as I am writing this BNO085 is almost impossible to found anywhere.

I have used both at 2020. Earlier I used Adafruit libraries for both.

BNO055 was mostly unusable. roll was drifting very bad and heading was jumping randomly. I have written more direct messaging based on datasheet. There are still some errors which are taken care of. Roll is OK, heading drifts slightly on moving tractor. It's not good but it is usable, at least on higher GPS heading usage.

The problem with BNO085 is that I2C communication is more complicated to write and I2C (at least Adafruit I2C library) is very unstable, it crashes often. Luckily there is more simple solution. When PC0 pin set high, xxxx-RCV mode is activated and BNO085 sends easy to use data at 100 Hz rate. And it seems to be stable.

#### BNO055 

BNO055 is connected by I2C.
You shoud not use BNO055, the drift is just terrible. Use BNO085 instead.

Wires connectedd to raspberry Pi.
|GPIO|Pi pin number|BNO085|
|--|--|--|
|3v3 Power|1|VIN|
|I2C1 SDA|3|SDA|
|I2C1 SCL|5|SCL|
|Ground|9|GND|

https://github.com/adafruit/Adafruit_BNO055

https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bno055-ds000.pdf

https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles


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

Set hardware PWM on Raspberry Pi 3
https://blog.oddbit.com/post/2017-09-26-some-notes-on-pwm-on-the-raspb/

Now it is not fully hardware PWM. I think it uses DMA and maybe kernel code to maintain PWM, 20 kHz uses uses about 100 % of CPU. 2 kHz is used is this code.
It is still a lot better than gpiozero fully software PWM, where maximum practical frequency is around 300 Hz.

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


## Tools
Some Python tools.

### sniff-aog.py
Tool to read AgOpenGPS UDP data.

### test_ads1115.py
Tool to test ADS1115 ADC.

### test_bno085.py
Tool to test BNO085 IMU.

### test_cytron_pwm.py
Test Cytron PWM motor controller (and motor).
