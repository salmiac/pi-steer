## Raspberry Pi Pico W pinout
|Pico| Pico pin | device pin |
|--|--|--|
|UART0 TX | 1 | BNO085 SDA |
|UART0 TX | 2 | BNO085 SCL |
|GND | 3 | BNO085 GND |
|3V3(OUT) | 36 | GND085 GND |


## MicroPico VSCode extension.

https://www.hackster.io/shilleh/how-to-use-vscode-with-raspberry-pi-pico-w-and-micropython-de88d6

## micropython download 
https://micropython.org/download/RPI_PICO_W/

Copy main.py to pico.
Create config.json and copy it to pico.
```json
{
    "SSID": "<your ssid>",
    "WIFI_PASS": "<your password>"
}
```
