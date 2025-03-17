import time
import gpiozero

DELAY = 5

relays = []
relay_pins = [22, 10, 9, 11, 0, 5, 6, 21, 20, 1, 7, 8, 25, 24, 23, 18, 4, 17]

for n in range(18):
    relay = gpiozero.DigitalOutputDevice(relay_pins[n], active_high=True, initial_value=False)
    relays.append(relay)
up_down_mode = gpiozero.DigitalInputDevice(26, pull_up=True)
normal_mode = gpiozero.DigitalInputDevice(19, pull_up=True)

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
                relays[16].on()
                relays[17].off()
            else:
                relays[17].on()
                relays[16].off()
            self.up_down_time = time.time()
            return

        if self.up_down_time + DELAY < time.time():
            relays[16].off()
            relays[17].off()

    def update(self, sc) -> None:
        if up_down_mode.value:
            self.up_down(_section_status(sc, 0))
            return
        if normal_mode.value:
            for n in range(10):
                if _section_status(sc, n):
                    relays[n].on()
                else:
                    relays[n].off()
