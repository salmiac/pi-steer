# aog-udp-sniffer
Tool to read AgOpenGPS UDP data.

## Raspberry Pi 3
Why Raspberry Pi? It's somethin I had laying around.

## Automation HAT
Why Automation HAT? It's also something I had.

Automation HAT Connections
|Function|GPIO|HAT connection|Pi pin number|
|--|--|--|--|
|Angle sensor signal||Analog 1||
|Angle sensor GND||GND||
|Angle sensor Vcc||5V||
|Motor direction|GPIO 5|Output 1|BCM 29|
|Motor PWM|GPIO 12|Output 2|BCM 32|
|Autosteer on-led|GPIO 6|Output 3|BCM 31|
|Autosteer switch|GPIO 26|Input 1|BCM 37|

## Wheel angle sensor **RTY120LVNAA**
|Function|pin|
|--|--|
|Vcc|1-A|
|GND|2-B|
|output|3-C|

## Adafruit BNO055 Absolute Orientation Sensor
Why this instead of BNO085? It was available.

Wires soldered to raspberry Pi - Automation HAT pins.
|GPIO|Pi pin number|BNO055|
|--|--|--|
|3v3 Power|1|VIN|
|I2C1 SDA|3|SDA|
|I2C1 SCL|5|SCL|
|Ground|7|GND|

## Motor controller Cytron MD13S
https://docs.google.com/document/d/1icu1GVDxZhUn3ADSUc3JknNcmUMdPcsnJ4MhxOPRo-I/view

Set hardware PWM on Raspberry Pi 3
https://blog.oddbit.com/post/2017-09-26-some-notes-on-pwm-on-the-raspb/

edit `/boot/config.txt`
Add the line `dtoverlay=pwm-2chan`
Save the file and reboot.

Motor controller wiring
|GPIO|Pi pin number|Cytron|
|--|--|--|
|Ground|6|GND|
|GPIO 18, PWM0|12|PWM|
|GPIO 25|22|DIR|

## Autosteer switch
A microswitch between Automation HAT +5V and Input 1. A 2K2 resistor is also connected from Input 1 to GND just to make sure Input 1 is low when switch is disconnected.

## Status LEDs

|Automation HAT Output|description|
|--|--|
|3|Autosteed activated|

