SEPAREITOR = ";"

def check_routes(routes_file_name, destination_address):
    """
    Revisa en orden el archivo de rutas y devuelve el siguiente salto (el next_hop
    que le dicen) para la dirección de destino.
    Recibe:
    - routes_file_name: nombre del archivo de rutas (str)
    - destination_address: tupla (dest_ip, dest_port)
    Retorna:
    - (next_hop_IP, next_hop_port) o None si no hay ruta D:
    """
    dest_ip, dest_port = destination_address

    with open(routes_file_name, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()

            # Posibles formatos para las partes:
            # Con cuatro columnas: IP_dest puerto_dest IP_next puerto_next
            # Con cinco columnas: IP_dest puerto_min puerto_max IP_next puerto_next
            if len(parts) == 4:
                ip_dest, p_min, ip_next, p_next = parts
                p_min = int(p_min)
                p_max = p_min
            elif len(parts) == 5:
                ip_dest, p_min, p_max, ip_next, p_next = parts
                p_min = int(p_min)
                p_max = int(p_max)
            else:
                # ignoramos
                continue

            p_next = int(p_next)

            # Si coincide IP y está el puerto en el rango
            if ip_dest == dest_ip and p_min <= dest_port <= p_max:
                return (ip_next, p_next)

    # Si no se encontró la ruta
    return None

def parse_packet(IP_packet: bytes):
    """
    Recibe en bytes b"IP_dest;puerto_dest;mensaje"
    Retorna un diccionario con claves dest_ip, dest_port, data
    """
    text = IP_packet.decode()
    parts = text.split(SEPAREITOR, 2)
    if len(parts) != 3:
        raise ValueError(f"Paquete IP mal formado: {text!r}")
    dest_ip = parts[0]
    dest_port = int(parts[1])
    data = parts[2]
    return {
        "dest_ip": dest_ip,
        "dest_port": dest_port,
        "data": data
    }

def probar(router_routes_file, raw_packet_str):
    IP_packet = raw_packet_str.encode()

    # Parseamos el paquete para obtener destino
    parsed = parse_packet(IP_packet)
    dest_ip = parsed["dest_ip"]
    dest_port = parsed["dest_port"]

    # Preguntamos a la tabla de rutas por el siguiente salto
    next_hop = check_routes(router_routes_file, (dest_ip, dest_port))

    print(f"Router ({router_routes_file}), paquete {raw_packet_str} -> next_hop = {next_hop}")


def main():
    # R1
    probar("rutas_R1_v2.txt", "127.0.0.1;8882;hola")
    probar("rutas_R1_v2.txt", "127.0.0.1;8883;hola")
    probar("rutas_R1_v2.txt", "127.0.0.1;8884;hola")
    # R2
    probar("rutas_R2_v2.txt", "127.0.0.1;8881;hola")
    probar("rutas_R2_v2.txt", "127.0.0.1;8883;hola")
    probar("rutas_R2_v2.txt", "127.0.0.1;8884;hola")
    # R3
    probar("rutas_R3_v2.txt", "127.0.0.1;8881;hola")
    probar("rutas_R3_v2.txt", "127.0.0.1;8882;hola")
    probar("rutas_R3_v2.txt", "127.0.0.1;8884;hola")

if __name__ == "__main__":
    main()
