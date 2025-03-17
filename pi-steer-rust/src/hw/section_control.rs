use rppal::gpio::{Gpio, OutputPin, InputPin};
use std::time::{Duration, Instant};
use std::sync::{Arc, Mutex};
use std::thread;

const WATCHDOG_TIMOUT: u128 = 2000;

enum RelayMode {
    Off = 0,
    Impulse = 1,
    OnOff = 2,
    Reverse = 3,
}

fn section_status(sc: u16, n: usize) -> bool {
    (1 << n) & sc != 0
}

fn get_input(inputs: &Vec<InputPin>) -> u16 {
    let mut sc = 0x0000;
    for (n, pin) in inputs.iter().enumerate() {
        if pin.is_low() {
            sc = (1 << n) | sc;
        }
    }
    sc
}
pub struct RelayControl {
    impulse_mode_status: Vec<bool>,
    impulse_time: Vec<Instant>,
    pub relay_gpio: Vec<OutputPin>,
    pub input_gpio: Vec<InputPin>,
    mode: RelayMode,
    impulse_seconds: f32,
    pub sections: u16,
    pub work_switch_gpio: InputPin,
}

impl RelayControl {
    pub fn new(mode: u8, impulse_seconds: f32, _relay_gpio: Vec<u8>, _input_gpio: Vec<u8>, work_switch_gpio: u8) -> RelayControl {
        let gpio = Gpio::new().expect("Failed to initialize GPIO");

        let relay_gpio: Vec<OutputPin> = _relay_gpio.iter()
            .map(|&pin| gpio.get(pin).expect("Failed to access GPIO pin").into_output())
            .collect();
    
        let impulse_mode_status: Vec<bool> = (0..relay_gpio.len()/2).into_iter().map(|_| false ).collect();
        let impulse_time: Vec<Instant> = (0..relay_gpio.len()/2).into_iter().map(|_| Instant::now()-Duration::from_secs(10) ).collect();

        RelayControl {
            impulse_mode_status,
            impulse_time,
            relay_gpio,
            mode: match mode {
                x if x == RelayMode::Off as u8 => RelayMode::Off,
                x if x == RelayMode::Impulse as u8 => RelayMode::Impulse,
                x if x == RelayMode::OnOff as u8 => RelayMode::OnOff,
                x if x == RelayMode::Reverse as u8 => RelayMode::Reverse,
                _ => RelayMode::Off
            },
            impulse_seconds,
            sections: 0x0000,
            work_switch_gpio: gpio.get(work_switch_gpio).unwrap().into_input_pullup(),
            input_gpio: _input_gpio.iter()
                .map(|&pin| gpio.get(pin).expect("Failed to access GPIO pin").into_input_pullup())
                .collect(),
        }
    }

    fn get_sections(&mut self, manual: bool) -> u16 {
        let work_switch = self.work_switch_gpio.is_low();
        let mut sc = self.sections;
        let manual_sc = get_input(&self.input_gpio);
        if ! work_switch {
            sc = 0;
        }
        else {
            sc = sc & manual_sc;
        }
        if manual {
            sc = manual_sc;
        }
        sc
    }

    pub fn impulse(&mut self, manual: bool) {
        let sc = self.get_sections(manual);
        
        for n in 0..self.relay_gpio.len()/2 {
            let status = section_status(sc, n);
            if self.impulse_mode_status[n] != status {
                self.impulse_mode_status[n] = status;
                if status {
                    self.relay_gpio[n*2].set_high();
                    self.relay_gpio[n*2+1].set_low();
                } else {
                    self.relay_gpio[n*2].set_low();
                    self.relay_gpio[n*2+1].set_high();
                }
                self.impulse_time[n] = Instant::now();
                continue;
            }

            if self.impulse_time[n].elapsed() > Duration::from_millis((self.impulse_seconds*1000.0) as u64) {
                self.relay_gpio[n*2].set_low();
                self.relay_gpio[n*2+1].set_low();
            }
    
        }
    }

