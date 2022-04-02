import time
import gpiozero

DELAY = 5

relays = []
relay_pins = [4, 10, 9, 11, 5, 6, 21, 20, 16, 7, 24, 18, 15, 14, 0, 1]
for n in range(10):
    relay = gpiozero.DigitalOutputDevice(relay_pins[n], active_high=True, initial_value=False)
    relays.append(relay)
up_down_mode = gpiozero.DigitalInputDevice(20, pull_up=True, active_state=False)

def _section_status(sc, n) -> int:
    return 1 if (1 << n & sc) else 0

class SectionControl():
    def __init__(self) -> None:
        self.up_down_status = 0
        self.up_down_time = 0

    def up_down(self, status) -> None:
        if status != self.up_down_status:
            self.up_down_status = status
            if status:
                relays[8].on()
                relays[9].off()
            else:
                relays[9].on()
                relays[8].off()
            self.up_down_time = time.time()
            return

        if self.up_down_time + DELAY < time.time():
            relays[8].off()
            relays[9].off()

    def update(self, sc) -> None:
        if up_down_mode.value():
            self.up_down(_section_status(sc, 0))
            return
        
        for n in range(10):
            relays[n].value(_section_status(sc, n))
