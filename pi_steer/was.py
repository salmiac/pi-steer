import pi_steer.automation_hat as hat

class WAS():
    def __init__(self, settings):
        self.settings = settings

    def angle(self):
        return (hat.analog1() - 2.5) / 2.0 * 60.0 * self.settings.settings['countsPerDeg'] / 100.0 + self.settings.settings['steerOffset']
