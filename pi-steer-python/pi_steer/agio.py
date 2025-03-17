import time
import pi_steer.debug as db
import pi_steer.section_control
import socket
import struct
import threading

_HELLO = 0xc7
_LATLON = 0xd0
_AGIOTRAFFIC = 0xd2
_IMU = 0xd3
_IMU_DETACH_REQ = 0xd4
_NMEA_BYTES = 0xd5
_SWITCH_CONTROL = 0xea
_MACHINE_CONFIG = 0xee
_RELAY_CONFIG = 0xec
_MACHINE_DATA = 0xef
_STEER_CONFIG = 0xfb
_STEERSETTINGS = 0xfc
_FROM_AUTOSTEER = 0xfd
_AUTOSTEER_DATA = 0xfe


source_text = {
    0x7b: 'switch control',
    0x7c: 'GPS',
    0x7d: 'IMU',
    0x7e: 'Autosteer',
    0x7f: 'AgIO',
}

pgn_text = {
    _HELLO: 'Hello???',
    _LATLON: 'LatLon',
    _AGIOTRAFFIC: 'AgIOTraffic',
    _IMU: 'IMU',
    _IMU_DETACH_REQ: 'IMU Detach Req',
    _NMEA_BYTES: 'NMEA bytes',
    _SWITCH_CONTROL: 'switchControl',
    _MACHINE_CONFIG: 'machineConfig',
    _RELAY_CONFIG: 'relayConfig',
    _MACHINE_DATA: 'machineData',
    _STEER_CONFIG: 'steerConfig',
    _STEERSETTINGS: 'steerSettings',
    _FROM_AUTOSTEER: 'fromAutoSteer',
    _AUTOSTEER_DATA: 'autoSteerData',
}

pgn_data = {
    _HELLO: # Hello???
    lambda data: { 
    },
    _LATLON: # LatLon
    lambda data: { 
        'Latitude': struct.unpack('<i', data[0:4])[0],
        'Longitude': struct.unpack('<i', data[0:4])[0],
    },
    _AGIOTRAFFIC: # AgIOTraffic
    lambda data: { 
        'Seconds': data[0],
    },
    _IMU: # IMU
    lambda data: { 
        'Heading': struct.unpack('<h', data[0:2])[0]/10.0,
        'Roll': struct.unpack('<h', data[2:4])[0]/10.0
    },
    _IMU_DETACH_REQ: # IMU Detach Req
    lambda data: { # Removed ?
    },
    _NMEA_BYTES: # NMEA bytes
    lambda data: { # ???
    },
    _SWITCH_CONTROL: # switchControl
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
    _MACHINE_CONFIG: # machineConfig
    lambda data: { 
        'raiseTime': data[0],
        'lowerTime': data[1],
        'hydEnable': data[2],
        'set0': data[3],
        'User1': data[4],
        'User2': data[5],
        'User3': data[6],
        'User4': data[7]
    },
    _RELAY_CONFIG: # machineConfig
    lambda data: { 
        'Pin 1': data[0],
        'Pin 2': data[1],
        'Pin 3': data[2],
        'Pin 4': data[3],
        'Pin 5': data[4],
        'Pin 6': data[5],
        'Pin 7': data[6],
        'Pin 8': data[7],
        'Pin 9': data[8],
        'Pin 10': data[9],
        'Pin 11': data[10],
        'Pin 12': data[11],
        'Pin 13': data[12],
        'Pin 14': data[13],
        'Pin 15': data[14],
        'Pin 16': data[15],
        'Pin 17': data[16],
        'Pin 18': data[17],
        'Pin 19': data[18],
        'Pin 20': data[19],
        'Pin 21': data[20],
        'Pin 22': data[21],
        'Pin 23': data[22],
        'Pin 24': data[23]
    },
    _MACHINE_DATA: # machineData
    lambda data: { 
        'uturn': data[0],
        'Speed': data[1]/10.0,
        'hydLift': data[2],
        'Tram': data[3],
        'Geo Stop': data[4],
        'SC': struct.unpack('<H', data[6:8])[0],
    },
    _STEER_CONFIG: # steerConfig
    lambda data: { 
        'set0': data[0],
        'invertWas': data[0] & 1,
        'steerInvertRelays': data[0] >> 1 & 1,
        'invertSteer': data[0] >> 2 & 1,
        'conv': 'Single' if data[0] >> 3 & 1 else 'Differential',
        'motorDrive': 'Cytron' if data[0] >> 4 & 1 else 'IBT2',
        'steerEnable': 'Switch' if data[0] >> 5 & 1 else ('Button' if data[0] >> 6 & 1 else 'None'),
        'encoder': data[0] >> 7 & 1,
        'pulseCount': data[1],
        'minSpeed': data[2],
        'sett1': data[3],
        'danfoss': data[3] & 1,
        'pressureSensor': data[3] >> 1 & 1,
        'currentSensor': data[3] >> 2 & 1,
    },
    _STEERSETTINGS: # steerSettings
    lambda data: { 
        'gainP': data[0],
        'highPWM': data[1],
        'lowPWM': data[2],
        'minPWM': data[3],
        'countsPerDeg': data[4],
        'steerOffset': struct.unpack('<h', data[5:7])[0]/100.0,
        'ackermanFix': data[7],
    },
    _FROM_AUTOSTEER: # fromAutoSteer
    lambda data: { 
        'ActualSteerAngle': struct.unpack('<h', data[0:2])[0]/100.0,
        'IMU Heading Hi/Lo': struct.unpack('<h', data[2:4])[0]/10.0,
        'IMU Roll Hi/Lo': struct.unpack('<h', data[4:6])[0]/10.0,
        'Switch': data[6],
        'PWMDisplay': data[7],
    },
    _AUTOSTEER_DATA: # autoSteerData
    lambda data: { 
        'Speed': struct.unpack('<H', data[0:2])[0]/10.0,
        'Status': data[2],
        'SteerAngle': struct.unpack('<h', data[3:5])[0]/100.0,
        'SC': struct.unpack('<H', data[6:8])[0],
    },
}

