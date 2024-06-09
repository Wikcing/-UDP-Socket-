import socket
import struct
import time
import random
from threading import Thread

SERVER_PORT = 8888
BUFFER_SIZE = 1024

class Packet:
    def __init__(self, sequence_number, version, data):
        self.sequence_number = sequence_number
        self.version = version
        self.data = data

    @classmethod
    def from_bytes(cls, packet_data):
        sequence_number, version = struct.unpack("!ii", packet_data[:8])
        data = packet_data[8:].decode()
        return cls(sequence_number, version, data)

    def to_bytes(self):
        return struct.pack("!ii", self.sequence_number, self.version) + self.data.encode()

def handle_client(server_socket):
    random.seed(time.time())

    while True:
        packet_data, client_address = server_socket.recvfrom(BUFFER_SIZE)
        packet = Packet.from_bytes(packet_data)
        address_length = len(client_address)

        if random.randint(0, 15) == 0:
            print("丢弃数据包，序列号:", packet.sequence_number)
            continue

        print("接收到来自客户端的数据包，序列号:", packet.sequence_number)

        current_time = time.strftime("%H:%M:%S", time.localtime())
        response_packet = Packet(packet.sequence_number, packet.version, f"服务器时间: {current_time}")
        server_socket.sendto(response_packet.to_bytes(), client_address)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("127.0.0.1", SERVER_PORT))

    print("服务器已启动，等待客户端连接...")

    for _ in range(5):
        client_thread = Thread(target=handle_client, args=(server_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()
