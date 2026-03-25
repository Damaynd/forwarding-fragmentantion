from router_frag import fragment_IP_packet

def main():
    IP_packet = "127.0.0.1;8885;010;00000001;00000000;00000005;0;hola!".encode()

    # No fragmenta
    frags1 = fragment_IP_packet(IP_packet, mtu = 200)
    print("Caso 1 - Cantidad Fragmentos:", len(frags1))
    print("Igual al original? OwO :", frags1[0] == IP_packet)

    # Sí fragmenta
    frags2 = fragment_IP_packet(IP_packet, mtu = 51)
    print("Caso 2 - Cantidad Fragmentos:", len(frags2))
    for i, frag in enumerate(frags2, 1):
        print(f"Fragmento N°{i} = ", frag)

if __name__ == "__main__":
    main()
