import time
import pi_steer.imu
import pi_steer.debug

imu = pi_steer.imu.IMU(False)
print('BNO085', imu.bno085)
print('BNO055', imu.bno055)
while True:
    h, r, p = imu.read()
    print(pi_steer.debug.now(), '{: 3.2f} {: 3.2f} {: 3.2f}'.format(h, r, p), '\r', end='')
    time.sleep(0.02)
