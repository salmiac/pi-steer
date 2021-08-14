from threading import settrace
import pi_steer.was
import time
import pi_steer.settings
import pi_steer.i2c

i2c = pi_steer.i2c.get_i2c()
settings = pi_steer.settings.Settings()
was = pi_steer.was.WAS(settings, i2c)

while True:
    print('\r {: = 7.2f} dedrees'.format(was.angle), end='')
    time.sleep(0.5)
