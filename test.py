import _socket
import array
data = bytearray(bytes.fromhex('FFFF0109032AA00F0000D00742'))

print(data)
# data = '\x01\x04\x028\x02'
# # def checksum(data):
# #     s = 0
# #     for d in data:
# #         s+=d
# #     s = (s & 0xffff) + (s>>16)
# #     s+=(s>>16)
# #     return (~s & 0xffff)
#
# checksum = sum(map(ord, data))
# print(checksum)

