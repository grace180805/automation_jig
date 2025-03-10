import time
from machine import UART


class MyUART:
    return_cmd = 'FF FF 01 02 00 FC FF FF 01 02 00 FC'

    def __init__(self, uart_id=2, baudrate=1000000, bits=8, parity=None, stop=1, rx=16, tx=17):
        self.uart = UART(uart_id)
        self.uart.init(baudrate=baudrate, bits=bits, parity=parity, stop=stop, rx=rx, tx=tx)

    def write(self, data):
        print('write data: %s ' % (data))
        data = bytes.fromhex(data)
        self.uart.write(data)

    def read(self):
        if self.uart.any():
            text = self.uart.readline()
            return text

    def is_return_cmd_success(self):
        #         print('checking return...')
        data = self.read()
        return_data = ' '.join(["%02X" % x for x in data])
        #         print('read data: %s ' % (return_data))
        if return_data == self.return_cmd:
            return True
        else:
            return False

    def check_sum(self, hex_str):
        """
        Check Sum = ~ (ID + Length + Instruction + Parameter1 + ... Parameter N) 若
        括号内的计算和超出 255, 则取最低的一个字节，“~”表示取反。
        """
        sum_result = 0
        # hex_num = bytes.fromhex(hex_str)
        for i in hex_str:
            sum_result += int(i, 16)

        if sum_result > 255:
            hex_result = hex(sum_result).upper()[-2:]  # 若括号内的计算和超出 255, 则取最低的一个字节
        else:
            hex_result = hex(sum_result).upper()[2:]

        inverted_result = ~int(hex_result, 16) & 0xFF # 转换成十进制之后取反
        hex_string = hex(abs(inverted_result)).upper()[2:]  # 转换成十六进制去掉结果前面的'0X'

        if len(hex_string) % 2 != 0:
            return '0' + hex_string
        else:
            return hex_string

    def steps_to_two_byte_hex(self, steps):
        """
        change steps to a two-byte hexadecimal number
        """
        hex_string = hex(int(steps))[2:]  # 转换为十六进制字符串，去掉前面的'0x'
        if len(hex_string) % 2 != 0:
            hex_string = '0' + hex_string  # 确保字符串长度为偶数，方便分组
        byte_list = [hex_string[i:i + 2] for i in range(0, len(hex_string), 2)]
        return byte_list

    def get_instructions(self, steps):
        byte_list = self.steps_to_two_byte_hex(steps)
        list_instruction = ["01", "09", "03", "2A"]
        list1 = ["00", "00", "E8", "03"]
        list_instruction.append(byte_list[1].upper())
        list_instruction.append(byte_list[0].upper())
        list_instruction.extend(list1)

        check_sum_num = self.check_sum(list_instruction)
        list_instruction.append(check_sum_num),
        list_instruction.insert(0, 'FF')
        list_instruction.insert(1, 'FF')
        my_instruction = ' '.join(list_instruction)

        return my_instruction

    def clear_data(self):
        data = 'FF FF 01 02 0A F2'
        print('clear data: %s ' % (data))
        hex_data = bytes.fromhex('FF FF 01 02 0A F2')  # clear data
        self.uart.write(hex_data)

    def open_torque(self):
        # print('open torque protection: %s ' % (data))
        # hex_data = bytes.fromhex(data)
        # self.uart.write(hex_data)
        #
        # print('open torque LED alarm: %s ' % (data))
        # hex_data = bytes.fromhex(data)
        # self.uart.write(hex_data)

        data = 'FF FF 01 04 03 28 01 CE'
        print('open_torque data: %s ' % (data))
        hex_data = bytes.fromhex(data)
        self.uart.write(hex_data)

    def close_torque(self):
        data = 'FF FF 01 04 03 28 00 CF'
        print('close_torque data: %s ' % (data))
        hex_data = bytes.fromhex(data)
        self.uart.write(hex_data)

    def get_current_steps(self):
        while self.uart.any():
            self.uart.read()
        hex_data = bytes.fromhex('FF FF 01 04 02 38 02 BE')
        self.uart.write(hex_data)
        time.sleep(0.2)  # 等待舵机返回数据

        if self.uart.any():  # 检查 UART 是否有返回数据
            read_data = self.uart.read()
            return_data = ' '.join(["%02X" % x for x in read_data])
            if len(return_data) == 23:
                location = int(return_data[18:20] + return_data[15:17], 16)
                return location

        return None

    def is_servo_moving(self):
        data = 'FF FF 01 04 02 42 01 B5'
        hex_data = bytes.fromhex(data)
        self.uart.write(hex_data)
        time.sleep(0.2)
        data = self.read()
        return_data = ' '.join(["%02X" % x for x in data])
        if return_data == 'FF FF 01 03 00 00 FB':
            return False
        else:
            return True
