import time
import threading
import pi_steer.ads1115
import pi_steer.settings

class WAS():
    def __init__(self, settings) -> None:
        self.settings = settings
        self.angle = 0
        threading.Thread(target=self.reader).start()

    def reader(self):
        ads = pi_steer.ads1115.ADS1115()

        while True:
            # tic = time.time()
            voltage = ads.read()
            # print('Imu read took: ', time.time()-tic, 's.')
            angle = ((voltage - 2.5) / 2.0 * 60.0 * self.settings.settings['countsPerDeg'] / 100.0 + self.settings.settings['steerOffset'])
            if self.settings.settings['invertWas']:
                angle = -angle
            self.angle = angle
            time.sleep(0.01)
