import socket
import struct

SERVER_IP = "127.0.0.1"
SERVER_PORT = 8888

def receive_initialization(sock):
    data = sock.recv(1024)
    type, block_count = struct.unpack("!ii", data)
    return block_count

def receive_reverse_request(sock):
    data = sock.recv(1024)
    type, length = struct.unpack("!ii", data[:8])
    return data[8:].decode()

def send_reverse_answer(sock, reversed_data):
    length = len(reversed_data)
    data = struct.pack("!ii", 3, length) + reversed_data.encode()
    sock.sendall(data)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        print("Connection from:", address)

        block_count = receive_initialization(client_socket)

        for _ in range(block_count):
            data = receive_reverse_request(client_socket)
            reversed_data = data[::-1]  # 反转数据块
            send_reverse_answer(client_socket, reversed_data)

        client_socket.close()

if __name__ == "__main__":
    main()
