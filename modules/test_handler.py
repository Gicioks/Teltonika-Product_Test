from modules.console_printer import ConsolePrinter
from modules.exceptions import ModuleInitializeException

class TestHandler:

    __connection = None
    __results = []
    __device_info = []
    __printer = None

    def __init__(self, connection):
        self.__connection = connection
        self.__device_info = connection.get_device_info()
        if not self.__device_info:
            raise ModuleInitializeException ("Unable to get device info")

    def test_commands(self, commands):
        self.__printer = ConsolePrinter(total=len(commands))
        for index, command in enumerate(commands):
            result = {}
            if "arguments" in command:
                respRaw, response = self.test_command(command["command"], command["expects"], command["arguments"])
                result["arguments"] = command["arguments"]
            else:
                respRaw, response = self.test_command(command["command"], command["expects"])
                result["arguments"] = None
            result["command"] = command["command"]
            result["expects"] = command["expects"]
            result["response"] = respRaw
            result["status"] = response
            self.__results.append(result)

    def test_command(self, command:str, expects, arguments = None):
        response = None
        success = False

        self.__printer.update_test_output(command, arguments)
        # self.__printer.clear_result_output()

        # If not AT command
        if not command.upper().startswith("AT"):
            self.__printer.update_result_output(False, command)
            response = "Incorrect command"
            
            if expects == response:
                status = "Passed"
            else:
                status = "Failed"

            return response, status

        # If args given
        if arguments:
            response, success = self.__connection.exec_command(command, expects, arguments)
        # If no args given
        else:
            response, success = self.__connection.exec_command(command, expects)
        if success:
            self.__printer.update_result_output(True, command)
            return response, "Passed"
        else:
            self.__printer.update_result_output(False, command)
            return response, "Failed"
    
    def get_results(self):
        return self.__results
    def get_device_info(self):
        return self.__device_info

    def close_printer(self):
        self.__printer.close()