use serde::{Deserialize, Serialize};
use serde_json::Result as JsonResult;
use std::{fs::File, io::Read, io::Write};

#[derive(Debug, Serialize, Deserialize)]
pub struct Settings {
    pub gain_p: u8,
    pub high_pwm: u8,
    pub low_pwm: u8,
    pub min_pwm: u8,
    pub counts_per_deg: u8,
    pub steer_offset: f32,
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
    pub relay_mode: u8,
    pub impulse_seconds: f32,
    pub section_control_enable: bool,
    pub impulse_gpio: Vec<u8>,
    pub relay_gpio: Vec<u8>,
    pub input_gpio: Vec<u8>,
    pub work_switch_gpio: u8,
    pub autosteer_switch_gpio: u8,
    pub pwm_direction: u8,
    pub was: bool,
    pub steer_control: bool,
    pub gps: String,
    pub sprayer_pressure_control: bool,
    pub sprayer_pressure_multiplier: f32,
    pub sprayer_pressure_add: f32,
    pub pressure_control_up_gpio: u8,
    pub pressure_control_down_gpio: u8,
    #[serde(skip)]
    debug: bool,
}

impl Settings {
    pub fn new(debug: bool) -> Self {
        let settings = Settings {
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
            relay_mode: 0,
            impulse_seconds: 4.0,
            section_control_enable: true,
            impulse_gpio: [4, 17].to_vec(),
            relay_gpio: [4, 17, 22, 10, 9, 11, 0, 5, 6, 21].to_vec(),
            input_gpio: [26, 18, 23, 24, 25].to_vec(),
            work_switch_gpio: 13,
            autosteer_switch_gpio: 27,
            pwm_direction: 16,
            was: true,
            steer_control: true,
            gps: "serial0".to_string(),
            sprayer_pressure_control: false,
            sprayer_pressure_multiplier: 2.51,
            sprayer_pressure_add: -1.33,
            pressure_control_up_gpio: 7,
            pressure_control_down_gpio: 8,
            debug,
        };
        settings.load_settings()
    }

    fn load_settings(mut self) -> Self {
        match File::open("settings.json") {
            Ok(mut file) => {
                let mut contents = String::new();
                if let Err(err) = file.read_to_string(&mut contents) {
                    self.log(&format!("Read file error: {}", err));
                    return self;
                }
                let updated_settings: JsonResult<Settings> = serde_json::from_str::<Settings>(&contents);
                match updated_settings {
                    Ok(_json) => {
                        return _json;
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
        return self;
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
            println!("{}", message); // Using the `log` crate's `info!` macro for logging
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