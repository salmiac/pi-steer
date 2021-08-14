from threading import settrace
import pi_steer.was
import time
import pi_steer.settings

settings = pi_steer.settings.Settings()
was = pi_steer.was.WAS(settings)

while True:
    print('\r {: = 7.2f} dedrees'.format(was.angle), end='')
    time.sleep(0.5)
