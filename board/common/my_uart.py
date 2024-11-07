from machine import UART

class MyUART:
    
    return_cmd = 'FF FF 01 02 00 FC'
    
    
    def __init__(self, uart_id = 2, baudrate=1000000, bits=8, parity=None, stop=1, rx=16,tx=17):
        self.uart = UART(uart_id)
        self.uart.init(baudrate=baudrate, bits=bits, parity=parity, stop=stop, rx=rx,tx=tx)
    
    def write(self, data):
        print('write data: %s ' % (data))
        data = bytes.fromhex(data)
        self.uart.write(data)
        
    def read(self):
        if self.uart.any():
            text = self.uart.readline()
            return text
        
    def is_return_cmd_success(self):
        data = self.read()
        return_data = ' '.join(["%02X" % x for x in data])
        if return_data == self.return_cmd:
            print('read data: %s ' % (return_data))
            return True
        else:
            return False
        

        