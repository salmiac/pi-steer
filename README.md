# PiSteer
Autosteer controller.

Run program by:

`python3 autosteer.py`

## Raspberry Pi 3
Why Raspberry Pi? It's somethin I had laying around.

### Install

From fresh Raspberry PI OS Lite.
```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
sudo pip3 install adafruit-circuitpython-ads1x15
sudo pip3 install adafruit-circuitpython-bno08x
```

enable i2C interface

`sudo raspi-config`

edit `/boot/config.txt` Add the line `dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4` Save the file and reboot.

## Raspberry Pi pinout
|Device|pin|Pi GPIO|Pi pin|Pi pin|Pi GPIO|pin|Device|
|--|--|--|--|--|--|--|--|
|BSS138, BNO085|VCC|3v3 Power|1|2|5V Power|VCC|BSS138, RTY120LVNAA|
|BSS138, BNO085|A2, SDA|I2C SDA|3|4|5V Power|||
|BSS138, BNO085|A1, SCL|I2C SCL|5|6|Ground|GND|Cytron|
|||GPIO 4|7|8|GPIO 14|||
|BNO085|GND|Ground|9|10|GPIO 15|||
|BNO085|RST|GPIO 17|11|12|GPIO 18|||
|Autosteer switch|A|GPIO 27|13|14|Ground|GND|ADS1115|
|Autosteer activated LED|-|GPIO 22|15|16|GPIO 23|-|Program activity LED|
|LED:s|+|3v3 Power|17|18|GPIO 24|||
|||GPIO 10|19|20|Ground|-|Power LED|
|||GPIO 9|21|22|GPIO 25|DIR|Cytron|
|||GPIO 11|23|24|GPIO 8|-|Motor direction LED|
|Autosteer switch|B|Ground|25|26|GPIO 7|||
|||GPIO 0|27|28|GPIO 1|||
|||GPIO 5|29|30|Ground|GND|BSS138|
|||GPIO 6|31|32|GPIO 12, PWM 0|PWM|Cytron|
|||GPIO 13|33|34|Ground|||
|||GPIO 19|35|36|GPIO 16|||
|||GPIO 20|37|38|GPIO 20|||
|RTY120LVNAA|GND|Ground|39|40|GPIO 21|||

## Wheel angle sensor **RTY120LVNAA**
|Function|pin|
|--|--|
|Vcc 5V|1-A|
|GND|2-B|
|output|3-C|

## Adafruit ADS1115 4-Channel ADC and 4-channel I2C-safe Bi-directional Logic Level Converter - BSS138
Wires connectedd to raspberry Pi via level converter

|GPIO|Pi pin number|BSS138|
|--|--|--|
|3v3 Power|1|LV|
|5V Power|2|HV|
|I2C1 SDA|3|A1|
|I2C1 SCL|5|A2|
|Ground|7|GND||

|GPIO|Pi pin number|ADS1115|BSS138|RTY120LVNAA|
|--|--|--|--|--|
|5V Power|4||VIN|1|
|||SDA|B1||
|||SCL|B2||
|Ground|20|GND|GND|3|
|||A0||2|

## Adafruit BNO085 Absolute Orientation Sensor
Wires connectedd to raspberry Pi.
|GPIO|Pi pin number|BNO085|
|--|--|--|
|3v3 Power|1|VIN|
|I2C1 SDA|3|SDA|
|I2C1 SCL|5|SCL|
|Ground|9|GND|

## Motor controller Cytron MD13S
https://docs.google.com/document/d/1icu1GVDxZhUn3ADSUc3JknNcmUMdPcsnJ4MhxOPRo-I/view

Set hardware PWM on Raspberry Pi 3
https://blog.oddbit.com/post/2017-09-26-some-notes-on-pwm-on-the-raspb/

edit `/boot/config.txt`
Add the line `dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4`
Save the file and reboot.

Motor controller wiring
|GPIO|Pi pin number|Cytron|
|--|--|--|
|Ground|6|GND|
|GPIO 12, PWM0|32|PWM|
|GPIO 25|22|DIR|

## Autosteer switch
A microswitch to activate autosteer is connected to Raspberry Pi:
|GPIO|Pi pin number|switch|
|--|--|--|
|Ground|30|A|
|GPIO 27|13|B|


## Status LEDs

Leds are connected between 3.3 V power (pin 17) and control pins
|GPIO|Pi pin number|description|
|--|--|--|
|GPIO 22|15|Autosteer activated|
|GPIO 8|24|Motor direction|
|GPIO 23|16|Program activity|
|Ground|20|Power on|

## Section control
Not implemented, sorry.

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
