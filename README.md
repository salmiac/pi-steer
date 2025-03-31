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
wget https://github.com/salmiac/pi-steer/releases/download/v0.1.5/pi-steer-rust
chmod +x pi-steer-rust
```
Run it once and default settings file (`settings.json`) is created.
Edit file.
```bash
nano settings.json
```

To build binaries Yourself [look here](pi-steer-rust/README.md)

## Raspberry Pi Pico W

Is used as standalone IMU. [README.md](imu-pico-w/README.md)

If GPS is connected to Raspberry Pi serial port, there is just not enough IO-pins for IMU.

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

#### BNO085

BNO085 is connected by serial. It uses xxxx-RCV mode. 

Wires connected to raspberry Pi.
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

There are 3 different modes for sections control.
- Impulse. 'impulse' is default 3 seconds. I use it for pneumatic cylinder to controld hydraulic lever. One GPIO pin for up and one for down motion.
- OnOff. It is just for on-off relays. I don't actually use it anywhere.
- Reverse. This uses a pair of GPIO pins and relays to reverse the polarity of voltage, e.g. 'On' is +12 V and 'Off' is -12 V. Sprayer sections control uses this one.

## Sprayer control

Sprayer pressure controller is separate feature from AgOpenGPS. Software on Raspberry Pi takes care of sprayer pressure reading and pressure control. One GPIO pin is also used to monitor whether boom is on locked position. Two GPIO pins (relays) are used to control pressure valve.
There are two options for pressure control, constant pressure and speed-based variable pressure. 

In my setup, this controller replaces controller for my Amazon sprayer.

Other (Windows) software is used to monitor sprayer pressure and to control settings. https://github.com/salmiac/salmiac-sprayer
Software has settings screen for nozzle spacing, nozzle size selector, litres/ha, min pressure, max pressure and nominal pressure. Nominal pressure is used for constant pressure.
Second screeen to monitor target pressure, current pressure and speed. Buttons for controller on/off and button to select variable or constant pressure. Also indicators for min and max speed for selected pressure range, indicator for boom locker yes/no and selected nozzle size.
