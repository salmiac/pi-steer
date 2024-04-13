use serialport;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use byteorder::{ByteOrder, LittleEndian};

pub struct BNO08X {
    // debug: bool,
    orientation: Arc<Mutex<(f32, f32, f32, bool)>>,
}

impl BNO08X {
    pub fn new(debug: bool) -> BNO08X {
        let orientation = Arc::new(Mutex::new((0.0, 0.0, 0.0, false)));

        let reader_orientation = Arc::clone(&orientation);

        thread::spawn(move || Self::reader(debug, reader_orientation));
        BNO08X {
            // debug,
            orientation,
        }
    }

    fn reader(debug: bool, orientation: Arc<Mutex<(f32, f32, f32, bool)>>) {
        let port_name = "/dev/ttyS0";
        let baud_rate = 115200;
        if debug { println!("Open serialport") }
        let mut port = serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
            .expect("Failed to open serial port");
        let mut buf0 = [0u8; 1]; // Assuming 18 bytes: 1-byte header + 17 bytes data
        let mut buf = [0u8; 17]; // Assuming 18 bytes: 1-byte header + 17 bytes data
        loop {
            for _n in 1..50 {
                if let Ok(_) = port.read_exact(&mut buf0) {
                    if buf0[0] == 0xaa {
                        if let Ok(_) = port.read_exact(&mut buf0) {
                            if buf0[0] == 0xaa {
                                thread::sleep(Duration::from_millis(2)); // Adjust based on your needs
                                if debug { println!("Header") }
                                if let Ok(length) = port.read(&mut buf) {
                                    if length == 17 {
                                        // index 0
                                        let heading = LittleEndian::read_i16(&buf[1..3]) as f32 / 100.0;
                                        let roll = LittleEndian::read_i16(&buf[3..5]) as f32 / 100.0;
                                        let pitch = LittleEndian::read_i16(&buf[5..7]) as f32 / 100.0;
                                        // acc_x 7..9
                                        // acc_y 9..11
                                        // acc_z 11..13
                                        // mi 13
                                        // mr 14
                                        // res 15
                                        let csum = buf[16];

                                        let crc_sum: u8 = buf[0..16].iter().fold(0u8, |acc, &x| acc.wrapping_add(x));
                                        
                                        if csum == crc_sum {
                                            // Update orientation
                                            let mut ori = orientation.lock().unwrap();
                                            *ori = (heading, roll, pitch, true);
                                            if debug {
                                                println!("Orientation updated: {:?}", *ori);
                                            }
                                        }
                                        else if debug { println!("crc fail: {:02X?}  {:?} - {:?}", buf, csum, crc_sum) }
                                    }
                                    else if debug { println!("only {:?} bytes read", length) }
                                }
                            }
                        }
                        else if debug { println!("Header fail: {:02X?}", buf0) }
                    }
                }
            }
            thread::sleep(Duration::from_millis(1)); // Adjust based on your needs
        }
    }

    pub fn get_orientation(&self) -> (f32, f32, f32, bool) {
        let ori = self.orientation.lock().unwrap();
        *ori
    }
}


#[cfg(test)]
mod tests {
    // use super::*;

    #[test]
    fn bno() {
        // let bno08x = BNO08X::new(true);
        // thread::sleep(Duration::from_millis(100)); // Adjust based on your needs
        // let orientation = bno08x.get_orientation();
        // println!("Current orientation: {:?}", orientation);
    }
}

// fn main() {
//     let debug = true;
//     let bno08x = BNO08X::new(debug);

//     loop {
//         let orientation = bno08x.get_orientation();
//         println!("Current orientation: {:?}", orientation);
//         thread::sleep(Duration::from_secs(1));
//     }
// }
