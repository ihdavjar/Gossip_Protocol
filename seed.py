import json
import socket
import argparse
import threading


peer_node_list = {}

def register_peer(seed_id, node_id, ip, port):
    global peer_node_list
    peer_node_list[node_id] = (ip, port)

def send_peer_list(conn, seed_id, node_id):
    global peer_node_list

    conn.sendall(json.dumps(peer_node_list).encode())

def handle_client(conn, addr, seed_id):
    while True:
        msg = conn.recv(2048).decode()

        if msg[0:8] == 'register':
            temp_msg = msg.split()
            node_id = temp_msg[1]
            ip_ = temp_msg[2]
            port_ = temp_msg[3]

            print(f"Register Request from Peer Node {node_id}: {ip_}:{port_}")

            with open(f'output/seed/seed_{seed_id}.txt','a') as f:
                f.write(f"Register Request from Peer Node {node_id}: {ip_}:{port_}\n")

            register_peer(seed_id, int(node_id), ip_, int(port_))
            conn.sendall('registered'.encode())

        if msg[0:7] == 'getData':
            send_peer_list(conn, seed_id, int(msg[8:]))
        


def launch_seed_node(ip, port, node_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((ip, port))
        print(f"Seed node {node_id} is running on {ip}:{port}")

        with open(f'output/seed/seed_{node_id}.txt','w') as f:
            f.write(f"Seed node {node_id} is running on {ip}:{port}\n")


        sock.listen()
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr, node_id)).start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('ip', type=str)
    parser.add_argument('port', type=int)
    parser.add_argument('node_id', type=int)
    args = parser.parse_args()

    launch_seed_node(args.ip, args.port, args.node_id)