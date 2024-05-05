use std::error::Error;
// use std::cell::RefCell;
// use std::rc::Rc;
use std::sync::{Arc, Mutex};

use crate::hw::ads1115::ADS1115;
use crate::config::settings::Settings;


const MAXANGLE: f64 = 85.0;

pub struct WAS {
    settings: Arc<Mutex<Settings>>,
    device: ADS1115,
}

impl WAS {
    pub fn new(settings: Arc<Mutex<Settings>>) -> Result<Self, Box<dyn Error>> {
        let device = ADS1115::new()?;
        Ok(WAS { settings, device })
    }

    pub fn read(&mut self) -> f64 {
        let adc = self.device.read().unwrap_or(0);
        let settings = self.settings.lock().unwrap();
        let mut angle = (adc as f64 / 16383.5 - 1.0) * 5.0 / 4.0 * 60.0 * settings.counts_per_deg as f64 / 100.0 + settings.steer_offset;
        if settings.invert_was {
            angle = -angle;
        }
        drop(settings);
        angle = angle.clamp(-MAXANGLE, MAXANGLE);
        angle
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wastest() {
        let settings = Arc::new(Mutex::new(Settings::new(true)));
        let was = WAS::new(Arc::clone(&settings));
        println!("ADS read: {:?}", was.expect("REASON").read());
    }
}
