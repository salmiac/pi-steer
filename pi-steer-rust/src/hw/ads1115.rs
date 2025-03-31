use rppal::i2c::I2c;
use std::error::Error;
use std::sync::{Arc, RwLock};
use std::thread;
use std::time::Duration;

/* --- Configuration Bits (Combined into u16) ---
 * Example: Single-shot, Channel 0, FSR ±6.144V, 250 SPS
 *
 * Bit 15:    1 = Begin single conversion
 * Bits 14-12: MUX configuration
 * 100 = AIN0/GND (Channel 0)
 * 101 = AIN1/GND (Channel 1)
 * 110 = AIN2/GND (Channel 2)
 * 111 = AIN3/GND (Channel 3)
 * Bits 11-9:  PGA (Gain) Configuration - FSR (Full-Scale Range)
 * 000 = ±6.144V
 * 001 = ±4.096V
 * 010 = ±2.048V (default)
 * 011 = ±1.024V
 * 100 = ±0.512V
 * 101 = ±0.256V
 * Bit 8:      MODE
 * 1 = Single-shot mode
 * 0 = Continuous conversion mode
 * Bits 7-5:   Data Rate (Samples Per Second)
 * 000 = 8 SPS
 * 001 = 16 SPS
 * 010 = 32 SPS
 * 011 = 64 SPS
 * 100 = 128 SPS (default)
 * 101 = 250 SPS
 * 110 = 475 SPS
 * 111 = 860 SPS
 * Bit 4:      COMP_MODE (Comparator Mode)
 * 0 = Traditional comparator (default)
 * 1 = Window comparator
 * Bit 3:      COMP_POL (Comparator Polarity)
 * 0 = Active low (default)
 * 1 = Active high
 * Bit 2:      COMP_LAT (Latching Comparator)
 * 0 = Non-latching (default)
 * 1 = Latching
 * Bits 1-0:   COMP_QUE (Comparator Queue & Disable)
 * 00 = Assert after one conversion
 * 01 = Assert after two conversions
 * 10 = Assert after four conversions
 * 11 = Disable comparator and set ALERT/RDY pin high impedance (default)
 */

// Base configuration: FSR=±6.144V, Single-Shot, 250SPS, Comparator Disabled
// High byte base (excluding OS and MUX): 0b0XXX_0001 (PGA=000, MODE=1) -> 0x01
// Low byte: 0b1010_0011 (DR=101, COMP_MODE=0, COMP_POL=0, COMP_LAT=0, COMP_QUE=11) -> 0xA3

// --- Constants ---
const ADS111X_ADDRESS0: u16 = 0x48;
const CONVERSION_REGISTER: u8 = 0x00;
const CONFIG_REGISTER: u8 = 0x01;
const CONFIG_PGA_6_144V: u16 = 0b000 << 9;
const CONFIG_MODE_SINGLE: u16 = 0b1 << 8;
const CONFIG_DR_250SPS: u16 = 0b101 << 5;
const CONFIG_COMP_DISABLE: u16 = 0b11;
const FSR_VOLTAGE: f32 = 6.144;
const ROLLING_AVERAGE_SIZE: usize = 4; // Number of samples for rolling average

// ADS1115 struct no longer holds the i2c handle
pub struct ADS1115 {
    data: Arc<RwLock<Vec<Vec<f32>>>>, // Rolling averages for each channel
}

impl ADS1115 {
    // --- Public constructor ---
    pub fn new(channels_mask: u8) -> Result<Self, Box<dyn Error>> {
        // Initialize shared data storage
        let data_arc = Arc::new(RwLock::new(vec![vec![]; 4]));
        let data_clone_for_thread = Arc::clone(&data_arc);
        
        // Spawn the background reader thread
        thread::spawn(move || 
            Self::background_loop(
                data_clone_for_thread, // Clone data Arc for the thread
                channels_mask,
            )
        );

        Ok(ADS1115 {
            data: data_arc, // Store the original data Arc
        })
    }

