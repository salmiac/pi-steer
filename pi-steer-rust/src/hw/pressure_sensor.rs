use std::error::Error;

use crate::hw::ads1115::ADS1115;
use crate::config::settings::Settings;


pub struct PressureSensor {
    device: ADS1115,
    p_multiplier: f32,
    p_add: f32,
}

impl PressureSensor {
    pub fn new(p_multiplier: f32, p_add: f32) -> Result<Self, Box<dyn Error>> {
        let device = ADS1115::new()?;
        Ok(PressureSensor { 
            device, 
            p_multiplier, 
            p_add 
        })
    }

    pub fn read(&mut self) -> f32 {
        let adc = self.device.read(1).unwrap_or(0);
        let settings = self.settings.lock().unwrap();
        adc * self.p_multiplier + self.p_add
    }

}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn wastest() {
        let _pressure_control = PressureControl::new(2.51, -1,33);
        println!("read pressure: {:?}", was.expect("REASON").read());
    }
}
