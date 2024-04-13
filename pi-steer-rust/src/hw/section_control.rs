// use std::sync::{Mutex, Arc};
use rppal::gpio::{Gpio, OutputPin, InputPin};
// use std::thread;
use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};
use std::thread;

use crate::config::settings::Settings;

const DELAY: u64 = 5;
const RELAY_PINS: [u8; 18] = [22, 10, 9, 11, 0, 5, 6, 21, 20, 1, 7, 8, 25, 24, 23, 18, 4, 17];
const WATCHDOG_TIMOUT: u128 = 1000;


fn section_status(sc: u16, n: usize) -> bool {
    (1 << n) & sc != 0
}

struct RelayControl {
    up_down_status: bool,
    up_down_time: Instant,
    relays: Vec<OutputPin>,
}

impl RelayControl {
    pub fn new() -> RelayControl {
        let gpio = Gpio::new().expect("Failed to initialize GPIO");

        RelayControl {
            up_down_status: false,
            up_down_time: Instant::now()-Duration::from_secs(10),
            relays: RELAY_PINS.iter()
                .map(|&pin| gpio.get(pin).expect("Failed to access GPIO pin").into_output())
                .collect(),
        }
    }

    pub fn up_down(&mut self, status: bool) {
        // let up_down_status = UP_DOWN_STATUS.lock().unwrap();
        // let up_down_time = UP_DOWN_TIME.lock().unwrap();
        
        if status != self.up_down_status {
            self.up_down_status = status;
            if status {
                self.relays[16].set_high();
                self.relays[17].set_low();
            } else {
                self.relays[17].set_high();
                self.relays[16].set_low();
            }
            self.up_down_time = Instant::now();
            return;
        }

        if self.up_down_time.elapsed() > Duration::from_secs(DELAY) {
            self.relays[16].set_low();
            self.relays[17].set_low();
        }
    }

    pub fn relays_set(&mut self, sc: u16, work_switch: bool) {
        for n in 0..16 {
            if work_switch && section_status(sc, n) {
                self.relays[n].set_high();
            } else {
                self.relays[n].set_low();
            }
        }
    }

    pub fn all_off(&mut self) {
        for relay in self.relays.iter_mut() {
            relay.set_low();
        }
    }

}
pub struct SectionControl {
    settings: Arc<Mutex<Settings>>,
    watchdog_timer: Arc<Mutex<Instant>>,
    work_switch: InputPin,
    rc: Arc<Mutex<RelayControl>>,

    //     relays: Vec<OutputPin>,
//     up_down_mode: InputPin,
//     normal_mode: InputPin,
//     up_down_status: bool,
//     up_down_time: Option<Instant>,
}

// static UP_DOWN_MODE: Lazy<InputPin> = Lazy::new(|| GPIO.get(26).expect("Failed to access GPIO pin").into_input_pullup());
// static NORMAL_MODE: Lazy<InputPin> = Lazy::new(|| GPIO.get(19).expect("Failed to access GPIO pin").into_input_pullup());
// static mut UP_DOWN_STATUS: Lazy<Mutex<bool>> = Lazy::new(|| Mutex::new(false));
// static mut UP_DOWN_TIME: Lazy<Mutex<Option<Instant>>> = Lazy::new(|| Mutex::new(None));

impl SectionControl {
    pub fn new(settings: Arc<Mutex<Settings>>) -> rppal::gpio::Result<SectionControl> {
    //     let gpio = Gpio::new()?;
    //     let relays = RELAY_PINS.iter()
    //         .map(|&pin| gpio.get(pin).unwrap().into_output())
    //         .collect::<Vec<OutputPin>>();
    //     let up_down_mode = gpio.get(26)?.into_input_pullup();
    //     let normal_mode = gpio.get(19)?.into_input_pullup();

        let gpio = Gpio::new().expect("Failed to initialize GPIO");
        
        let watchdog_timer = Arc::new(Mutex::new(Instant::now()));
        let rc = Arc::new(Mutex::new(RelayControl::new()));

        let watchdog_clone = Arc::clone(&watchdog_timer);
        let rc_clone = Arc::clone(&rc);
        thread::spawn(move || Self::watchdog(watchdog_clone, rc_clone));
        Ok(SectionControl {
    //         relays,
    //         up_down_mode,
    //         normal_mode,
    //         up_down_status: false,
    //         up_down_time: None,
            settings: Arc::clone(&settings),
            watchdog_timer,
            work_switch: gpio.get(13).unwrap().into_input_pullup(),
            rc,
        })
    }

    fn watchdog(timer: Arc<Mutex<Instant>>, relays_arc: Arc<Mutex<RelayControl>>) {
        loop {
            let watchdog_timer = timer.lock().unwrap();
            let timeout = watchdog_timer.elapsed().as_millis() > WATCHDOG_TIMOUT;
            drop(watchdog_timer);
            if timeout {
                let mut relays = relays_arc.lock().unwrap();
                // Shutdown all relays
                relays.all_off();
            }
            thread::sleep(Duration::from_millis(100));
        }        
    }

    pub fn update(&mut self, sc: u16) {
        let work_switch = self.work_switch.is_low();
        let settings = self.settings.lock().unwrap();
        let mut rc = self.rc.lock().unwrap();
        if settings.up_down {
            rc.up_down(work_switch && section_status(sc, 0));
        }
        if settings.relays {
            rc.relays_set(sc, work_switch);
        }
        drop(rc);
        let mut watchdog_timer = self.watchdog_timer.lock().unwrap();
        *watchdog_timer = Instant::now();
    }
}

#[cfg(test)]
mod tests {
    // use super::*;

    // #[test]
    // fn section() {
    //     let mut section_control = SectionControl::new();
    //     // Simulate an update call with some status code `sc`
    //     section_control.update(0b1010101010101010); // Example SC value

    // }
}
