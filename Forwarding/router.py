import sys
import socket
from collections import defaultdict

SEPARATOR = ";"

# Estado global para RRobin:
# clave: (routes_file_name, ip_dest, p_min, p_max)
# valor: índice de la próxima ruta a usar
rr_state = {}

# ========= parse_packet =========
def parse_packet(IP_packet: bytes):
    """
    Recibe: b"IP_dest;PUERTO_dest;mensaje"
    Devuelve: dict con claves dest_ip, dest_port, data
    """
    text = IP_packet.decode()
    parts = text.split(SEPARATOR, 2)
    if len(parts) != 3:
        raise ValueError(f"Paquete IP mal formado: {text!r}")
    dest_ip = parts[0]
    dest_port = int(parts[1])
    data = parts[2]
    return {"dest_ip": dest_ip, "dest_port": dest_port, "data": data}


def check_routes(routes_file_name, destination_address):
    """
    Revisa el archivo de rutas y devuelve el siguiente salto para destination_address
    usando round-robin cuando hay múltiples rutas posibles.

    :param routes_file_name: nombre del archivo de rutas, ej. "rutas_R2_v3.txt"
    :param destination_address: tupla (dest_ip, dest_port)
    :return: (next_hop_IP, next_hop_port) o None si no hay ruta
    """
    dest_ip, dest_port = destination_address

    matching_next_hops = []   # [(ip_next, p_next), ...]
    area_key = None           # (routes_file_name, ip_dest, p_min, p_max)

    with open(routes_file_name, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split()
            if len(parts) != 5:
                continue  # por seguridad

            ip_dest, p_min, p_max, ip_next, p_next = parts
            p_min = int(p_min)
            p_max = int(p_max)
            p_next = int(p_next)

            # ¿Esta línea sirve para este destino?
            if ip_dest == dest_ip and p_min <= dest_port <= p_max:
                # Todas las líneas que comparten (ip_dest, p_min, p_max)
                # forman un "área" para round-robin
                if area_key is None:
                    area_key = (routes_file_name, ip_dest, p_min, p_max)
                matching_next_hops.append((ip_next, p_next))

    # Si no hubo ninguna coincidencia, no hay ruta
    if not matching_next_hops:
        return None

    # Todas las rutas encontradas pertenecen al mismo área (mismo p_min/p_max)
    # Elegimos una en round-robin usando rr_state[area_key]
    global rr_state
    if area_key not in rr_state:
        rr_state[area_key] = 0  # primera vez que usamos esta área

    idx = rr_state[area_key]          # índice actual
    next_hop = matching_next_hops[idx % len(matching_next_hops)]
    rr_state[area_key] = (idx + 1) % len(matching_next_hops)

    return next_hop



# ========= loop del router (paso 6) =========
def main():
    if len(sys.argv) != 4:
        print("Uso: python3 router.py <IP_router> <PUERTO_router> <archivo_rutas>")
        sys.exit(1)

    router_ip = sys.argv[1]
    router_port = int(sys.argv[2])
    routes_file = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((router_ip, router_port))
    print(f"Router escuchando en ({router_ip}, {router_port}) usando {routes_file}")

    while True:
        # Paquete IP inmaculado y dirección de quién lo envió (addr)
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
            # formato pedido
            print(f"No hay rutas hacia {destination_address} para paquete {packet_str}")
            continue

        # formato pedido
        print(
            f"redirigiendo paquete {packet_str} "
            f"con destino final {destination_address} "
            f"desde {current_router} hacia {next_hop}"
        )

        # reenviamos el mismo paquete IP
        sock.sendto(ip_packet, next_hop)


if __name__ == "__main__":
    main()
