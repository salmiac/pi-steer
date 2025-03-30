use std::error::Error;
// use std::cell::RefCell;
// use std::rc::Rc;
use std::sync::{Arc, Mutex};

use crate::config::settings::Settings;


const MAXANGLE: f32 = 85.0;

pub struct WAS {
    settings: Arc<Mutex<Settings>>,
}

impl WAS {
    pub fn new(settings: Arc<Mutex<Settings>>) -> Result<Self, Box<dyn Error>> {
        Ok(WAS { settings })
    }

    pub fn angle(&mut self, voltage: f32) -> f32 {
        let settings = self.settings.lock().unwrap();
        let mut angle = (voltage - 2.5) / 4.0 * 60.0 * settings.counts_per_deg as f32 / 100.0 + settings.steer_offset;
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
        println!("ADS read: {:?}", was.expect("REASON").angle(2.5));
    }
}
