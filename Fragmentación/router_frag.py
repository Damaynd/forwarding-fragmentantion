import sys
import socket
from collections import defaultdict

SEPAREITOR = ";"

# Estado global para RRobin:
# key: (routes_file_name, ip_dest, p_min, p_max)
# value: idx del próximo camino/ruta a usar
rr_state = {}
received_frags = defaultdict(list)

def int_to_str(n: int, width: int) -> str:
    """Procesa un entero a string de ancho fijo con ceros a la izquierda"""
    return f"{n:0{width}d}"


# parse_packet
def parse_packet(IP_packet: bytes):
    """
    Recibe en bytes b"IP_dest;PUERTO_dest;TTL;mensaje"
    Devuelve un diccionario con claves dest_ip, dest_port, ttl, data
    """
    text = IP_packet.decode()
    # ahora vienen 4 (cuashro) partes: IP;PUERTO;TTL;msg
    parts = text.split(SEPAREITOR, 7)   # es decir, tenemos 7 splits para 8 elementos
    if len(parts) != 8:
        raise ValueError(f"Paquete IP mal formado: {text}")

    dest_ip = parts[0]
    dest_port = int(parts[1])
    ttl = int(parts[2])
    ident = int(parts[3])
    offset = int(parts[4])
    size = int(parts[5])
    flag = int(parts[6])
    data = parts[7]

    return {
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "ttl": ttl,
        "id": ident,
        "offset": offset,
        "size": size,
        "flag": flag,
        "data": data,
    }

def create_packet(parsed_IP_packet: dict) -> str:
    """
    Recibe un diccionario con keys dest_ip, dest_port, ttl, id, offset, flag, data
    y devuelve el string del paquete en formato: "IP;PUERTO;TTL;ID;OFFSET;SIZE;FLAG;MSG"
    """
    
    dest_ip = parsed_IP_packet['dest_ip']
    dest_port = parsed_IP_packet['dest_port']
    ttl = parsed_IP_packet['ttl']
    id = parsed_IP_packet['id']
    offset = parsed_IP_packet['offset']
    size = parsed_IP_packet['size']
    flag = parsed_IP_packet['flag']
    data = parsed_IP_packet['data']

    size = len(data.encode())

    return SEPAREITOR.join([
        dest_ip,
        str(dest_port),
        int_to_str(ttl, 3),
        int_to_str(id, 8),
        int_to_str(offset, 8),
        int_to_str(size, 8),
        str(flag),
        data
    ])
    


def check_routes(routes_file_name, destination_address):
    """
    Revisa el archivo de rutas y devuelve el siguiente salto
    (el next hop que le llaman) para destination_address
    usando RRobin cuando hayan rutas posibles dentro de la misma área.
    """
    dest_ip, dest_port = destination_address

    matching_next_hops = [] # [((ip_next, p_next), mtu), ...]
    area_key = None # (routes_file_name, ip_dest, p_min, p_max)

    with open(routes_file_name, "r") as f:
        for line in f:
            line = line.strip() # limpiamos
            if not line:
                continue

            parts = line.split()
            if len(parts) < 5:
                continue  # nop


            ip_dest, p_min, p_max, ip_next, p_next = parts[:5]

            if len(parts) >= 6:
                mtu = int(parts[5]) # ahora consideramos al parámetro mtu
            else: mtu = None
            

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

            # Si llegamos aquí, es una ruta válida dentro del área (ahora agregamos mtu)
            matching_next_hops.append(((ip_next, p_next), mtu))

    # Si no hay ninguna coincidencia entonces no hay ruta
    if not matching_next_hops:
        return None

    # RRobin dentro del área
    global rr_state
    if area_key not in rr_state:
        rr_state[area_key] = 0  # es la primera vez que usamos esta área

    idx = rr_state[area_key]
    next_hop, mtu = matching_next_hops[idx % len(matching_next_hops)] # asignamos la tupla
    rr_state[area_key] = (idx + 1) % len(matching_next_hops)

    return next_hop, mtu # retornamos la nueva tupla

