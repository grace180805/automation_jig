# 定义通信结果常量
from machine import UART
import time
from scservo_def import *
from utils import Utils
TXPACKET_MAX_LEN = 250
RXPACKET_MAX_LEN = 250

# for Protocol Packet
PKT_HEADER0 = 0
PKT_HEADER1 = 1
PKT_ID = 2
PKT_LENGTH = 3
PKT_INSTRUCTION = 4
PKT_ERROR = 4
PKT_PARAMETER0 = 5

# Protocol Error bit
ERRBIT_VOLTAGE = 1
ERRBIT_ANGLE = 2
ERRBIT_OVERHEAT = 4
ERRBIT_OVERELE = 8
ERRBIT_OVERLOAD = 32
utils = Utils()
class PacketHandler:
    def __init__(self, uart_port):
        self.uart = UART(uart_port, baudrate=1000000, tx=14, rx=12)
        self.scs_end = 0
    def getUart(self):
        return self.uart

    def txPacket1(self):
        hex_data = b'\xFF\xFF\x01\x04\x02\x38\x02\xbe'
        hex_string = "FF FF 01 09 03 2A 00 20 00 00 E8 03 BD"
        byte_array = bytes.fromhex(hex_string.replace(" ", ""))
        self.uart.write(hex_data)
        utils.info("发送的数据： ", hex_data.hex())
        self.uart.write(byte_array)
        utils.info("发送的数据： ", byte_array.hex())
    def txPacket(self, txpacket):
        checksum = 0
        total_packet_length = txpacket[PKT_LENGTH] + 4  # 4: HEADER0 HEADER1 ID LENGTH

        # check max packet length
        if total_packet_length > TXPACKET_MAX_LEN:
            return COMM_TX_ERROR

        # make packet header
        txpacket[PKT_HEADER0] = 0xFF
        txpacket[PKT_HEADER1] = 0xFF

        # add a checksum to the packet
        for idx in range(2, total_packet_length - 1):  # except header, checksum
            checksum += txpacket[idx]

        txpacket[total_packet_length - 1] = ~checksum & 0xFF

        # tx packet
        self.flush()
        txpacket_byte_array = bytearray()
        for value in txpacket:
          txpacket_byte_array.append(value)
        hex_string = txpacket_byte_array.hex()
        utils.info("tx: ",hex_string)
        written_packet_length = self.uart.write(txpacket_byte_array)
        if total_packet_length != written_packet_length:
            return COMM_TX_FAIL

        return COMM_SUCCESS
    def flush(self):
        # self.uart.deinit()
         # 关闭串口
        # self.uart = UART(uart_port, baudrate=1000000, tx=14, rx=12)
        self.uart.write(b'')
    def rxPacket(self):
        rxpacket = []

        result = COMM_TX_FAIL
        checksum = 0
        rx_length = 0
        wait_length = 6  # 最小长度 (HEADER0 HEADER1 ID LENGTH ERROR CHKSUM)

        start_time = time.time()

        while True:
            # 循环读取串口数据
            if self.uart.any():
                rxpacket.extend(self.uart.read(1))
                rx_length = len(rxpacket)

                # 检查是否收到完整数据包
                if rx_length >= wait_length:
                    # 找到数据包头
                    for idx in range(0, (rx_length - 1)):
                        if rxpacket[idx] == 0xFF and rxpacket[idx + 1] == 0xFF:
                            break

                    if idx == 0:  # 数据包头在数据包的开头
                        if rxpacket[2] > 0xFD or rxpacket[3] > 63 or rxpacket[4] > 0x7F:
                            # 不可用的 ID、长度或错误
                            del rxpacket[0]  # 删除数据包的第一个字节
                            rx_length -= 1
                            continue

                        # 重新计算数据包的准确长度
                        if wait_length != (rxpacket[3] + 4):
                            wait_length = rxpacket[3] + 4
                            continue

                        if rx_length < wait_length:
                            # 检查超时
                            if time.time() - start_time > 1:  # 设置超时时间为1秒
                                if rx_length == 0:
                                    result = COMM_RX_TIMEOUT
                                else:
                                    result = COMM_RX_CORRUPT
                                break
                            else:
                                continue

                        # 计算校验和
                        for i in range(2, wait_length - 1):
                            checksum += rxpacket[i]
                        checksum = ~checksum & 0xFF
                        # 验证校验和
                        if rxpacket[wait_length - 1] == checksum:
                            result = COMM_SUCCESS
                        else:
                            result = COMM_RX_CORRUPT
                        break

                    else:
                        # 删除不必要的数据包
                        del rxpacket[0: idx]
                        rx_length -= idx

            else:
                # 检查超时
                if time.time() - start_time > 1:
                    if rx_length == 0:
                        result = COMM_RX_TIMEOUT
                    else:
                        result = COMM_RX_CORRUPT
                    break

        return rxpacket, result
    def txRxPacket(self, txpacket):
          rxpacket = None
          error = 0

          # tx packet
          result = self.txPacket(txpacket)
          if result != COMM_SUCCESS:
              return rxpacket, result, error

          # (ID == Broadcast ID) == no need to wait for status packet or not available
          if (txpacket[PKT_ID] == BROADCAST_ID):
              # self.portHandler.is_using = False
              return rxpacket, result, error

          # set packet timeout
          # if txpacket[PKT_INSTRUCTION] == INST_READ:
          #     self.portHandler.setPacketTimeout(txpacket[PKT_PARAMETER0 + 1] + 6)
          # else:
          #     self.portHandler.setPacketTimeout(6)  # HEADER0 HEADER1 ID LENGTH ERROR CHECKSUM

          # rx packet
          while True:
              rxpacket, result = self.rxPacket()
              if result != COMM_SUCCESS or txpacket[PKT_ID] == rxpacket[PKT_ID]:
                  break

          if result == COMM_SUCCESS and txpacket[PKT_ID] == rxpacket[PKT_ID]:
              error = rxpacket[PKT_ERROR]

          return rxpacket, result, error
    def readTxRx(self, scs_id, address, length):
        txpacket = [0] * 8
        data = []

        if scs_id >= BROADCAST_ID:
          return data, COMM_NOT_AVAILABLE, 0

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = 4
        txpacket[PKT_INSTRUCTION] = INST_READ
        txpacket[PKT_PARAMETER0 + 0] = address
        txpacket[PKT_PARAMETER0 + 1] = length

        rxpacket, result, error = self.txRxPacket(txpacket)
        if result == COMM_SUCCESS:
          error = rxpacket[PKT_ERROR]
          data.extend(rxpacket[PKT_PARAMETER0: PKT_PARAMETER0 + length])

        return data, result, error
    def writeTxRx(self, scs_id, address, length, data):
        txpacket = [0] * (length + 7)

        txpacket[PKT_ID] = scs_id
        txpacket[PKT_LENGTH] = length + 3
        txpacket[PKT_INSTRUCTION] = INST_WRITE
        txpacket[PKT_PARAMETER0] = address

        txpacket[PKT_PARAMETER0 + 1: PKT_PARAMETER0 + 1 + length] = data[0: length]
        rxpacket, result, error = self.txRxPacket(txpacket)

        return result, error
    def read2ByteTxRx(self, scs_id, address):
        data, result, error = self.readTxRx(scs_id, address, 2)
        data_read = self.sts_makeword(data[0], data[1]) if (result == COMM_SUCCESS) else 0
        return data_read, result, error

    def read1ByteTxRx(self, scs_id, address):
        data, result, error = self.readTxRx(scs_id, address, 1)
        data_read = data[0] if (result == COMM_SUCCESS) else 0
        return data_read, result, error
    def write1ByteTxRx(self, scs_id, address, data):
        data_write = [data]
        return self.writeTxRx(scs_id, address, 1, data_write)
    def sts_makeword(self, a, b):
        if self.scs_end==0:
            return (a & 0xFF) | ((b & 0xFF) << 8)
        else:
            return (b & 0xFF) | ((a & 0xFF) << 8)
    def sts_lobyte(self, w):
      if self.scs_end == 0:
        return w & 0xFF
      else:
        return (w >> 8) & 0xFF
    def sts_hibyte(self, w):
      if self.scs_end == 0:
        return (w >> 8) & 0xFF
      else:
        return w & 0xFF
    def sts_tohost(self, a, b):
      if (a & (1 << b)):
        return -(a & ~(1 << b))
      else:
        return a
    def getRxPacketError(self, error):
      if error & ERRBIT_VOLTAGE:
          return "[ServoStatus] Input voltage error!"

      if error & ERRBIT_ANGLE:
          return "[ServoStatus] Angle sen error!"

      if error & ERRBIT_OVERHEAT:
          return "[ServoStatus] Overheat error!"

      if error & ERRBIT_OVERELE:
          return "[ServoStatus] OverEle error!"

      if error & ERRBIT_OVERLOAD:
          return "[ServoStatus] Overload error!"

      return ""
