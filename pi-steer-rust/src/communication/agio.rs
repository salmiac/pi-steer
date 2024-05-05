use std::net::UdpSocket;
use std::thread;
use std::time::Duration;
use byteorder::{ByteOrder, LittleEndian};
use std::sync::{Arc, Mutex};

use crate::hw::motor::MotorControl;
use crate::hw::section_control::SectionControl;
use crate::config::settings::Settings;

const HELLO: u8 = 0xc7;
const LATLON: u8 = 0xd0;
const AGIOTRAFFIC: u8 = 0xd2;
const IMU: u8 = 0xd3;
const IMU_DETACH_REQ: u8 = 0xd4;
const NMEA_BYTES: u8 = 0xd5;
const SWITCH_CONTROL: u8 = 0xea;
const MACHINE_CONFIG: u8 = 0xee;
const RELAY_CONFIG: u8 = 0xec;
const MACHINE_DATA: u8 = 0xef;
const STEER_CONFIG: u8 = 0xfb;
const STEERSETTINGS: u8 = 0xfc;
const FROM_AUTOSTEER: u8 = 0xfd;
const AUTOSTEER_DATA: u8 = 0xfe;

pub struct Writer {
    client: UdpSocket,
    is_imu: bool,
    debug: bool,
}

impl Writer {
    pub fn new(is_imu: bool, debug: bool) -> Writer {
        let client = UdpSocket::bind("0.0.0.0:0").unwrap();
        client.set_broadcast(true).unwrap();
        println!("Start Writer, IMU {}", is_imu);
        Writer{
            client,
            is_imu,
            debug,
        }
    }

    pub fn from_autosteer(&self, wheel_angle: f64, heading: f32, roll: f32, switch: u8, pwm_value: f64) {
        let mut data = vec![0x80, 0x81, 0x7e, 0xfd, 0x08];
        
        let pwm_display = (pwm_value * 2.55) as u8;
        let wheel_angle_int = (wheel_angle * 100.0) as i16;
        let mut heading_int = ((heading * 10.0) as i16) as u16;
        let mut roll_int = ((roll * 10.0) as i16) as u16;
        if ! self.is_imu {
            heading_int = 9999;
            roll_int = 8888;
        }

        let mut buf = [0; 2];
        LittleEndian::write_i16(&mut buf, wheel_angle_int);
        data.extend_from_slice(&buf);
        LittleEndian::write_u16(&mut buf, heading_int);
        data.extend_from_slice(&buf);
        LittleEndian::write_u16(&mut buf, roll_int);
        data.extend_from_slice(&buf);

        data.push(switch);
        data.push(pwm_display);

        let crc: u8 = data.iter().skip(2).fold(0, |acc, &x| acc.wrapping_add(x));
        data.push(crc);

        match self.client.send_to(&data, "255.255.255.255:9999") {
            Ok(_) => (),
            Err(e) => if self.debug {
                println!("Send error: {:?}", e);
            },
        }
    }

