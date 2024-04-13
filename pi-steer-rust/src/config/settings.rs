use serde::{Deserialize, Serialize};
use serde_json::{Result as JsonResult, Value};
use std::{fs::File, io::Read, io::Write};
use log::{info};

#[derive(Serialize, Deserialize)]
pub struct Settings {
    pub gain_p: u8,
    pub high_pwm: u8,
    pub low_pwm: u8,
    pub min_pwm: u8,
    pub counts_per_deg: u8,
    pub steer_offset: f64,
    pub ackerman_fix: u8,
    pub invert_was: bool,
    pub steer_invert_relays: bool,
    pub invert_steer: bool,
    pub conv: String,
    pub motor_drive: String,
    pub steer_enable: String,
    pub encoder: bool,
    pub danfoss: bool,
    pub pressure_sensor: bool,
    pub current_sensor: bool,
    pub bno085: bool,
    pub relays: bool,
    pub up_down: bool,
    #[serde(skip)]
    debug: bool,
}

impl Settings {
    pub fn new(debug: bool) -> Self {
        let mut settings = Settings {
            gain_p: 50,
            high_pwm: 120,
            low_pwm: 30,
            min_pwm: 25,
            counts_per_deg: 100,
            steer_offset: 0.0,
            ackerman_fix: 128,
            invert_was: false,
            steer_invert_relays: false,
            invert_steer: false,
            conv: "Single".to_string(),
            motor_drive: "Cytron".to_string(),
            steer_enable: "Switch".to_string(),
            encoder: false,
            danfoss: false,
            pressure_sensor: false,
            current_sensor: false,
            bno085: false,
            relays: false,
            up_down: false,
            debug,
        };
        settings.load_settings();
        settings
    }

    fn load_settings(&mut self) {
        match File::open("settings.json") {
            Ok(mut file) => {
                let mut contents = String::new();
                if let Err(err) = file.read_to_string(&mut contents) {
                    self.log(&format!("Read file error: {}", err));
                    return;
                }
                let updated_settings: JsonResult<Value> = serde_json::from_str(&contents);
                match updated_settings {
                    Ok(_json) => {
                        // Assuming manual merging of settings is required. Implement as needed.
                    },
                    Err(err) => self.log(&format!("JSON parse error: {}", err)),
                }
            },
            Err(_) => {
                self.log("Read file error: File not found");
                self.save_settings();
            },
        }
    }

    pub fn save_settings(&mut self) {
        match File::create("settings.json") {
            Ok(mut file) => {
                if let Err(err) = file.write_all(serde_json::to_string(&self).unwrap().as_bytes()) {
                    self.log(&format!("Write file error: {}", err));
                    return;
                }
                self.log("Save settings ok");
            },
            Err(err) => self.log(&format!("Create file error: {}", err)),
        }
    }

    fn log(&self, message: &str) {
        if self.debug {
            info!("{}", message); // Using the `log` crate's `info!` macro for logging
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn settest() {
        let mut s = Settings::new(true);
        s.save_settings();
    }
}