    pub fn relays_on_off(&mut self, manual: bool) {
        let sc = self.get_sections(manual);
        for n in 0..16 {
            if section_status(sc, n) {
                self.relay_gpio[n].set_low();
            } else {
                self.relay_gpio[n].set_high();
            }
        }
    }

    pub fn relays_reverse(&mut self,  manual: bool) {
        let sc = self.get_sections(manual);
        for n in 0..self.relay_gpio.len()/2 {
            if section_status(sc, n) {
                self.relay_gpio[n*2].set_low();
                self.relay_gpio[n*2+1].set_high();
            } else {
                self.relay_gpio[n*2].set_high();
                self.relay_gpio[n*2+1].set_low();
            }
        }
    }

    pub fn all_off(&mut self) {
        for relay in self.relay_gpio.iter_mut() {
            relay.set_high();
        }
    }

}
pub struct SectionControl {
    watchdog_timer: Arc<Mutex<Instant>>,
    pub rc: Arc<Mutex<RelayControl>>,
}

impl SectionControl {
    pub fn new(
            relay_mode: u8, 
            impulse_seconds: f32, 
            relay_gpio: Vec<u8>, 
            input_gpio: Vec<u8>,
            work_switch: u8,
            manual_mode_gpio: u8
        ) -> rppal::gpio::Result<SectionControl> {
        let watchdog_timer = Arc::new(Mutex::new(Instant::now()));
        println!("Relay mode {}", relay_mode);
        let rc = Arc::new(Mutex::new(RelayControl::new(relay_mode, impulse_seconds, relay_gpio, input_gpio, work_switch)));

        let watchdog_clone = Arc::clone(&watchdog_timer);
        let rc_clone = Arc::clone(&rc);
        thread::spawn(move || Self::watchdog(watchdog_clone, rc_clone, manual_mode_gpio));
        Ok(SectionControl {
            watchdog_timer,
            rc,
        })
    }

    fn watchdog(timer: Arc<Mutex<Instant>>, relays_arc: Arc<Mutex<RelayControl>>, manual_mode_gpio: u8) {
        let gpio = Gpio::new().expect("Failed to initialize GPIO");
        let manual = gpio.get(manual_mode_gpio).expect("Failed to access GPIO pin").into_input_pullup();
        loop {
            let watchdog_timer = timer.lock().unwrap();
            let timeout = watchdog_timer.elapsed().as_millis() > WATCHDOG_TIMOUT;
            drop(watchdog_timer);
            let is_manual = manual.is_low();
            let mut rc = relays_arc.lock().unwrap();
            if timeout && ! is_manual {
                // Shutdown all relays
                rc.all_off();
            }
            else {
                match rc.mode {
                    RelayMode::OnOff => {
                        rc.relays_on_off(is_manual)
                    },
                    RelayMode::Impulse => rc.impulse(is_manual),
                    RelayMode::Reverse => {
                        rc.relays_reverse(is_manual)
                    },
                    RelayMode::Off => {
                    },
                };
            }
            drop(rc);

            thread::sleep(Duration::from_millis(4));
        }        
    }

    pub fn update(&mut self, sc: u16) {
        let mut rc = self.rc.lock().unwrap();
        rc.sections = sc;
        drop(rc);
        let mut watchdog_timer = self.watchdog_timer.lock().unwrap();
        *watchdog_timer = Instant::now();
    }
}

#[cfg(test)]
mod section_control {
    use super::*;

    #[test]
    fn section() {
        let relay_gpio: Vec<u8> = [4, 17, 22, 10, 9, 11, 0, 5, 6, 21].to_vec();
        let input_gpio: Vec<u8> = [26, 18, 23, 24, 25].to_vec();
        let mut section_control = SectionControl::new(3, 2.0, relay_gpio, input_gpio, 13, 19).unwrap();
        // Simulate an update call with some status code `sc`
        section_control.update(0b1010101010101010); // Example SC value
        thread::sleep(Duration::from_millis(500));
    }
}
