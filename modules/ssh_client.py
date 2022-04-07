from time import sleep
import paramiko
from modules.exceptions import SSHConnectionException, SSHRetryException
from modules.console_printer import ConsolePrinter

class SshHandler:

    __ssh_client = None
    __shell = None
    __device = None
    __error_printer = None

    def __init__(self, config, args):
        addr = args.get_ssh_addr()
        username = args.get_ssh_user()
        password = args.get_ssh_password()
        port = args.get_ssh_port()
        self.__device = config.get_param("device")
        self.__error_printer = ConsolePrinter(1)
        if not self.__open_connection(addr, username, password, port):
            raise SSHConnectionException("Unable to connect to SSH server")

        self.__clear_shell()
        self.__stop_GSMD()
        self.__start_socat()
        self.__print()

    ###
    # Connection operations

    def __open_connection(self, addr, username, password, port):
        success = False
        counter = 0
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        while counter <= 5 and not success:
            counter += 1
            try:
                client.connect(addr, port, username, password, auth_timeout=10, timeout=10)
                self.__ssh_client = client
                self.__shell = self.__ssh_client.invoke_shell()

                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Unable to connect to SSH server, retrying... " + str(counter)))
                    sleep(1)
        
        return success

    def __close_connection(self):
        if self.__ssh_client:
            self.__ssh_client.close()

    ###
    # read/write operations

    def __read_shell(self, expects=None):
        success = False
        counter = 0
        while counter <= 5 and not success:
            counter += 1

            try:
                buffer = []
                if expects is not None:
                    buffer = self.__read_AT(expects)
                else:
                    msWait = 0
                    while (msWait <= 50 and not self.__shell.recv_ready):
                        msWait += 1
                        sleep(0.1)
                    self.__shell.recv(nbytes=2147483647)
                
                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Could not read shell, retrying... " + str(counter)))
                    sleep(1)
                else:
                    return None


        return buffer

    def __read_AT(self, expects):
        buffer = ""
        bufferList = []
        isRead = False

        msWaiting = 0
        while(msWaiting <= 180000 and not isRead):
            msWaiting += 1
            if self.__shell.recv_ready():
                bufferNew = self.__shell.recv(nbytes=2147483647).decode()
                if buffer != bufferNew:
                    buffer += bufferNew

                    bufferList = buffer.splitlines()
                    if len(bufferList) > 0:
                        if len(bufferList[0]) > 0:
                            bufferList = bufferList[1::2]
                        else:
                            bufferList = bufferList[::2]

                        lastLine = self.__get_last_line(bufferList).strip()
                        if self.__check_response(lastLine, expects):
                            isRead = True
            sleep(0.01)

        return bufferList

    def __write_shell(self, str):
        # self.__clear_buffer()

        success = False
        counter = 0
        while counter <= 5 and not success:
            counter += 1

            try:
                self.__shell.send(str + "\r")
                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Could not write to shell, retrying... " + str(counter)))
                    sleep(1)

        return success

    ### 
    # String operations

    # Get last line of line list
    def __get_last_line(self, lines:list[str]):
        lastLine = ""
        if lines is not None:
            if lines.__len__() > 0:
                lastLine = lines.__getitem__(lines.__len__() - 1)
        else:
            return None

        return lastLine

    def __get_first_line(self, lines:list[str]):
        firstLine = None
        if lines.__len__() > 1 and lines:
            firstLine = lines.__getitem__(1)

        return firstLine

    # Check if line is valid
    def __check_line(self, line:str):
        if line is None:
            return False
        elif line.__len__() == 0:
            return False
        
        return True
    
    # Check response with expected response
    def __check_response(self, line:str, response:str):
        if self.__check_line(line) and line.lower().startswith(response.lower()):
            return True

        return False

    ###
    # Command operations

    def exec_command(self, command, expects, arguments=None):
        success = True
        response = None

        if not self.__write_shell(command):
            raise SSHConnectionException("Connection to SSH server lost")

        if arguments:
            for index, arg in enumerate(arguments):
                sleep(0.5)
                # If last arg
                if index + 1 == len(arguments):
                    if not self.__write_shell(arg + "\x1a"):
                        raise SSHConnectionException("Connection to SSH server lost")
                else:
                    if not self.__write_serial(arg):
                        raise SSHConnectionException("Connection to SSH server lost")

        response = self.__get_last_line(self.__read_shell(expects))

        if response is None:
            raise SSHConnectionException("Connection to SSH server lost")

        if not self.__check_response(response, expects):
            success = False

        return response, success

    def get_device_info(self):
        deviceInfo = []
        self.__write_shell("ATI")
        response = self.__read_shell("OK")

        if self.__check_response(self.__get_last_line(response), "OK"):
            deviceInfo.append(self.__device.upper())
            deviceInfo.append(response.__getitem__(1)) # 2
            deviceInfo.append(response.__getitem__(2)) # 3
            deviceInfo.append(response.__getitem__(3)) # 4
        
            return deviceInfo
        else:
            return None

    # GSMD (modem controller service)
    def __start_GSMD(self):
        self.__write_shell("/etc/init.d/gsmd start")
        sleep(1)
        self.__read_shell()
    def __stop_GSMD(self):
        self.__write_shell("/etc/init.d/gsmd stop")
        sleep(1)
        self.__read_shell()

    def __clear_shell(self):
        self.__write_shell("clear")

    # socat (AT command reader/writer)
    def __start_socat(self):
        self.__write_shell("socat /dev/tty,raw,echo=0,escape=0x03 /dev/ttyUSB3,raw,setsid,sane,echo=0,nonblock ; stty sane")
        sleep(1)
        self.__read_shell()
    def __stop_socat(self):
        # Send Ctrl+C
        self.__write_shell("\x03")
        sleep(1)
        self.__read_shell()

    def __print(self):
        print("Connected to device '" + self.__device.upper() + "' via serial port")
        print("Device info:")
        for line in self.get_device_info()[1:]:
            print(line)
        print()

    def __del__(self):
        if self.__ssh_client:
            self.__stop_socat()
            self.__start_GSMD()
            self.__close_connection()
        # self.__error_printer.close()