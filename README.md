# Teltonika Qualtec EC25 modem tester
Program tests any device from device list in config file when given parameter -D, for example: `sudo python3 ./main.py -D RUTX11`.

Note: the device must defined in config file. 
Config JSON file [example](config.json). 

It connects to device via SSH or Serial Port and tests modem using AT commands.
The program reads all data of a given device from config file and other arguments (or default argument values) if such device exists. 
A connection is established if given parameters are correct (serial port device, SSH port, IP address, auth credentials, etc.) and if the device is connected and is avaliable.

Program tests if given commands' return value is as axpected (_see config file [example](config.json)_) and forms result file. Some commands may return multiple lines (executing multiple arguments) and may take up to 180s to test, if command does not return expected result under 180s then it is consider that command failed.

Example result file:

![image](https://user-images.githubusercontent.com/61172051/162189209-e097bd29-520f-4a30-a07c-be6fc9f19296.png)

Example program output:

![image](https://user-images.githubusercontent.com/61172051/162190345-a8d60a15-abbb-4463-9378-a063a81c5d28.png)

## Setup
Install Python 3.9.x with pip:
```
sudo apt update
sudo apt install python3.9 python3-pip
```
Install listed packages:

- [PySerial](https://pyserial.readthedocs.io/)
- [Paramiko](https://docs.paramiko.org/)
- [reprint](https://github.com/Yinzo/reprint)
```
pip3 install pyserial
pip3 install paramiko
pip3 install reprint
```

Program that tests Qualtec EC25 modem using AT commands of these device series:
- RTXxx
- TRM2xx
- RUT9xx

## Usage
Run program as sudo with parameters: `sudo python3 ./main.py -D {device}`. For more information run `python3 ./main -h`

Note: when connecting to devices via serial port, first turn off Modem Manager service by executing comman in terminal: `sudo systemctl stop ModemManager`

## Flags
Default flag values:
- General flags:
  - Device name: (`-D", "--device`) no default value, **the device must be specified by the user**.
- SSH flags:
  - SSH port: (`-P | --port`) default value - `22`
  - SSH IP address: (`-a" | --ip`) default value - `'192.168.1.1'`
  - SSH user username: (`-u | --user`) default value - `'root'`
  - SSH user password: (`-p | --password`) default value - `'Admin123'`
- Serial port flags:
  - Serial port: (`-s | --serial-port`) default value - `'/dev/ttyUSB2'`
  - Serial baudrate: (`-b" | --baudrate`) default value - `115200`
  - Serial port timeout in seconds: (`-t | --timeout`) default value - `0.5`
