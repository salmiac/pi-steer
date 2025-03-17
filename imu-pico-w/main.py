import struct
import sys
from micropython import const, kbd_intr
import _thread
from machine import Pin
from time import sleep
import network
from machine import UART
import socket
import json

def read_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    return config['SSID'], config['WIFI_PASS']

_SSID, _WIFI_PASS = read_config()
_IP = const('255.255.255.255')
_PORT = const(9999)

status = {
    network.STAT_IDLE: 'no connection and no activity',
    network.STAT_CONNECTING: 'connecting',
    network.STAT_WRONG_PASSWORD: 'connection failed due to incorrect password',
    network.STAT_NO_AP_FOUND: 'connection failed because no access point replied',
    network.STAT_CONNECT_FAIL: 'connection failed for the reason not in the other categories',
    network.STAT_GOT_IP: 'successfully connected and got an IP address',
}

def read_imu(uart):
    while True:
        data = uart.read(1)
        if data is not None and len(data) != 0 and data[0] == 0xaa:
            data = uart.read(1)
            if data is not None and len(data) != 0 and data[0] == 0xaa:
                sleep(0.002)
                data = uart.read(17)
                if data is not None and len(data) == 17:
                    (
                        index,
                        heading,
                        pitch,
                        roll,
                        acc_x,
                        acc_y,
                        acc_z,
                        mi,
                        mr,
                        res,
                        csum
                    ) = struct.unpack_from("<BhhhhhhBBBB", data)
                    if csum != sum(data[0:16]) % 256:
                        continue
                    return heading*0.01, roll*0.01, pitch*0.01

def send_imu_data(heading, roll, angular_velocity):
    data = bytearray([0x80, 0x81, 0x79, 0xd3, 0x08])
    heading_int = int(heading * 10)
    for b in struct.pack('<H', heading_int):
        data.append(b)
    roll_int = int(roll * 10)
    for b in struct.pack('<H', roll_int):
        data.append(b)
    angular_velocity_int = int(angular_velocity)
    for b in struct.pack('<H', angular_velocity_int):
        data.append(b)
    data.append(0x00)
    data.append(0x00)

    crc = 0
    for byte in data[2:]:
        crc += byte
    crc %= 256
    data.append(crc)
    send_udp(data)

def send_udp(data):
    addr_info = socket.getaddrinfo(_IP, _PORT)
    addr = addr_info[0][-1]

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(data, addr)
    s.close()
    print(''.join(['{:02x}:'.format(byte) for byte in data]))

def connect_to_network(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # wlan.hostname("imu-pico-w")
    # wlan.config(reconnects=5)
    while True:
        wlan.connect(ssid, password)

        # Wait for connection
        while not wlan.isconnected():
            sleep(1)
            
            print("Connecting to network... ", ssid, status[wlan.status()])
            if wlan.status() == network.NO_AP_FOUND or wlan.status() == network.CONNECT_FAIL:
                print("Connect failed, retrying...")
                break

        print('Network config:', wlan.ifconfig())
        return wlan

uart0 = UART(0, baudrate=115200)

base_roll = 0
sleep(1)
(heading, roll, pitch) = read_imu(uart0)
print("Base roll", roll)
if -135 < roll < -45:
    base_roll = -90
elif 45 < roll < 135:
    base_roll = 90
elif roll > 135 or roll < -135:
    base_roll = 180

while True:
    try:
        wlan = connect_to_network(_SSID, _WIFI_PASS)
        pin = Pin("LED", Pin.OUT)

        while True:
            pin.toggle()
            (heading, roll, pitch) = read_imu(uart0)
            roll -= base_roll
            send_imu_data(heading, roll, 0) # TODO angular velocity
            print(heading, roll, pitch)
            # sleep(1)  # Add a delay to avoid busy-waiting

    except Exception as e:
        print("Network error:", e)
        print("Reconnecting to network...")
        sleep(5)  # Wait before attempting to reconnect
