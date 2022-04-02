import pi_steer.ads1115
import pi_steer.settings
import pi_steer.debug as db

_ADS111X_ADDRESS0 = 0b01001000
_ADS111X_ADDRESS1 = 0b01001001
MAXANGLE = 85

class WAS():
    def __init__(self, settings, debug=False) -> None:
        self.settings = settings
        self.debug = debug
        address = _ADS111X_ADDRESS0
        self.device = None
        if address:
            self.device = pi_steer.ads1115.ADS1115(address, self.debug)

    def read(self):
        if self.device:
            adc = None
            try:
                adc = self.device.read()
            except OSError as err:
                if self.debug:
                    db.write(str(err))
            if adc is None:
                return None
            if self.debug:
                db.write('ADC {}'.format(adc))
            angle = (adc/16383.5 - 1) * 5 / 4.0 * 60.0 * self.settings.settings['countsPerDeg'] / 100.0 + self.settings.settings['steerOffset']
            if self.settings.settings['invertWas']:
                angle = -angle
            if angle < -MAXANGLE:
                angle = -MAXANGLE
            if angle > MAXANGLE:
                angle = MAXANGLE
            if self.debug:
                db.write('Angle {}'.format(angle))
            return angle
        return None
        