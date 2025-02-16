# Seed and Peer Node
This project simply implements a peer-to-peer network using seed and peer nodes.

## Seed Node
Seed nodes are special nodes in a peer-to-peer network that act as initial contact points for other nodes to join the network. They provide a list of known active nodes to new nodes, allowing them to bootstrap and establish connections with other peers in the network.

## Peer Node
Peer nodes are the nodes that are connected to the network and are not seed nodes. They are the nodes that store and retrieve data from the network.

## Seed Node and Peer Node Working
When a peer node starts, it connects to n/2 + 1 seed node to get the network's list of active peer nodes. It then connects to the active peer nodes and starts the process of data storage and retrieval.

## Seed Node and Peer Node Communication
The seed node and peer node communicate using the following messages:
- `request`: The peer node sends this message to the seed node to get the list of active peer nodes in the network.
-  The seed node sends the list of peer node connected to it .

## Peer Node and Peer Node Communication
Peer node sends message  as per the format 
    `<self.timestamp>:<self.IP>:<self.Msg#>`
  - A peer sends this message to another peer to forward data.  
  - **Example:**  
    
   ```
   
   2025-02-16 12:34:56 : 192.168.1.10 : Hello, Peer!
   
   ``` 
  - The receiving peer processes the message and may forward it.  


## How to Run?
- Run '`pip install -r requirements.txt` to install the required packages.
- Run `python3 main.py --n` where n is the number of seed nodes default is 3. 
- Run  peer nodes using the command `python3 peer.py peer_id ` to create a new peer.




## Stopping the Peer Node
- To stop the peer node, press `Ctrl + C` in the terminal where the peer node is running.

## Output Files
- Two output directories will be created `seed` and `peer` in `output` folder containing the logs of the seed node and peer nodes respectively.
- The logs will contain the messages sent and received by the seed node and peer nodes.


## Contributors
- [Saksham Jain(B21EE059)]
- [Kalbhavi Vadhi Raj(B21EE030)]