def fragment_IP_packet(IP_packet, mtu):
    """
    Fragmenta un datagrama IP (con el tipo de header especificado) según el MTU
    Devuelve una lista de fragmentos (del mismo tipo que IP_packet: bytes o str)
    Si len(IP_packet) <= MTU (en bytes) -> devuelve [IP_packet]
    Si no, genera fragmentación.
    """

    # Trabajamos internamente siempre en bytes
    is_bytes = isinstance(IP_packet, (bytes, bytearray))
    if is_bytes:
        original_bytes = IP_packet
    else:
        print("IP_packet debe estar en bytes !")

    total_len = len(original_bytes)

    # Si no requiere fragmentación
    if total_len <= mtu:
        return [IP_packet]

    # Fragmentación (se vieeeneeeeeee):
    # Parseamos el paquete original
    parsed = parse_packet(original_bytes)

    # Calculamos tamaño del header en bytes
    # Idea: usar el mismo header pero con data vacía
    tmp = parsed.copy()
    tmp["data"] = ""
    tmp["size"] = 0
    header_str = create_packet(tmp)
    header_len = len(header_str.encode())

    # Capacidad de datos por fragmento
    max_payload = mtu - header_len

    # Datos originales en bytes
    message_bytes = parsed["data"].encode()
    msg_len = len(message_bytes)

    dest_ip = parsed["dest_ip"]
    dest_port = parsed["dest_port"]
    ttl = parsed["ttl"]
    ident = parsed["id"]
    offset = parsed["offset"] # puede venir distinto de 0?

    fragments = []
    start_index = 0
    bytes_remaining = msg_len

    while bytes_remaining > 0:
        chunk_len = min(max_payload, bytes_remaining)
        chunk_bytes = message_bytes[start_index:start_index + chunk_len]
        chunk_data = chunk_bytes.decode() # asumo UTF-8

        bytes_remaining -= chunk_len
        start_index += chunk_len

        # Flag = 1 si aún quedan fragmentos, 0 si éste is the last one
        if (bytes_remaining > 0):
            flag = 1
        else: flag = parsed["flag"]

        frag_parsed = {
            "dest_ip": dest_ip,
            "dest_port": dest_port,
            "ttl": ttl,
            "id": ident,
            "offset": offset,
            "size": chunk_len,
            "flag": flag,
            "data": chunk_data,
        }

        frag_str = create_packet(frag_parsed)
        frag_bytes = frag_str.encode()

        if is_bytes:
            fragments.append(frag_bytes)
        else:
            fragments.append(frag_str)

        # El siguiente fragmento comienza chunk_len bytes más adelante
        offset += chunk_len

    return fragments

