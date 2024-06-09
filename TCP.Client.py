import socket
import struct
import random
import os

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8888

FILE_PATH = "tcp.txt"  # 直接在代码中指定文件路径
Lmin = 20  # 最小块大小
Lmax = 90  # 最大块大小

def send_initialization(sock, block_count):
    data = struct.pack("!ii", 0, block_count)
    sock.sendall(data)

def send_reverse_request(sock, file_path, block_sizes):
    with open(file_path, 'r') as file:
        data = file.read()

    offset = 0
    for i, block_size in enumerate(block_sizes):
        block_data = data[offset:offset + block_size]
        block_length = len(block_data)
        block_msg = struct.pack("!ii", 1, block_length) + block_data.encode()
        sock.sendall(block_msg)
        offset += block_size

def receive_reverse_answer(sock):
    header = sock.recv(8)
    if len(header) < 8:
        raise RuntimeError("Failed to receive complete header.")

    type, length = struct.unpack("!ii", header)

    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise RuntimeError("Failed to receive complete data.")
        data += chunk

    return data.decode()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))

    file_size = os.path.getsize(FILE_PATH)

    block_sizes = []
    remaining_size = file_size
    while remaining_size > 0:
        block_size = random.randint(Lmin, Lmax)
        if block_size > remaining_size:
            block_size = remaining_size
        block_sizes.append(block_size)
        remaining_size -= block_size

    block_count = len(block_sizes)
    send_initialization(client_socket, block_count)

    for i, block_size in enumerate(block_sizes):
        send_reverse_request(client_socket, FILE_PATH, [block_size])
        reversed_data = receive_reverse_answer(client_socket)
        print(f"第 {i + 1} 块: 反转的文本如下")
        print(f"Block {i + 1}: Reversed Data:", reversed_data)

    client_socket.close()

if __name__ == "__main__":
    main()
