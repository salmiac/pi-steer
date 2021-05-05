import json

class Settings(): 
    def __init__(self):
        self.settings = {
            'gainP': 50,
            'highPWM': 120,
            'lowPWM': 30,
            'minPWM': 25,
            'countsPerDeg': 100,
            'steerOffset': 0,
            'ackermanFix': 128
        }

        try:
            with open('settings.json') as json_file:
                self.settings = json.load(json_file)
        except FileNotFoundError:
            self.save_settings()

    def save_settings(self):
        try:
            with open('settings.json', 'w') as writer:
                json.dump(self.settings, writer)
        except:
            pass

