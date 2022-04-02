import json
import pi_steer.debug as db

class Settings(): 
    def __init__(self, debug) -> None:
        self.settings = {
            'gainP': 50,
            'highPWM': 120,
            'lowPWM': 30,
            'minPWM': 25,
            'countsPerDeg': 100,
            'steerOffset': 0,
            'ackermanFix': 128,
            'invertWas': 0,
            'steerInvertRelays': 0,
            'invertSteer': 0,
            'conv': 'Single',
            'motorDrive': 'Cytron',
            'steerEnable': 'Switch',
            'encoder': 0,
            'danfoss': 0,
            'pressureSensor': 0,
            'currentSensor': 0,
        }
        self.debug = debug

        try:
            with open('settings.json') as json_file:
                self.settings.update(json.load(json_file))
        except FileNotFoundError:
            if self.debug:
                db.write('Read file error')
            self.save_settings()

    def save_settings(self):
        if self.debug:
            db.write('Save settings')
        try:
            with open('settings.json', 'w') as writer:
                json.dump(self.settings, writer)
        except Exception as err:
            if self.debug:
                db.write(str(err))
        if self.debug:
            db.write('Save settings ok')

