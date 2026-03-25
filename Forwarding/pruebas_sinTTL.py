import sys
import time
import socket

SEPAREITOR = ";"


def send_packet(entry_ip, entry_port, dest_ip, dest_port, msg, delay=0.2):
    """Básicamente un sender de paquetes"""
    payload = f"{dest_ip}{SEPAREITOR}{dest_port}{SEPAREITOR}{msg}".encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(payload, (entry_ip, entry_port))
    sock.close()
    time.sleep(delay)  # Pequeño delay para hacerlo más legible


# Prueba 1: 3 routers

def prueba1():
    """
    Prueba 1 del enunciado:

    Antes de correr este test, hay que asegurarse de tener
    levantados los 3 routers en terminales distintas:

        python3 router.py 127.0.0.1 8881 rutas_R1_v2.txt
        python3 router.py 127.0.0.1 8882 rutas_R2_v2.txt -> éste está modificado
        python3 router.py 127.0.0.1 8883 rutas_R3_v2.txt

    Este test envía paquetes desde R1 (8881) -> R3 (8883)
    y trata de evidenciar lo que sucede cuando un archivo de rutas está
    mal configurado.
    """
    print("Prueba 1: Enviando paquetes R1 -> R3...")
    for i in range(1, 6):
        msg = f"R1->R3 #{i}"
        send_packet("127.0.0.1", 8881, "127.0.0.1", 8883, msg)
    print("Prueba 1 finalizada :D")


# Prueba 2: 5 routers

def prueba2():
    """
    Prueba 2 del enunciado:

    Antes de correr este test, hay que asegurarse tener levantados los 5 routers:

        python3 router.py 127.0.0.1 8881 rutas_R1_v3.txt
        python3 router.py 127.0.0.1 8882 rutas_R2_v3.txt
        python3 router.py 127.0.0.1 8883 rutas_R3_v3.txt
        python3 router.py 127.0.0.1 8884 rutas_R4_v3.txt
        python3 router.py 127.0.0.1 8885 rutas_R5_v3.txt

    Este test envía paquetes R1 (8881) -> R5 (8885) y trata
    de evidenciar el número de saltos según RRobin
    """
    print("Prueba 2: Enviando paquetes R1 -> R5...")
    for i in range(1, 9):
        msg = f"R1->R5 #{i}"
        send_packet("127.0.0.1", 8881, "127.0.0.1", 8885, msg)
    print("Prueba 2 finalizada >:D")


# Prueba 3: Routers R0-R6

def prueba3():
    """
    Prueba 3 del enunciado:

    Antes de correr este test, hay que asegurarse de tener levantados los 7 routers:

        python3 router.py 127.0.0.1 8880 rutas_R0_v4.txt
        python3 router.py 127.0.0.1 8881 rutas_R1_v4.txt
        python3 router.py 127.0.0.1 8882 rutas_R2_v4.txt
        python3 router.py 127.0.0.1 8883 rutas_R3_v4.txt
        python3 router.py 127.0.0.1 8884 rutas_R4_v4.txt
        python3 router.py 127.0.0.1 8885 rutas_R5_v4.txt
        python3 router.py 127.0.0.1 8886 rutas_R6_v4.txt

    Este test intercala paquetes R1->R5 y R5->R1 para verificar el funcionamiento
    de RRobin por zonas/áreas.
    """
    print("Prueba 3: Enviando paquetes R1 <-> R5...")

    # intercalamos 4 paquetes R1->R5 y 4 paquetes R5->R1
    for i in range(1, 5):
        # R1 -> R5 (entra por R1 = 8881)
        msg1 = f"R1->R5 #{i}"
        send_packet("127.0.0.1", 8881, "127.0.0.1", 8885, msg1)

        # R5 -> R1 (entra por R5 = 8885)
        msg2 = f"R5->R1 #{i}"
        send_packet("127.0.0.1", 8885, "127.0.0.1", 8881, msg2)

    print("Prueba 3 finalizada OwO")


# Programa

def main():
    if len(sys.argv) == 1:
        print("Uso: python3 pruebas_sinTTL.py [1|2|3|all]")
        print("1 -> Prueba 1 (3 routers con rutas_R*_v2.txt)")
        print("2 -> Prueba 2 (5 routers, rutas_R*_v3.txt)")
        print("3 -> Prueba 3 (7 routers con R0 y R6, rutas_R*_v4.txt)")
        return

    choice = sys.argv[1]

    if choice == "1":
        prueba1()
    elif choice == "2":
        prueba2()
    elif choice == "3":
        prueba3()
    else:
        print("Opción inválida: Usa 1, 2 o 3")


if __name__ == "__main__":
    main()
