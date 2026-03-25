import sys
import socket

SEPAREITOR = ";"


def main():
    if len(sys.argv) != 4:
        print("No se usa así pajarón: python3 prueba_router.py IP_dest,puerto_dest,TTL IP_router_inicial puerto_router_inicial")
        print("Ej: python3 prueba_router.py 127.0.0.1,8885,10 127.0.0.1 8881 < archivo.txt")
        sys.exit(1)

    headers = sys.argv[1]
    router_ip = sys.argv[2]
    router_port = int(sys.argv[3])

    # Parseamos headers
    try:
        dest_ip, dest_port_str, ttl_str = headers.split(",")
        dest_port = int(dest_port_str)
        ttl = int(ttl_str)
    except ValueError:
        print("Error: headers debe tener formato IP,PUERTO,TTL")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Leemos las líneas
    for line in sys.stdin:
        line = line.rstrip("\n")
        if not line:
            continue

        # Formato solicitado para paquetes IP;puerto;TTL;msg
        packet_str = f"{dest_ip}{SEPAREITOR}{dest_port}{SEPAREITOR}{ttl}{SEPAREITOR}{line}"
        sock.sendto(packet_str.encode(), (router_ip, router_port))

    sock.close()


if __name__ == "__main__":
    main()
