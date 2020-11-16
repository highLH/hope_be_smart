import socket

def crc16(str):  # CRC 计算函数 输入是字符串
    data = bytearray.fromhex(str)
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if ((crc & 1) != 0):
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    crc = ((crc & 0xff) << 8) + (crc >> 8)
    # print(hex(crc).upper()[2:])
    # return hex(crc).upper()[2:]
    # print('%02X' % crc)
    return '%02X' % crc

cloud_addr = '00000000'
cloud_port = 8105

frame_head = 'FFFE'
register = '01'
forward = '03'
heart = '02'
data = '0004aaaa'
frame_tail = 'EFFF'

src_addr = '00000001'

REG = 1
HEART = 2
FORWARD = 3

def main():
    state = REG
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cloud_info = (cloud_addr,cloud_port)
    while True:
        if state == REG:
            crc = crc16(src_addr+cloud_addr+register+data)
            frame = frame_head+src_addr+cloud_addr+register+data+crc+frame_tail
            sock.sendto(bytearray.fromhex(frame),cloud_info) #发消息
            state = HEART
        elif state == HEART:
            crc = crc16(src_addr+cloud_addr+heart+data)
            frame = frame_head+src_addr+cloud_addr+heart+data+crc+frame_tail
            sock.sendto(bytearray.fromhex(frame),cloud_info) #发消息
            state = FORWARD
        elif  state == FORWARD:
            crc = crc16(src_addr+cloud_addr+forward+data)
            frame = frame_head+src_addr+cloud_addr+forward+data+crc+frame_tail
            sock.sendto(bytearray.fromhex(frame),cloud_info) #发消息
            state = HEART
        else:
            print("Undefined state :(")
        
        print(sock.recvfrom(1024).decode("utf-8")) #收消息，recvfrom可以得到发送方的消息和地址，recv只能得到消息


if __name__ == '__main__':
    main()
