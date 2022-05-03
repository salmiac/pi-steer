import pi_steer.bno055
import pi_steer.bno08x
import pi_steer.quaternion
import pi_steer.debug as db
import time

BNO055_ADDRESS0 = 0x28
BNO055_ADDRESS1 = 0x29

class IMU():
    def __init__(self, debug=False):
        if debug:
            db.write('Starting IMU')
        self.debug = debug
        address = 0
        self.device = None
        self.poll_delay = 1 # 0.01
        self.bno085 = False
        self.bno055 = False

        self.device = pi_steer.bno08x.BNO08X(debug)
        if self.device.read():
            self.bno085 = True
            self.device.reader_thread.start()
        if not self.bno085:
            address = pi_steer.bno055.find_bno055()
            if address:
                self.device = pi_steer.bno055.BNO055(address, debug)
            self.bno055 = True

        if debug:
            db.write('Imu address and device {} {}'.format(address, self.device) )
        self.base_roll = 0
        for n in range(20):
            time.sleep(1)
            orientation = self.read()
            if orientation is None:
                continue
            (heading, roll, pitch) = orientation
            print("Base roll", roll)
            if roll is None:
                continue
            if -45 < roll < 45:
                break
            if -135 < roll < -45:
                self.base_roll = -90
                break
            if 45 < roll < 135:
                self.base_roll = 90
                break
            if roll > 135 or roll < -135:
                self.base_roll = 180
                break

    def read(self):
        if self.bno055 and self.device:
            for retry in range(3):
                qn = None
                try:
                    qn = self.device.quaternion()
                except OSError as err:
                    if self.debug:
                        db.write(str(err))
                    continue
                if qn is None:
                    continue
                else:
                    (qw, qx, qy, qz) = qn
                if self.debug:
                    db.write('Quaternion {} {} {} {}'.format(qw, qx, qy, qz) )
                (heading, roll, pitch) = pi_steer.quaternion.quaternion_to_euler(qw, qx, qy, qz, self.debug)
                if heading is None:
                    continue
                roll -= self.base_roll
                if roll < -180:
                    roll += 360
                if roll > 180:
                    roll -= 360
                if self.debug:
                    db.write('Heading {}, roll {}, pitch {}'.format(heading, roll, pitch) )
                return (heading, roll, pitch)
        elif self.bno085:
            heading, roll, pitch = self.device.get_orientation()
            roll -= self.base_roll
            if roll < -180:
                roll += 360
            if roll > 180:
                roll -= 360
            return (heading, roll, pitch) 

        return None
