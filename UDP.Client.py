import socket
import struct
import time
import random
from threading import Thread

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8888
BUFFER_SIZE = 1024
TIMEOUT_MS = 100
RETRANSMISSION_LIMIT = 2

class Packet:
    def __init__(self, sequence_number, version, data):
        self.sequence_number = sequence_number
        self.version = version
        self.data = data

    def to_bytes(self):
        return struct.pack("!Hb", self.sequence_number, self.version) + self.data.encode()

    @staticmethod
    def from_bytes(packet_data):
        sequence_number, version = struct.unpack("!Hb", packet_data[:3])
        data = packet_data[3:].decode()
        return Packet(sequence_number, version, data)

def send_packet(sock, server_addr, packet):
    sock.sendto(packet.to_bytes(), server_addr)

def receive_packet(sock):
    sock.settimeout(TIMEOUT_MS / 1000.0)
    try:
        packet_data, _ = sock.recvfrom(BUFFER_SIZE)
        received_packet = Packet.from_bytes(packet_data)
        return received_packet
    except socket.timeout:
        return None

def communicate_with_server(client_socket, server_addr):
    packets_sent = 0
    packets_received = 0
    total_rtt = 0
    min_rtt = float('inf')
    max_rtt = float('-inf')
    rtts = []
    first_start_time = None
    last_end_time = None

    for i in range(1, 13):
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        packet = Packet(i, 2, timestamp)
        if first_start_time is None:
            first_start_time = time.time()

        start_time = time.time()
        send_packet(client_socket, server_addr, packet)
        packets_sent += 1
        delay = random.uniform(0.002, 0.005)
        time.sleep(delay)

        received = False

        for attempt in range(RETRANSMISSION_LIMIT + 1):
            response_packet = receive_packet(client_socket)
            if response_packet:
                received = True
                current_time = time.time()
                rtt = (current_time - start_time) * 1000
                rtts.append(rtt)
                total_rtt += rtt
                min_rtt = min(min_rtt, rtt)
                max_rtt = max(max_rtt, rtt)
                packets_received += 1
                last_end_time = current_time
                print(f"收到响应，序列号: {response_packet.sequence_number} (往返时间: {rtt:.2f} ms) 服务器IP: {server_addr[0]} 端口号:{server_addr[1]}")
                break
            else:
                print(f"序列号 {i} 超时，正在重传 ({attempt + 1}/{RETRANSMISSION_LIMIT})")
                start_time = time.time()
                send_packet(client_socket, server_addr, packet)
                packets_sent += 1
                delay = random.uniform(0.002, 0.005)
                time.sleep(delay)

        if not received:
            print(f"序列号 {i} 的数据包在重传后仍未收到响应。")

    client_socket.close()

    loss_rate = ((packets_sent - packets_received) / packets_sent) * 100
    avg_rtt = total_rtt / packets_received if packets_received > 0 else 0
    rtt_sum_of_squares = sum((rtt - avg_rtt) ** 2 for rtt in rtts)
    stddev_rtt = (rtt_sum_of_squares / packets_received) ** 0.5 if packets_received > 0 else 0

    print("\n汇总:")
    print(f"发送的数据包数: {packets_sent}")
    print(f"接收的数据包数: {packets_received}")
    print(f"丢包率: {loss_rate:.2f}%")
    print(f"最大往返时间: {max_rtt:.2f} ms")
    print(f"最小往返时间: {min_rtt:.2f} ms")
    print(f"平均往返时间: {avg_rtt:.2f} ms")
    print(f"往返时间标准差: {stddev_rtt:.2f} ms")

    if first_start_time is not None and last_end_time is not None:
        total_response_time = (last_end_time - first_start_time) * 1000
        print(f"服务器整体响应时间: {total_response_time:.2f} ms")

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_addr = (SERVER_IP, SERVER_PORT)
    communicate_with_server(client_socket, server_addr)

if __name__ == "__main__":
    main()
