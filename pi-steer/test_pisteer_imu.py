import time
import pi_steer.imu as imu
import pi_steer.i2c

i2c = pi_steer.i2c.get_i2c()
imu.start(i2c)

while True:
    print('\r H {: = 7.2f} P {: = 7.2f} R {: = 7.2f}    '.format(imu.heading, imu.pitch, imu.roll), end='')
    time.sleep(0.5)
