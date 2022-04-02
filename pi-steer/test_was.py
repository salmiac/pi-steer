import time
import pi_steer.was
import pi_steer.settings

settings = pi_steer.settings.Settings()
was = pi_steer.was.WAS(settings, True)
while True:
    was.read()
    time.sleep(1)
