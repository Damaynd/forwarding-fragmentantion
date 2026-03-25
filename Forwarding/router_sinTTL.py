import sys
import socket
from collections import defaultdict

SEPAREITOR = ";"

# Estado global para RRobin:
# key: (routes_file_name, ip_dest, p_min, p_max)
# value: índice del próximo camino/ruta a usar
rr_state = {}

# parse_packet
def parse_packet(IP_packet: bytes):
    """
    Recibe en bytes b"IP_dest;PUERTO_dest;mensaje"
    Devuelve un diccionario con keys dest_ip, dest_port, data
    """
    text = IP_packet.decode()
    parts = text.split(SEPAREITOR, 2)
    if len(parts) != 3:
        raise ValueError(f"Paquete IP mal formado: {text}")
    dest_ip = parts[0]
    dest_port = int(parts[1])
    data = parts[2]
    return {"dest_ip": dest_ip, "dest_port": dest_port, "data": data}


def check_routes(routes_file_name, destination_address):
    """
    Revisa el archivo de rutas y devuelve el siguiente salto
    (el next hop que le llaman) para destination_address
    usando RRobin cuando hayan rutas posibles dentro de la misma área
    """
    dest_ip, dest_port = destination_address

    matching_next_hops = [] # [(ip_next, p_next), ...]
    area_key = None # (routes_file_name, ip_dest, p_min, p_max)

    with open(routes_file_name, "r") as f:
        for line in f:
            line = line.strip() # limpiamos
            if not line:
                continue

            parts = line.split()
            if len(parts) != 5:
                continue  # nop

            ip_dest, p_min, p_max, ip_next, p_next = parts
            p_min = int(p_min)
            p_max = int(p_max)
            p_next = int(p_next)

            # Si la línea nos sirve para este destino
            if not (ip_dest == dest_ip and p_min <= dest_port <= p_max):
                continue

            # Definimos el área
            this_area = (routes_file_name, ip_dest, p_min, p_max)

            # Si aún no hemos elegido un área, tomamos ésta
            if area_key is None:
                area_key = this_area
            # Si ya tenemos un área y esta es distinta (e.g: default), la ignoramos
            elif this_area != area_key:
                continue

            # Si llegamos aquí, es una ruta válida dentro del área
            matching_next_hops.append((ip_next, p_next))

    # Si no hay ninguna coincidencia entonces no hay ruta
    if not matching_next_hops:
        return None

    # RRobin dentro del área
    global rr_state
    if area_key not in rr_state:
        rr_state[area_key] = 0  # es la primera vez que usamos esta área

    idx = rr_state[area_key]
    next_hop = matching_next_hops[idx % len(matching_next_hops)]
    rr_state[area_key] = (idx + 1) % len(matching_next_hops)

    return next_hop



def main():
    if len(sys.argv) != 4:
        print("No se usa así pajarón: python3 router.py <IP_router> <puerto_router> <rutas_textfile>")
        sys.exit(1)

    router_ip = sys.argv[1]
    router_port = int(sys.argv[2])
    routes_file = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((router_ip, router_port))
    print(f"Router escuchando en ({router_ip}, {router_port}) usando {routes_file}")

    while True:
        # Paquete IP inmaculado (yia) y dirección de quién lo envió (su addr)
        ip_packet, addr = sock.recvfrom(4096)
        packet_str = ip_packet.decode()

        try:
            parsed = parse_packet(ip_packet)
        except ValueError as e:
            print(f"Paquete inválido desde {addr}: {e}")
            continue

        destination_address = (parsed["dest_ip"], parsed["dest_port"])
        current_router = (router_ip, router_port)

        # Si es para mí
        if destination_address == current_router:
            # imprimimos el contenido del mensaje (sin los headers)
            print(parsed["data"])
            continue

        # No es para mí -> miramos tabla de rutas
        next_hop = check_routes(routes_file, destination_address)

        if next_hop is None:
            # Formato pedido
            print(f"No hay rutas hacia {destination_address} para paquete {packet_str}")
            continue

        # Formato pedido
        print(
            f"redirigiendo paquete {packet_str} "
            f"con destino final {destination_address} "
            f"desde {current_router} hacia {next_hop}"
        )

        # reenviamos el mismo paquete IP
        sock.sendto(ip_packet, next_hop)


if __name__ == "__main__":
    main()