    // --- Private helper to run the background task ---
    // Takes ownership of the i2c Arc
    fn background_loop(
        data_clone: Arc<RwLock<Vec<Vec<f32>>>>,
        channels_mask: u8,
    )  {
        let mut i2c_handle = I2c::new().expect("Failed to initialize I2C");
        i2c_handle.set_slave_address(ADS111X_ADDRESS0).expect("Failed to set I2C slave address");

        // The loop now uses the 'i2c' Arc it owns
        loop {
            for channel in 0..4 {
                if (channels_mask & (1 << channel)) != 0 {
                    // Perform I2C read (logic is identical, just uses 'i2c' directly)
                    let read_result = {
                        let mux_config: u16 = match channel {
                            0 => 0b100 << 12,
                            1 => 0b101 << 12,
                            2 => 0b110 << 12,
                            3 => 0b111 << 12,
                            _ => 0b100 << 12,
                        };
                        let config: u16 = 0x8000 | mux_config | CONFIG_PGA_6_144V | CONFIG_MODE_SINGLE | CONFIG_DR_250SPS | CONFIG_COMP_DISABLE;
                        let config_bytes = config.to_be_bytes();

                        if let Err(e) = i2c_handle.block_write(CONFIG_REGISTER, &[config_bytes[0], config_bytes[1]]) {
                            eprintln!("[ADS1115 Thread] Error writing config for channel {}: {}", channel, e);
                            continue;
                        }

                        thread::sleep(Duration::from_millis(5)); // Wait

                        let mut read_buffer = [0u8; 2];
                        match i2c_handle.block_read(CONVERSION_REGISTER, &mut read_buffer) {
                            Ok(_) => {
                                let raw_adc = i16::from_be_bytes(read_buffer);
                                let voltage = (raw_adc as f32 / 32767.0) * FSR_VOLTAGE;
                                Ok(voltage)
                            }
                            Err(e) => {
                                eprintln!("[ADS1115 Thread] Error reading channel {}: {}", channel, e);
                                Err(e)
                            }
                        }
                    };

                    // Update shared data
                    if let Ok(voltage) = read_result {
                        let mut data_guard = data_clone.write().expect("Data RwLock poisoned");
                        let channel_data = &mut data_guard[channel as usize];
                        channel_data.push(voltage);
                        if channel_data.len() > ROLLING_AVERAGE_SIZE {
                            channel_data.remove(0);
                        }
                    }
                }
            }
        } // End loop
    } // End thread spawn

    // --- Public method to get voltage ---
    pub fn voltage(&self, channel: u8) -> Option<f32> {
        if channel >= 4 {
             eprintln!("Invalid channel requested: {}", channel);
             return None;
        }
        let data_guard = self.data.read().expect("Data RwLock poisoned");
        let channel_data = &data_guard[channel as usize];

        if channel_data.is_empty() {
            None
        } else {
            let sum: f32 = channel_data.iter().sum();
            Some(sum / channel_data.len() as f32)
        }
    }
}

// --- Test Module ---
#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn ads() {
        println!("Initializing ADS1115...");

        let ads = ADS1115::new(0b0000_0011).expect("Failed to initialize ADS1115");

        println!("Allowing time for initial readings...");
        thread::sleep(Duration::from_millis(100));

        println!("Reading voltages...");
        let voltage0 = ads.voltage(0);
        let voltage1 = ads.voltage(1);
        let voltage2 = ads.voltage(2);
        let voltage3 = ads.voltage(3);

        println!("Channel 0 average voltage: {:?}", voltage0);
        println!("Channel 1 average voltage: {:?}", voltage1);
        println!("Channel 2 average voltage: {:?}", voltage2); // Expected: None
        println!("Channel 3 average voltage: {:?}", voltage3); // Expected: None

        assert!(voltage0.is_some(), "Channel 0 should have readings");
        assert!(voltage1.is_some(), "Channel 1 should have readings");
        assert!(voltage2.is_none(), "Channel 2 should not have readings");
        assert!(voltage3.is_none(), "Channel 3 should not have readings");

        thread::sleep(Duration::from_millis(200));
        println!("Reading voltages again...");
        println!("Channel 0 average voltage: {:?}", ads.voltage(0));
        println!("Channel 1 average voltage: {:?}", ads.voltage(1));
    }
}