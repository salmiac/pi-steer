
curl https://sh.rustup.rs -sSf | sh

sudo apt-get install libudev-dev

sudo usermod -a -G dialout $USER

# build
cargo build

# Run unit tests
cargo test

cargo test -- --nocapture
