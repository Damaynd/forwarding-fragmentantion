from router_conTTL import parse_packet, create_packet

def main():
    IP_packet_v1 = "127.0.0.1;8881;4;hola".encode()

    parsed_IP_packet = parse_packet(IP_packet_v1)
    IP_packet_v2_str = create_packet(parsed_IP_packet)
    IP_packet_v2 = IP_packet_v2_str.encode()

    print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
    print("parsed_IP_packet =", parsed_IP_packet)

if __name__ == "__main__":
    main()