    pub fn gps(&self, _time: &str, lat: f64, ns: &str, lon: f64, ew: &str, fix: u8, sat: u16, hdop: f32, alt: f32, _geoid: &str, age: f32, heading: f32, speed: f32) {
        let mut data: Vec<u8> = vec![0x80, 0x81, 0x7c, 0xd6, 51 as u8];
        let mut buf8 = [0; 8];
        let mut buf4 = [0; 4];
        let mut buf2 = [0; 2];
        let mut longitude = lon;
        if ew == "W" { longitude = -longitude; }
        let mut latitude = lat;
        if ns == "S" { latitude = -latitude; }
        LittleEndian::write_f64(&mut buf8, longitude);
        data.extend_from_slice(&mut buf8);
        LittleEndian::write_f64(&mut buf8, latitude);
        data.extend_from_slice(&mut buf8);
        LittleEndian::write_f32(&mut buf4, f32::MAX); // dual antenna heading
        data.extend_from_slice(&mut buf4);
        LittleEndian::write_f32(&mut buf4, heading); // single antenna heading
        data.extend_from_slice(&mut buf4);
        LittleEndian::write_f32(&mut buf4, speed); // Speed
        data.extend_from_slice(&mut buf4);
        LittleEndian::write_f32(&mut buf4, f32::MAX); // Roll
        data.extend_from_slice(&mut buf4);
        LittleEndian::write_f32(&mut buf4, alt); // Altitude
        data.extend_from_slice(&mut buf4);
        LittleEndian::write_u16(&mut buf2, sat); // Satellites
        data.extend_from_slice(&mut buf2);
        data.push(fix); //Fix
        LittleEndian::write_u16(&mut buf2, (hdop * 100.0) as u16); // HDOP
        data.extend_from_slice(&mut buf2);
        LittleEndian::write_u16(&mut buf2, (age * 100.0) as u16); // Age
        data.extend_from_slice(&mut buf2);
        LittleEndian::write_u16(&mut buf2, u16::MAX); // IMU heading
        data.extend_from_slice(&mut buf2);
        LittleEndian::write_i16(&mut buf2, i16::MAX); // IMU roll
        data.extend_from_slice(&mut buf2);
        LittleEndian::write_i16(&mut buf2, i16::MAX); // IMU pitch
        data.extend_from_slice(&mut buf2);
        LittleEndian::write_i16(&mut buf2, i16::MAX); // IMU yaw
        data.extend_from_slice(&mut buf2);
        let crc: u8 = data.iter().skip(2).fold(0, |acc, &x| acc.wrapping_add(x));
        data.push(crc);

        match self.client.send_to(&data, "255.255.255.255:9999") {
            Ok(_) => (),
            Err(e) => if self.debug {
                println!("Send error: {:?}", e);
            },
        }
    }

    // fn send_heartbeat(client: &UdpSocket) -> std::io::Result<()> {
    //     let heartbeat_message = [0x80, 0x81, 0x7f, HELLO as u8, 1, 0, 0x47];
    //     let broadcast_addr = SocketAddrV4::new(Ipv4Addr::BROADCAST, 9999);
    //     client.send_to(&heartbeat_message, broadcast_addr)?;
    //     println!("Heartbeat message sent.");
    //     Ok(())
    // }
    
}

pub struct Reader {
    motor: Arc<Mutex<MotorControl>>,
    settings: Arc<Mutex<Settings>>,
    pub sc: SectionControl,
    debug: bool,
}

impl Reader {
    pub fn new(settings: Arc<Mutex<Settings>>, motor: Arc<Mutex<MotorControl>>, debug: bool) -> Reader {
        let set_lock = settings.lock().unwrap();
        println!("Relay mode reader {}", set_lock.relay_mode);
        let sc = SectionControl::new(set_lock.relay_mode, set_lock.impulse_seconds, set_lock.impulse_gpio.clone(), set_lock.relay_gpio.clone(), set_lock.input_gpio.clone(), set_lock.work_switch ).unwrap();
        drop(set_lock);
        Reader { 
            motor, 
            settings: Arc::clone(&settings), 
            sc,
            debug 
        }
    }

    pub fn start(self) {
        let server = UdpSocket::bind("0.0.0.0:8888").unwrap();
        server.set_broadcast(true).unwrap();
        server.set_nonblocking(true).unwrap();

        let agio_arc = Arc::new(Mutex::new(self));
        let agio_clone = Arc::clone(&agio_arc);
    
        // Reader thread to listen for incoming messages
        let _reader_thread = thread::spawn(move || loop {
            let mut buf = [0u8; 1024];
            match server.recv_from(&mut buf) {
                Ok((size, _addr)) => {
                    if size >= 6 {
                        let mut _agio = agio_clone.lock().unwrap();
                        _agio.decode_data(&buf[..size]);
                    }
                },
                Err(e) if e.kind() != std::io::ErrorKind::WouldBlock => {
                    eprintln!("Read socket error: {:?}", e);
                    break;
                },
                _ => {}
            }
            thread::sleep(Duration::from_millis(1));
        });
    }

