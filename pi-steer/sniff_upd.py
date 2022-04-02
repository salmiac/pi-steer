import binascii
import socket
import struct

source_text = {
    0x7b: 'switch control',
    0x7c: 'GPS',
    0x7d: 'IMU',
    0x7e: 'Autosteer',
    0x7f: 'AgIO',
}

pgn_text = {
    0xc7: 'Hello???',
    0xd0: 'LatLon',
    0xd2: 'AgIOTraffic',
    0xd3: 'IMU',
    0xd4: 'IMU Detach Req',
    0xd6: 'NMEA bytes',
    0xea: 'switchControl',
    0xee: 'machineConfig',
    0xef: 'machineData',
    0xfb: 'steerConfig',
    0xfc: 'steerSettings',
    0xfd: 'fromAutoSteer',
    0xfe: 'autoSteerData',
}

pgn_data = {
    0xc7: # Hello???
    lambda data: { 
    },
    0xd0: # LatLon
    lambda data: { 
        'Latitude': int.from_bytes(data[0:4], byteorder='little', signed=True),
        'Longitude': int.from_bytes(data[0:4], byteorder='little', signed=True),
    },
    0xd2: # AgIOTraffic
    lambda data: { 
        'Seconds': data[0],
    },
    0xd3: # IMU
    lambda data: { 
        'Heading': int.from_bytes(data[0:2], byteorder='little', signed=True)/10.0,
        'Roll': int.from_bytes(data[2:4], byteorder='little', signed=True)/10.0
    },
    0xd4: # IMU Detach Req
    lambda data: { # Removed ?
    },
    0xd6: # NMEA bytes
    lambda data: { # ???
    },
    0xea: # switchControl
    lambda data: { 
        'Main': data[0],
        'Res1': data[1],
        'Res2': data[2],
        '# sections': data[3],
        'On Group 0': bin(data[4])[2:],
        'Off Group 0': bin(data[5])[2:],
        'On Group 1': bin(data[6])[2:],
        'Off Group 1': bin(data[7])[2:],
    },
    0xee: # machineConfig
    lambda data: { 
        'raiseTime': data[0],
        'lowerTime': data[1],
        'hydEnable': data[2],
        'set0': data[3],
    },
    0xef: # machineData
    lambda data: { 
        'uturn': data[0],
        'tree': data[1],
        'hydLift': data[2],
        'Tram': data[3],
        'SC': bin(int.from_bytes(data[6:8], byteorder='big', signed=False))[2:],
    },
    0xfb: # steerConfig
    lambda data: { 
        'set0': data[0],
        'pulseCount': data[1],
        'minSpeed': data[2],
        'sett1': data[3],
    },
    0xfc: # steerSettings
    lambda data: { 
        'gainP': data[0],
        'highPWM': data[1],
        'lowPWM': data[2],
        'minPWM': data[3],
        'countsPerDeg': data[4],
        'steerOffset': int.from_bytes(data[5:7], byteorder='little', signed=True),
        'ackermanFix': data[7],
    },
    0xfd: # fromAutoSteer
    lambda data: { 
        'ActualSteerAngle': int.from_bytes(data[0:2], byteorder='little', signed=True)/100.0,
        'IMU Heading Hi/Lo': int.from_bytes(data[2:4], byteorder='little', signed=True)/10.0,
        'IMU Roll Hi/Lo': int.from_bytes(data[4:6], byteorder='little', signed=True)/10.0,
        'Switch': data[6],
        'PWMDisplay': data[7],
    },
    0xfe: # autoSteerData
    lambda data: { 
        'Speed': int.from_bytes(data[0:2], byteorder='little', signed=False)/10.0,
        'Status': data[2],
        'SteerAngle': int.from_bytes(data[3:5], byteorder='little', signed=True)/100.0,
        'SC': bin(int.from_bytes(data[6:8], byteorder='big', signed=False))[2:],
    },
}

def decode_data(data):
    source = data[2]
    pgn = data[3]
    length = data[4]
    crc = data[5+length]
    crc_sum = 0
    for byte in data[2:length+5]:
        crc_sum += byte
    crc_sum %= 256

    crc_text = 'CRC failed.'
    if crc == crc_sum:
        crc_text = 'CRC Ok.'
    
    payload = pgn_data[pgn](data[5:length+5])
    payload_text = '| Payload:'
    for key in payload.keys():
        payload_text += ' ' + key + ' : ' + str(payload[key])

    print(
        'From:', source_text[source], 
        '| PGN:', pgn_text[pgn],
        payload_text,
        '| ', crc_text
    )

def main():
    print('Init')
    client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(('', 8888))
    while True:
        (data, address)=client.recvfrom(1024)
        if data[3] in [ 0xfe, 0xef]:
            continue
        print(binascii.hexlify(data, '-'), address)
        if data[0] == 0x80 and data[1] == 0x81:
            pass
            # decode_data(data)

if __name__ == "__main__":
    main()
