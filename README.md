# Product modem test program
Program that tests Qualtec EC25 modem using AT commands of these device series:
- RTXxx
- TRM2xx
- RUT9xx

Run program as sudo with parameters: `sudo python3 ./main.py -D {device}`. For more information run `python3 ./main -h`
Program tests any device from device list in config file when given parameter -D, for example: `sudo python3 ./main.py -D RUTX11`.

Note: the device must defined in config file. 
Config JSON file [example](config.json). 

It connects to device via SSH or Serial Port and tests modem using AT commands.
The program reads all data of a given device from config file and other arguments (or default argument values) if such device exists. 
A connection is established if given parameters are correct (serial port device, SSH port, IP address, auth credentials, etc.) and if the device is connected and avaliable

Note: when connecting to devices via serial port, first turn off Modem Manager service by executing comman in terminal: `sudo systemctl stop ModemManager`

Default flag values:
- General flags:
  - parser.add_argument("-D", "--device", dest="device", help="Device name", required=True)
- SSH flags:
  - SSH port: (`-P | --port`) default = `22`
  - SSH IP address: (`-a" | --ip`) default = `'192.168.1.1'`
  - SSH user username: (`-u | --user`) default = `'root'`
  - SSH user password: (`-p | --password`) default=`'Admin123'`
- Serial port flags:
  - Serial port: (`-s | --serial-port`) default = `'/dev/ttyUSB2'`
  - Serial baudrate: (`-b" | --baudrate`) default = `115200`
  - Serial port timeout in seconds: (`-t | --timeout`) default = `0.5`