    fn decode_data(&mut self, data: &[u8]) -> Option<()> {
        if data.len() < 6 {
            return None; // Early return if data is too short for a valid message.
        }

        let source = data[2];
        let pgn = data[3];
        let length = data[4] as usize;

        if data.len() < length + 6 { return None; } // Check if the length is valid.

        let crc = data[5 + length];
        let crc_sum: u8 = data[2..length + 5].iter().fold(0u8, |acc, &x| acc.wrapping_add(x));

        let crc_ok = crc == crc_sum;

        // Use debug_write for debug messages, assuming it's a stand-in for the db.write function.
        if self.debug && pgn != 0xfe && pgn != 0xef && pgn != 0xfd {
            let crc_text = if crc_ok { "CRC Ok." } else { "CRC failed." };
            println!("From: {} | PGN: {} | CRC: {}", source, pgn, crc_text);
        }

        if !crc_ok {
            return None;
        }

        self.pgn_handler(pgn, &data[5..5 + length]);

        Some(())
    }

    fn pgn_handler(&mut self, pgn: u8, data: &[u8]) {
        match pgn {
            HELLO => {},
            LATLON => {},
            AGIOTRAFFIC => {}
            IMU => {},
            IMU_DETACH_REQ => {},
            NMEA_BYTES => {},
            SWITCH_CONTROL => {},
            MACHINE_CONFIG => {},
            RELAY_CONFIG => {},
            MACHINE_DATA => {
                // let uturn = data[0];
                // let speed = data[1] as f64 / 10.0;
                // let hyd_lift = data[2];
                // let tram = data[3];
                // let geo_stop = data[4];
                let sc = LittleEndian::read_u16(&data[6..8]);
        
                if self.debug {
                    println!("machine data");
                }
                self.sc.update(sc);
            },
            STEER_CONFIG => {
                let mut settings = self.settings.lock().unwrap();
                // let set0 = data[0];
                settings.invert_was = data[0] & 1 == 1;
                settings.steer_invert_relays = data[0] >> 1 & 1 == 1;
                settings.invert_steer = data[0] >> 2 & 1 == 1;
                settings.conv = if data[0] >> 3 & 1 == 1 { "Single".to_string() } else { "Differential".to_string() };
                settings.motor_drive = if data[0] >> 4 & 1 == 1 { "Cytron".to_string() } else { "IBT2".to_string() };
                settings.steer_enable = if data[0] >> 5 & 1 == 1 { "Switch".to_string() } else { if data[0] >> 6 & 1 == 1 { "Button".to_string() } else { "None".to_string() } };
                settings.encoder = data[0] >> 7 & 1 == 1;
                // let pulse_count = data[1];
                // let min_speed = data[2];
                // let sett1 = data[3];
                settings.danfoss = data[3] & 1 == 1;
                settings.pressure_sensor = data[3] >> 1 & 1 == 1;
                settings.current_sensor = data[3] >> 2 & 1 == 1;
        
                if self.debug {
                    println!("steer config");
                }
                settings.save_settings();
            },
            STEERSETTINGS => {
                let mut settings = self.settings.lock().unwrap();
                settings.gain_p = data[0];
                settings.high_pwm = data[1];
                settings.low_pwm = data[2];
                settings.min_pwm = data[3];
                settings.counts_per_deg = data[4];
                settings.steer_offset = LittleEndian::read_i16(&data[5..7]) as f64 / 100.0;
                settings.ackerman_fix = data[7];

                if self.debug {
                    println!("steer settings");
                }
                settings.save_settings();
            },
            FROM_AUTOSTEER => {},
            AUTOSTEER_DATA => {
                // let speed = LittleEndian::read_u16(&data[0..2]) as f64 / 10.0;
                let status = data[2];
                let steer_angle = LittleEndian::read_i16(&data[3..5]) as f64 / 100.0;
                let sc = LittleEndian::read_u16(&data[6..8]);

                if self.debug {
                    println!("autosteer data");
                    println!("SC: {:#018b}, steer angle: {}", sc, steer_angle);
                }
                let mut motor = self.motor.lock().unwrap();
                motor.set_control(steer_angle, status != 0);
                drop(motor);
                self.sc.update(sc);
            },
            _ => (),
        }
    }

}

#[test]
fn settest() {

}
