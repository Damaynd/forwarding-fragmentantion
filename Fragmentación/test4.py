from router_frag import fragment_IP_packet, reassemble_IP_packet

def main():

    IP_packet_v1 = "127.0.0.1;8885;010;00000001;00000000;00000005;0;hola!".encode()    
    MTU = 51
    fragment_list = fragment_IP_packet(IP_packet_v1, MTU)
    
    print("Cantidad de fragmentos generados:", len(fragment_list))

    IP_packet_v2 = reassemble_IP_packet(fragment_list)

    print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

if __name__ == "__main__":
    main()