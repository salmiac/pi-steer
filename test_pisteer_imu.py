import pi_steer.imu as imu
import time

while True:
    print('\r H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}'.format(imu.heading, imu.pitch, imu.roll), end='')
    time.sleep(0.5)
