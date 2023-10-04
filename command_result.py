import dbus

SUCCESS = 0x0000
INVALID_STATE = 0x0001
INVALID_CONFIGURATION = 0x0002
INVALID_LENGTH = 0x0003
INVALID_PARAM = 0x0004
INVALID_COMMAND = 0xFFFF

def get_command_result(command_op_code, response_status):
    return [dbus.UInt16(command_op_code), dbus.UInt16(response_status)]