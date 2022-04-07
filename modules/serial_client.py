from time import sleep
import serial
from modules.console_printer import ConsolePrinter
from modules.exceptions import SerialConnectionException, SerialRetryException

class SerialHandler:
    
    __serial_client__ = None
    __sleepTime__ = 0
    __device = None
    __error_printer = None

    def __init__(self, config, args):
        port = args.get_serial_port()
        baudrate = args.get_serial_baudrate()
        time = args.get_serial_timeout()
        self.__sleepTime__ = args.get_serial_wait()
        self.__device = config.get_param("device")
        self.__error_printer = ConsolePrinter(1)
        if not self.__open_connection(port, baudrate, time):
            raise SerialConnectionException("Unable to connect to serial port")

        self.__print()

    ###
    # Connection operations

    def __open_connection(self, port, baudrate, time):
        success = False
        counter = 0
        while counter <= 5 and not success:
            counter += 1
            try:
                self.__serial_client__ = serial.Serial(port, baudrate, timeout=time)
                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Unable to connect to serial port, retrying... " + str(counter)))
                    sleep(1)
        
        return success

    def __close_connection(self):
        if self.__serial_client__:
            self.__serial_client__.close

    ###
    # read/write operations

    def __read_serial(self, expects="OK"):
        success = False
        counter = 0
        while counter <= 5 and not success:
            counter += 1

            try:
                buffer = self.__read_AT(expects)
                # buffer = self.__serial_client__.readlines()
                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Could not read serial port, retrying... " + str(counter)))
                    sleep(1)
                else:
                    return None
        
        return buffer

    def __read_AT(self, expects):
        buffer = ""
        bufferList = []
        isRead = False

        msWaiting=0
        while(msWaiting <= 180000 and not isRead):
            msWaiting+=1
            if(self.__serial_client__.inWaiting() > 0):
                bufferNew = buffer + self.__serial_client__.read(self.__serial_client__.inWaiting()).decode()
                if buffer != bufferNew:
                    buffer = bufferNew

                    bufferList = buffer.splitlines()
                    if len(bufferList) > 0:

                        lastLine = self.__get_last_line(bufferList).strip()
                        if(self.__check_response(lastLine, expects)):
                            isRead = True
            sleep(0.01)
        
        return bufferList

    def __write_serial(self, str):
        success = False
        counter = 0
        while counter <= 5 and not success:
            counter += 1
            
            try:
                self.__serial_client__.reset_output_buffer
                self.__serial_client__.reset_input_buffer

                self.__serial_client__.write((str + "\r").encode())
                success = True
            except:
                if counter <= 5:
                    self.__error_printer.update_line(0, self.__error_printer.string_style("33", "Could not write serial port, retrying..." + str(counter)))
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

        if not self.__write_serial(command):
            raise SerialConnectionException("Connection to serial port lost")
            
        if arguments:
            for index, arg in enumerate(arguments):
                sleep(0.5)
                # If last arg
                if index + 1 == len(arguments):
                    if not self.__write_serial(arg + "\x1a"):
                        raise SerialConnectionException("Connection to serial port lost")
                else:
                    if not self.__write_serial(arg):
                        raise SerialConnectionException("Connection to serial port lost")

        response = self.__get_last_line(self.__read_serial(expects))

        if response is None:
            raise SerialConnectionException("Connection to serial port lost")

        if not self.__check_response(response, expects):
            success = False

        return response, success

    # Get device info (send ATI and read response)
    def get_device_info(self):
        deviceInfo = []

        self.__write_serial("ATI")
        response = self.__read_serial()

        if self.__check_response(self.__get_last_line(response), "OK"):
            deviceInfo.append(self.__device.upper())
            deviceInfo.append(response.__getitem__(2)) # 1
            deviceInfo.append(response.__getitem__(3)) # 2
            deviceInfo.append(response.__getitem__(4)) # 3
        
            return deviceInfo
        else:
            return None

    def __print(self):
        print("Connected to device '" + self.__device.upper() + "' via serial port")
        print("Device info:")
        for line in self.get_device_info()[1:]:
            print(line)
        print()

    def __del__(self):
        if self.__serial_client__:
            self.__close_connection()
        # self.__error_printer.close()