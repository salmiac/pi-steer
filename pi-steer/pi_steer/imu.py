import pi_steer.bno055
import pi_steer.quaternion
import pi_steer.debug as db


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
        self.device = pi_steer.bno055.BNO055(BNO055_ADDRESS0, debug)
        if debug:
            db.write('Imu address and device {} {}'.format(address, self.device) )

    def read(self):
        if self.device:
            qn = None
            try:
                qn = self.device.quaternion()
            except OSError as err:
                if self.debug:
                    db.write(str(err))
            if qn is None:
                return None
            else:
                (qw, qx, qy, qz) = qn
            if self.debug:
                db.write('Quaternion {} {} {} {}'.format(qw, qx, qy, qz) )
            (heading, roll, pitch) = pi_steer.quaternion.quaternion_to_euler(qw, qx, qy, qz, self.debug)
            if heading is None:
                return None
            if self.debug:
                db.write('Heading {}, roll {}, pitch {}'.format(heading, roll, pitch) )
            return (heading, roll, pitch)
        return None