alive = [0x80,0x81, 0x7f, 0xC7, 1, 0, 0x47]

class AgIO():
    def __init__(self, settings, motor_control, debug=False):
        self.debug=debug
        self.motor_control=motor_control
        self.settings = settings
        self.sc = pi_steer.section_control.SectionControl()
        self.server=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.server.bind(('', 8888))
        self.server.settimeout(0.1)

        self.client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.client.settimeout(0)
        self.client.setblocking(0)

        self.reader_thread = threading.Thread(target=self.read)
        self.reader_thread.start()

    def __del__(self):
        self.reader_thread.join(0)

    def decode_data(self, data):
        try:
            source = data[2]
            pgn = data[3]
            length = data[4]
            crc = data[5+length]
            crc_sum = 0
            for byte in data[2:length+5]:
                crc_sum += byte
            crc_sum %= 256

            crc_text = 'CRC failed.'
            crc_ok = False
            if crc == crc_sum:
                crc_text = 'CRC Ok.'
                crc_ok = True
            else:
                return (None, None)
            
            payload = pgn_data[pgn](data[5:length+5])
            payload_text = '| Payload:'
            for key in payload.keys():
                payload_text += ' ' + key + ' : ' + str(payload[key])
        except KeyError:
            return (None, None)

        if self.debug and pgn not in [0xfe, 0xef, 0xfd]:
            db.write('From: {} | PGN: {} | {} | {}'.format(source_text[source], pgn_text[pgn], payload_text, crc_text))

        if crc_ok:
            self._pgn_handler(pgn, payload)

    def read(self) -> None:
        while True:
            try:
                while True:
                    (data, address)=self.server.recvfrom(1024)
                    if len(data) < 6:
                        continue
                    if data[0] == 0x80 and data[1] == 0x81:
                        self.decode_data(data)
            except socket.error as err:
                if self.debug:
                    db.write('Read socket error: {}'.format(err))
            except socket.timeout as err:
                if self.debug:
                    db.write('Read socket timeout: {}'.format(err))

    def _pgn_handler(self, pgn, payload) -> None:
        if pgn is not None:
            if pgn == _STEER_CONFIG:
                if self.debug:
                    db.write('steer config')
                self.settings.settings.update(payload)
                self.settings.save_settings()
                return
            if pgn == _STEERSETTINGS:
                if self.debug:
                    db.write('steer settings')
                self.settings.settings.update(payload)
                self.settings.save_settings()
                return
            if pgn == _AUTOSTEER_DATA:
                if self.debug:
                    db.write('autosteer data')
                if payload is not None:
                    self.motor_control.set_control(payload)
                    if self.debug:
                        db.write(payload['SC'])
                    self.sc.update(payload['SC'])
                return
            if pgn == _MACHINE_DATA:
                if self.debug:
                    db.write('machine data')
                if payload is not None:
                    self.sc.update(payload['SC'])
                return

    def alive(self):
        self.client.sendto(bytes(alive), ('255.255.255.255',9999))

    def from_autosteer(self, wheel_angle, heading, roll, switch, pwm_display):
        data = bytearray([0x80, 0x81, 0x7e, 0xfd, 0x08])
        wheel_angle_int = int(wheel_angle * 100)
        data.extend(list(struct.pack('<h', wheel_angle_int)))
        heading_int = int(heading * 10)
        data.extend(list(struct.pack('<h', heading_int)))
        roll_int = int(roll * 10)
        data.extend(list(struct.pack('<h', roll_int)))

        data.append(switch)
        data.append(pwm_display)

        crc = 0
        for byte in data[2:]:
            crc += byte
        crc %= 256
        data.append(crc)

        try:
            self.client.sendto(bytes(data), ('255.255.255.255',9999))
        except Exception as err:
            if self.debug:
                db.write('Send error: {}'.format(err))
