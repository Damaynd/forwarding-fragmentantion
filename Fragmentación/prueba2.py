# send_150.py
import socket

TOTAL_LEN = 150  # tamaño total del datagrama

def build_packet(total_len = TOTAL_LEN):
    ip = "127.0.0.1"
    port = "8885" # hacia R5
    ttl = "010"
    ident = "00000150" # cualquiera
    offset = "00000000"
    flag = "0" # completo

    
    base = (
        "Este es un mensaje largo para probar "
        "fragmentacion y reensamblaje de paquetes IP. "
    )

    # Buscamos un largo de mensaje tal que el datagrama completo mida 150 bytes
    for msg_len in range(1, 500):
        # repetimos la frase y la cortamos al largo deseado
        msg = (base * 10)[:msg_len]

        size = f"{len(msg):08d}"  # [size] en 8 dígitos
        pkt = ";".join([ip, port, ttl, ident, offset, size, flag, msg])

        if len(pkt.encode()) == total_len:
            print("Paquete generado")
            print("Largo msg: ", len(msg))
            print("Msg: ")
            print(msg)
            print("Bytes totales del datagrama: ", len(pkt.encode()))
            return pkt

    raise RuntimeError("No se encontro un mensaje que deje el paquete en 150 bytes")

def send(from_port):
    pkt = build_packet()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(pkt.encode(), ("127.0.0.1", from_port))
    sock.close()

if __name__ == "__main__":
    # Cambiar para probar desde distintos puertos: 8881 -> R1, 8882 -> R2, 8883 -> R3, 8884 -> R4
    send(8881)
