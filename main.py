import os
import socket
import random
import platform
import argparse
import subprocess
import pandas as pd

def create_config_file(n=3):
    '''
    n: number of seed nodes

    This function will create a config file containing information of each seed node
    '''
    if n>1:

        ip_addrs = socket.gethostbyname(socket.gethostname())

        # Range available ports 
        port_l = 1024
        port_r = 49151

        # choose only even numbers here
        ports = list(range(port_l, port_r, 2))
        ports = random.sample(ports, n)

        node_label = [f'Seed_{i}' for i in range(n)]

        df = pd.DataFrame({'node_label':node_label,'ip':ip_addrs,'port':ports})
        df.to_csv('config.csv',index=False)

        # Create files for broadcasting output
        os.makedirs('output/seed', exist_ok=True)
        os.makedirs('output/peer', exist_ok=True)
        
    else:
        print('Number of seed nodes should be greater than 1')
    
    return

def run_in_new_terminal(command):
    if platform.system() == "Windows":
        subprocess.Popen(["start", "cmd", "/k", command], shell=True)
    elif platform.system() == "Linux":
        subprocess.Popen(["x-terminal-emulator", "-e", command])
    elif platform.system() == "Darwin":  # macOS
        subprocess.Popen(["open", "-a", "Terminal", command])

def create_seed_terminals(df):
    '''
    df: dataframe containing information of each seed node

    This function will create a terminal for each seed node
    '''
    for i in range(len(df)):
        ip = df['ip'][i]
        port = df['port'][i]
        node_id = int(df['node_label'][i][5:])
        command = f'python seed.py {ip} {port} {node_id}'
        run_in_new_terminal(command)
    return
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=3)
    args = parser.parse_args()
    create_config_file(args.n)

    df = pd.read_csv('config.csv')
    create_seed_terminals(df)

    print('Config file created')


    # Initialize the adjacency matrix as an empty csv
    adj_matrix = pd.DataFrame()
    adj_matrix.to_csv('adj_matrix.csv')

    # Initialize the peer node list
    peer_node_list = {}
