import socket

# paquete con bytes = len(pkt.encode()) < 50 por si pasa por R3 (tiene MTU = 50)
pkt = "127.0.0.1;8885;010;00000001;00000000;00000001;0;a"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# se lo mandamos al router R1 (127.0.0.1, 8881)
sock.sendto(pkt.encode(), ("127.0.0.1", 8881))
sock.close()