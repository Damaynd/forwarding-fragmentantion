from router_frag import parse_packet, create_packet

def main():
    # Ejemplo: TTL = 10, ID = 1, OFFSET = 0, msg = "hola!"
    IP_packet_v1 = "127.0.0.1;8881;010;00000001;00000000;00000005;0;hola!".encode()

    parsed_IP_packet = parse_packet(IP_packet_v1)
    IP_packet_v2_str = create_packet(parsed_IP_packet)
    IP_packet_v2 = IP_packet_v2_str.encode()

    print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
    print("parsed_IP_packet =", parsed_IP_packet)

if __name__ == "__main__":
    main()
