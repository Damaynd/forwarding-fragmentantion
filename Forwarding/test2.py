SEPAREITOR = ";"

def parse_packet(IP_packet: bytes):
    text = IP_packet.decode()
    parts = text.split(SEPAREITOR, 2)
    dest_ip = parts[0]
    dest_port = int(parts[1])
    data = parts[2]
    return {"dest_ip": dest_ip, "dest_port": dest_port, "data": data}

def create_packet(parsed_IP_packet) -> str:
    return f"{parsed_IP_packet['dest_ip']}{SEPAREITOR}{parsed_IP_packet['dest_port']}{SEPAREITOR}{parsed_IP_packet['data']}"

IP_packet_v1 = "127.0.0.1;8881;hola".encode()
parsed_IP_packet = parse_packet(IP_packet_v1)
IP_packet_v2_str = create_packet(parsed_IP_packet)
IP_packet_v2 = IP_packet_v2_str.encode()

print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

