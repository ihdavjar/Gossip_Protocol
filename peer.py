import json
import time
import socket
import random
import argparse
import threading
import numpy as np
import pandas as pd


class PeerNode:
    def __init__(self, node_id, ip, port, df):
        self.node_id = node_id
        self.df = df
        self.ip = ip
        self.port = port
        self.messages_list = {}
        self.seed_nodes = self.register_to_seed()  # Register once
        self.queue = []
        self.peer_data = {}

        self.create_connections()

        # Create a persistent listening socket
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind((self.ip, self.port))
        self.server_sock.listen(5)  # Listen for incoming connections

        # Start a thread to handle incoming messages
        threading.Thread(target=self.listen_for_messages, daemon=True).start()

    def register_to_seed(self):
        '''
        Register the node to randomly selected seed nodes.
        '''
        n = len(self.df)
        seed_nodes = random.sample(range(n), n // 2 + 1)

        for i in seed_nodes:
            ip = self.df['ip'][i]
            port = self.df['port'][i]

            try:
                # Create a temporary client socket for registration
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip, port))
                    sock.sendall(f"register {self.node_id} {self.ip} {self.port}".encode())
                    msg = sock.recv(1024).decode()

                    if msg == 'registered':
                        pass
                       
                    else:
                        print(f"Failed to register to seed node {ip}:{port}")
                        with open(f'output/peer/peer_{self.node_id}.txt', 'a') as f:
                            f.write(f"Failed to register to seed node {i} {ip}:{port}\n")

            except Exception as e:
                print(f"Error registering to {ip}:{port} - {e}")

        return seed_nodes
    
    def create_connections(self):
        '''
        Create connections to other peer nodes.
        '''
        # Get the peer list from the seed nodes
        self.get_peer_data()

        adj_matrix = pd.read_csv('adj_matrix.csv')

        if (len(adj_matrix) == 0):
            adj_matrix = pd.DataFrame([1])

        else:
            # Number of already present nodes
            n_nodes = len(adj_matrix)
            temp_row = [0] * n_nodes

            # Get the distribution of peers
            peer_distribution = np.array(adj_matrix.sum(axis=0))

            # Calculate the probability for each peer
            peer_prob = peer_distribution / sum(peer_distribution)

            peers_selection = [random.random() < p for p in peer_prob]
            peers_selection.append(1)


            # Update the adjacency matrix            
            adj_matrix.loc[self.node_id] = temp_row
            adj_matrix[self.node_id] = 0

            adj_matrix = np.array(adj_matrix)

            for peer in self.peer_data:
                if peers_selection[int(peer)]:
                    adj_matrix[self.node_id][int(peer)] = 1
                    adj_matrix[int(peer)][self.node_id] = 1

            adj_matrix = pd.DataFrame(adj_matrix)   
            # save the adjacency matrix
            adj_matrix.to_csv('adj_matrix.csv', index=False, header=False)


        # Update the adjacency matrix
        for peer in self.peer_data:
            adj_matrix[self.node_id][int(peer)] = 1
            adj_matrix[int(peer)][self.node_id] = 1

        # Save the updated adjacency matrix
        adj_matrix.to_csv('adj_matrix.csv', index=False)


    def listen_for_messages(self):
        '''
        Listen for incoming messages from peers.
        '''
        while True:
            client_sock, addr = self.server_sock.accept()
            threading.Thread(target=self.handle_client, args=(client_sock, addr)).start()

    def handle_client(self, client_sock, addr):
        '''
        Handle messages received from peers.
        '''
        try:
            data = client_sock.recv(1024).decode()

            if data[0:4] == 'MSG':
                peer_id = data.split()[1]
                msg = " ".join(data.split()[2:])
                msg_split = data.split(' ')

                date_time = f"{msg_split[2]} {msg_split[3]}"
                ip = f"{msg_split[5]}"
                msg = f"{msg_split[7]}"

                temp_msg = f"<{date_time}>:<{ip}>:<{msg}>"

                if msg not in self.messages_list:
                    self.messages_list[msg] = {
                        'peer_id': peer_id,
                        'ip': addr[0],
                        'port': addr[1]
                    }
                    
                    with open(f'output/peer/peer_{self.node_id}.txt', 'a') as f:
                        f.write(f"Received message from Peer Node {peer_id}: {temp_msg} \n")
                    
                    # Add the message to the queue
                    self.queue.append((peer_id, msg, addr[0], addr[1]))

        except Exception as e:
            print(f"Error handling client {addr} - {e}")
        finally:
            client_sock.close()

    def generate_messages(self):

        # Generate data time etc
        date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        msgs = ["Vadhi Raj", "Saksham", "Ihdavjar", "Hello Peer!", "Yo Yo Peer my guy"]
        return f"MSG {self.node_id} {date_time} : {self.ip} : {random.choice(msgs)}"

    def get_peer_data(self):
        '''
        Fetch peer information from registered seed nodes.
        '''
        data_all = []

        for seed_node in self.seed_nodes:
            ip = self.df['ip'][seed_node]
            port = self.df['port'][seed_node]

            try:
                # Create a temporary client socket for fetching data
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip, port))
                    sock.sendall(f"getData {self.node_id}".encode())

                    # with open(f'output/peer/peer_{self.node_id}.txt', 'a') as f:
                    #     f.write(f"getData {self.node_id}\n")

                    data = sock.recv(1024).decode()
                    data = json.loads(data)
                    data_all.append(data)


                    with open(f'output/peer/peer_{self.node_id}.txt', 'a') as f:
                        f.write(f"Received data from seed node {seed_node} : {data.keys()}\n")

            except Exception as e:
                print(f"Error receiving data from {ip}:{port} - {e}")

        self.peer_data = dict(pair for dictionary in data_all for pair in dictionary.items())

    def gen_messages(self, delay, num_messages):
        '''
        Generate messages with a specified delay and number of messages.
        '''
        for _ in range(num_messages):

            msg = self.generate_messages()
            self.messages_list[msg] = {
                'peer_id': self.node_id,
                'ip': self.ip,
                'port': self.port
            }
            self.queue.append((self.node_id, msg, self.ip, self.port))
            time.sleep(delay)

    def send_message_to_peer_socket(self, peer_ip, peer_port, message):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((peer_ip, peer_port))
                sock.sendall(message.encode())
                
        except Exception as e:
            print(f"Error sending message to {peer_ip}:{peer_port} - {e}")            

    def send_message_to_peer(self):
        '''
        Send a message to another peer.
        '''
        while True:
            if len(self.queue) > 0:
                peer_id, msg, peer_ip, peer_port = self.queue.pop(0)

                # Access the connection list
                adj_matrix = np.array(pd.read_csv('adj_matrix.csv'))

                # Get the connection list for the peer
                peer_connections = adj_matrix[self.node_id, :]
                
                # Send to all except the ones having same peer_id
                for peer in range(len(peer_connections)):
                    if peer != int(peer_id):
                        if peer_connections[peer] != 0:
                            self.send_message_to_peer_socket(peer_ip, peer_port, msg)

    def run(self):
        '''
        Main loop to send messages and fetch peer data.
        '''
        # Thread for generating messages
        threading.Thread(target=self.gen_messages, args=(5, 10), daemon=True).start()
    
        self.send_message_to_peer()
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('Node_id', type=int, default= 0)
    args = parser.parse_args()

    df = pd.read_csv('config.csv')

    port_l = 1024
    port_r = 49151

    ip = socket.gethostbyname(socket.gethostname())
    ports = list(range(port_l + 1, port_r, 2))

    # Choosing a port for the node
    port_node = ports[args.Node_id]

    peer = PeerNode(args.Node_id, ip, port_node, df)

    peer.run()