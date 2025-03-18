# PiSteer
Autosteer controller. 

## Warning
This just just for demonstration and proof of concept. This should never ever be used on full sized machinery. You will crash and die if You do. You have been warned.

## Other documents
Pictures and something [here](Documents/README.md).

## Raspberry Pi 3
Why Raspberry Pi? It's just somethin I had laying around.

### install

Configure raspberry:
```bash
sudo raspi-config
```
From System Options set Wireless LAN, from Interface Options enable I2C, disable login console on serial port, enable serial port hardware.

Edit `/boot/firmware/config.txt`
```bash
sudo nano /boot/firmware/config.txt
```
Add the line `dtoverlay=pwm,pin=12,func=4`
Save the file and reboot.

```bash
wget https://github.com/salmiac/pi-steer/releases/download/v0.1.2/pi-steer-rust
chmod +x pi-steer-rust-raspberry-pi-3
```
Run it once and default settings file (`settings.json`) is created.
Edit file.
```bash
nano settings.json
```

To build binaries Yourself [look here](pi-steer-rust/README.md)

## Raspberry Pi Pico W

Is used as standalone IMU. [README.md](imu-pico-w/README.md)

## Raspberry Pi pinout
|Device|pin|Pi GPIO|Pi pin|Pi pin|Pi GPIO|pin|Device|
|--|--|--|--|--|--|--|--|
|BSS138, BNO055, BNO085 VCC/PS0|LV, VIN|3v3 Power|1|2|5V Power|HV, VDD|BSS138, ADS1115|
|BSS138 (ADS1115), BNO055|A2, SDA|I2C SDA|3|4|5V Power|VCC, 1-A|RTY120LVNAA|
|BSS138 (ADS1115), BNO055|A1, SCL|I2C SCL|5|6|Ground|GND, 2-B|RTY120LVNAA|
|Relay|1|GPIO 4|7|8|GPIO 14|TXD|BNO085 SCL/SCK/RX|
|BNO055|GND|Ground|9|10|GPIO 15|RXD|BNO085 S/MISO/TX|
|Relay|2|GPIO 17|11|12|GPIO 18|2|Manual (in)|
|Autosteer switch|A|GPIO 27|13|14|Ground|GND|Relay|
|Relay|3|GPIO 22|15|16|GPIO 23|3|Manual (in)|
|LED:s|+|3v3 Power|17|18|GPIO 24|4|Manual (in)|
|Relay|4|GPIO 10|19|20|Ground|-|Power LED|
|Relay|5|GPIO 9|21|22|GPIO 25|5|Manual (in)|
|Relay|6|GPIO 11|23|24|GPIO 8|14|Relay|
|Autosteer switch|B|Ground|25|26|GPIO 7|13|Relay|
|Relay|7|GPIO 0|27|28|GPIO 1|12|Relay|
|Relay|8|GPIO 5|29|30|Ground|GND|BSS138|
|Relay|9|GPIO 6|31|32|GPIO 12, PWM 0|PWM|Cytron|
|Work switch||GPIO 13|33|34|Ground|GND|Cytron|
|Relay, manual mode|2|GPIO 19|35|36|GPIO 16|DIR|Cytron|
|Manual (in)|1|GPIO 26|37|38|GPIO 20|11|Relay|
|Relay mode switch|GND|Ground|39|40|GPIO 21|10|Relay|

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
|5V Power|4||VIN|1-A|
|||SDA|B1||
|||SCL|B2||
|Ground|20|GND|GND|2-B|
|||A0||3-C|

### Inertial masurement unit (IMU)

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

#### BNO085

BNO085 is connected by serial. It uses xxxx-RCV mode. 

Wires connectedd to raspberry Pi.
|GPIO|Pi pin number|BNO085|
|--|--|--|
|3v3 Power|1|VIN|
|I2C1 SDA|XX|SDA|
|I2C1 SCL|XX|SCL|
|Ground|9|GND|
|PC0|9|GND|


https://learn.adafruit.com/adafruit-9-dof-orientation-imu-fusion-breakout-bno085

https://www.ceva-dsp.com/wp-content/uploads/2019/10/BNO080_085-Datasheet.pdf

## Motor controller Cytron MD13S
https://docs.google.com/document/d/1icu1GVDxZhUn3ADSUc3JknNcmUMdPcsnJ4MhxOPRo-I/view

Set hardware PWM on Raspberry Pi 3
https://blog.oddbit.com/post/2017-09-26-some-notes-on-pwm-on-the-raspb/

Now it is not fully hardware PWM. I think it uses DMA and maybe kernel code to maintain PWM, 20 kHz uses uses about 100 % of CPU. 2 kHz is used is this code.
It is still a lot better than gpiozero fully software PWM, where maximum practical frequency is around 300 Hz.

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

# Relays
Pololu Basic 2-Channel SPDT Relay Carrier with 12VDC Relays
https://www.pololu.com/product/2485

|GPIO|Pi pin number|relay|12V|Output|
|--|--|--|--|--|
|GND|14|GND|||
|||GND|GND|Out GND|
|||VDD|+12 V||
|GPIO 4|7|EN1|||
|GPIO 17|11|EN2|||
|||NO1||Output Up|
|||NO2||Output Down|

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