def reassemble_IP_packet(fragment_list):
    """
    Reensambla un paquete IP a partir de una lista de fragmentos
    1.- Si la lista está vacía -> None
    2.- Si la lista tiene 1 elemento:
        2.1.- Si el offset = 0 y la flag = 0 -> paquete completo -> lo devolvemos tal cual
        2.2.- En otro caso -> fragmento suelto -> None
    3.- Si tiene más de 1 elemento:
        3.1.- Se ordenan por offset
        3.2.- Se verifica que los offsets sean contiguos
        3.3.- Se usan las flags para validar
        3.4.- Se concatena el mensaje y se reconstruye un paquete IP iwal
          al original (el que se le pasó a fragment_IP_packet).
    """

    if not fragment_list:
        return None

    # Tipo de los elementos (bytes o str)
    first = fragment_list[0]
    
    parsed_list = []
    for frag in fragment_list:
        parsed = parse_packet(frag)
        parsed_list.append((frag, parsed))

    # Tamaño 1
    if len(parsed_list) == 1:
        _, p = parsed_list[0]
        # No está fragmentado si offset = flag = 0
        if p["offset"] == 0 and p["flag"] == 0:
            # Devolvemos tal cual
            return fragment_list[0]
        else:
            # Sólo un fragmento suelto, imposible reconstruir
            return None

    # Más de un fragmento: ordenamos según offset
    
    parsed_list.sort(key=lambda t: t[1]["offset"])
    if parsed_list[-1][1]["flag"] != 0:
        return None

    # Tomamos los parámetros del primer fragmentiwi
    base = parsed_list[0][1]
    dest_ip = base["dest_ip"]
    dest_port = base["dest_port"]
    ttl = base["ttl"]
    ident = base["id"]
    base_offset = base["offset"]

    # Verificamos continuidad de offsets y flag
    expected_offset = base_offset
    message_bytes_parts = []
    last_flag = None

    for i, (_, p) in enumerate(parsed_list):
        # Nos aseguramos que todos los fragmentos pertenezcan efectivamente al datagrama
        if (p["dest_ip"] != dest_ip or
            p["dest_port"] != dest_port or
            p["id"] != ident):
            return None  # Nos equivocamos; aquí no pasó nada...

        # Offset vecino
        if p["offset"] != expected_offset:
            return None

        data_bytes = p["data"].encode()
        message_bytes_parts.append(data_bytes)
        expected_offset += len(data_bytes)

        # Flags; intermedios deben tener flag = 1
        if i < len(parsed_list) - 1:
            if p["flag"] != 1:
                return None
        else:
            # La flag de the last fragmento será la flag del paquete rearmado
            last_flag = p["flag"]

    # Reconstruimos el mensaje entero
    full_message_bytes = b"".join(message_bytes_parts)
    full_message = full_message_bytes.decode()

    # Construimos el paquete rearmado
    reassembled = {
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "ttl": ttl,
        "id": ident,
        "offset": base_offset,
        "size": len(full_message_bytes),
        "flag": last_flag,
        "data": full_message,
    }

    packet = create_packet(reassembled)
    return packet.encode()



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
        # Restricción por TTL
        if parsed["ttl"] <= 0:
            print(f"Se recibió paquete {packet_str} con TTL 0")
            continue

        destination_address = (parsed["dest_ip"], parsed["dest_port"])
        current_router = (router_ip, router_port)

        # Si es para mí
        if destination_address == current_router:
            frag_id = parsed["id"]
            received_frags[frag_id].append(ip_packet)
            # imprimimos el contenido del mensaje (sin los headers)
            # y ahora también acusamos recepción de fragmentos
            print(f"({current_router}): recepción de fragmento; id = {frag_id}, offset = {parsed['offset']}, flag = {parsed['flag']}")

            # Reconstruimos el paquete
            full_packet = reassemble_IP_packet(received_frags[frag_id])

            # Si tuvimos éxito
            if full_packet is not None:
                full_parsed = parse_packet(full_packet)
                print(full_parsed["data"])
                del received_frags[frag_id]
            
            # Si aún está incompleto o tuvimos éxito, no fordwardeamos
            continue

        # No es para mí -> miramos tabla de rutas
        result = check_routes(routes_file, destination_address)

        if result is None:
            # Formato pedido
            print(f"No hay rutas hacia {destination_address} para paquete {packet_str}")
            continue

        next_hop, mtu = result

        # Ahora decrementamos TTL antes de forwardear
        parsed["ttl"] -= 1
        new_packet_str = create_packet(parsed)
        new_ip_packet = new_packet_str.encode()

        # Fragment IP y Forwarding
        if mtu is None:
            fragments = [new_ip_packet]
        else:
            fragments = fragment_IP_packet(new_ip_packet, mtu)

        # Formato pedido
        print(
            f"redirigiendo paquete {packet_str} "
            f"con destino final {destination_address} "
            f"desde {current_router} hacia {next_hop} "
            f"con MTU = {mtu} "
            f"(Se envían {len(fragments)} fragmentiwis)"
        )

        # reenviamos paquetes según fragmentación
        for frag in fragments:
            sock.sendto(frag, next_hop)


if __name__ == "__main__":
    main()
