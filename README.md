# PaperDash

PaperDash is a custom Linux kernel driver for SPI-based e-paper displays, designed to work with Raspberry Pi Zero and Waveshare's 7.5-inch e-paper display. The project consists of:
- An **Out-of-Tree (OOB) kernel driver** for handling SPI communication.
- A **daemon** that provides a user-space interface for displaying information such as datetime and weather updates.

## Project Structure
```
PaperDash/
├── driver/       # Kernel module (OOB driver)
│   ├── paperdash.c
│   ├── paperdash.h
│   ├── Makefile
│   ├── Kbuild
│
├── daemon/       # User-space daemon
│   ├── paperdashd.c
│   ├── Makefile
│   ├── config.json
│
├── README.md
```

## Requirements
- Raspberry Pi Zero
- Waveshare 7.5-inch SPI e-paper display
- Linux kernel with SPI support enabled
- GCC toolchain for compiling kernel modules

## Building & Installing the Kernel Driver
1. **Enable SPI on Raspberry Pi**
   ```sh
   sudo raspi-config   # Enable SPI under 'Interfacing Options'
   sudo reboot
   ```
2. **Compile and Load the Kernel Module**
   ```sh
   cd driver
   make
   sudo insmod paperdash.ko
   dmesg | tail -n 10  # Verify module is loaded
   ```
3. **Unload the Module** (if needed)
   ```sh
   sudo rmmod paperdash
   ```

## Running the Daemon
1. **Compile the daemon**
   ```sh
   cd daemon
   make
   ```
2. **Start the daemon**
   ```sh
   sudo ./paperdashd
   ```

## TODO
- Implement SPI communication in the driver
- Support basic display commands (clear screen, draw text/images)
- Add weather and datetime display functionality
- Optimize power consumption

## License
This project is licensed under the MIT License - see the LICENSE file for details.

