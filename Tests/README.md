# Forwarding and Fragmentation over UDP

This project implements a simplified IP-like router system in Python using UDP sockets. It was developed for a Computer Networks course and focuses on two main topics:

1. **Forwarding**
2. **Fragmentation and Reassembly**

The system simulates routers that receive, parse, forward, fragment, and reassemble packets according to routing tables and simplified IP-style headers.

## Features

### Forwarding
- UDP-based router simulation
- Packet parsing and packet creation
- Routing through text-based routing tables
- Delivery to local destination
- Packet dropping when no valid route exists
- **TTL support** to prevent infinite forwarding loops
- **Round-robin routing by area** when multiple equivalent routes are available
- Support for a **default router** for unmatched destinations

### Fragmentation
- Extended packet headers including:
  - destination IP
  - destination port
  - TTL
  - packet ID
  - fragment offset
  - payload size
  - more-fragments flag
  - message data
- Route-dependent **MTU support**
- Packet fragmentation when packet size exceeds MTU
- Reassembly of fragments at destination
- Validation of contiguous offsets and fragment flags
- Reassembly independent of fragment arrival order

## Main Files

- `router_conTTL.py`  
  Router implementation with forwarding, TTL handling, and round-robin routing.

- `router_frag.py`  
  Router implementation with forwarding, TTL, round-robin, fragmentation, and reassembly.

- `rutas_*.txt`  
  Routing table configurations used for different network topologies and experiments.

- `test*.py`, `prueba*.py`  
  Test and experiment scripts for validating forwarding, TTL behavior, round-robin routing, fragmentation, and reassembly.

## Packet Formats

### Forwarding with TTL
```text
IP_DEST;PORT_DEST;TTL;MESSAGE
```

### Fragmentation
```text
IP_DEST;PORT_DEST;TTL;ID;OFFSET;SIZE;FLAG;MESSAGE
```
#### How to Run

- Run a router:
```bash
python3 <router>.py 127.0.0.1 <port> <routes>.txt
```

#### Examples

```bash
python3 router_conTTL.py 127.0.0.1 8882 rutas_R2_v2.txt
python3 router_frag.py 127.0.0.1 8883 rutas_R3_v4_mtu.txt
```

### Forwarding Tests

Depending on the experiment, run the required routers first and then execute the test scripts.

#### Examples:
```bash
python3 test1_conTTL.py
python3 pruebas_sinTTL.py 1
python3 prueba_router.py 127.0.0.1,8883,10 127.0.0.1 8881 < msg.txt
```

### Fragmentation Tests
#### Examples:
```bash
python3 test1.py
python3 test3.py
python3 test4.py
python3 test5.py
python3 prueba1.py
python3 prueba2.py
```
### What the Project Demonstrates

This project shows how key networking concepts can be simulated in a lightweight environment:

- Packet forwarding through routing tables
- Loop mitigation with TTL
- Load balancing via round-robin routing
- Route selection by destination ranges
- MTU-aware fragmentation
- Packet reassembly from multiple fragments

It also highlights how routing decisions can affect packet order and path length in multi-router topologies.

### Course Context

Developed as part of a Computer Networks assignment focused on forwarding and fragmentation.

### Author

Emiliano Vásquez Parada
Universidad de Chile