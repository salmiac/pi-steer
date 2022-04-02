import time
import socket

client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
client.settimeout(0.2)

while True:
    client.sendto(bytes([0x80,0x81, 0x7f, 0xC7, 1, 0, 0x47]), ('255.255.255.255',9999))
    time.sleep(1)

