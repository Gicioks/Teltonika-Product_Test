import argparse
from curses import meta
from modules.exceptions import ModuleInitializeException, ArgumentHandlerException

class ArgHandler:

    __argHandler = None

    def __init__(self) -> None:
        
        if not self.__parse_args():
            raise ModuleInitializeException("Unable to parse arguments")
    
    def __parse_args(self):
        parser = argparse.ArgumentParser()
        # general args
        parser.add_argument("-D", "--device", dest="device", help="Device name", required=True)
        # ssh args
        parser.add_argument("-P", "--port", dest="ssh_port", default=22, help="SSH port", required=False)
        parser.add_argument("-a", "--ip", dest="ssh_ip", default="192.168.1.1", help= "SSH IP", required=False)
        parser.add_argument("-u", "--user", dest="ssh_username", default="root", help="SSH user username", required=False)
        parser.add_argument("-p", "--password", dest="ssh_password", default="Admin123", help="SSH user password", required=False)
        # serial args
        parser.add_argument("-s", "--serial-port", dest="serial_port", default="/dev/ttyUSB2", help="Serial port", required=False)
        parser.add_argument("-b", "--baudrate", dest="serial_baudrate", default=115200, help="Serial baudrate", required=False)
        parser.add_argument("-t" "--timeout", dest="serial_timeout", default=0.5, help="Serial port timeout in seconds", required=False)
        parser.add_argument("-w" "--wait-time", dest="serial_wait", default=1.0, help="Serial port wait time for device response in secons", required=False)

        try:
            self.__argHandler = parser.parse_args()
        except Exception:
            return False

        return True

    def get_args(self):
        if self.__argHandler:
           return self.__argHandler
        else:
            return None

    def print_args(self):
        if self.__argHandler:
            print(self.__argHandler)
    
    ###
    # general args

    def get_device(self):
        if self.__argHandler:
           return self.__argHandler.device.strip()
        else:
            return None

    ###
    # SSH args

    def get_ssh_port(self):
        if self.__argHandler:
            return self.__argHandler.ssh_port
        else:
            return None
    def get_ssh_addr(self):
        if self.__argHandler:
            return self.__argHandler.ssh_ip.strip()
        else:
            return None
    def get_ssh_user(self):
        if self.__argHandler:
            return self.__argHandler.ssh_username.strip()
        else:
            return None
    def get_ssh_password(self):
        if self.__argHandler:
            return self.__argHandler.ssh_password.strip()
        else:
            return None
    
    ###
    # Serial args

    def get_serial_port(self):
        if self.__argHandler:
            return self.__argHandler.serial_port.strip()
        else:
            return None
    def get_serial_baudrate(self):
        if self.__argHandler:
            return self.__argHandler.serial_baudrate
        else:
            return None
    def get_serial_timeout(self):
        if self.__argHandler:
            return self.__argHandler.serial_timeout
        else:
            return None
    def get_serial_wait(self):
        if self.__argHandler:
            return self.__argHandler.serial_wait
        else:
            return None