import socket

SERVER_IP, SERVER_PORT = '127.0.0.1', 5000

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))

    # recebe marcação X ou O
    try:
        data = sock.recv(1024).decode()
    except ConnectionResetError:
        print("Erro: conexão foi fechada antes de receber a marcação. Finalizando.")
        return
    if not data:
        print("Servidor não enviou nada. Saindo.")
        return
    _, marker = data.split()
    print(f"Você é: {marker}")

    while True:
        try:
            msg = sock.recv(1024).decode()
        except ConnectionResetError:
            print("Conexão interrompida pelo servidor.")
            break

        if not msg:
            # socket foi fechado normalmente (recv retornou b'')
            print("Servidor fechou a conexão.")
            break

        if msg == "START":
            print("Jogo iniciado!")
        elif msg.startswith("UPDATE"):
            state = msg[len("UPDATE "):]
            # Exibe o tabuleiro em 3 linhas de 3 casas
            for i in range(0, 9, 3):
                print("|".join(state[i:i+3]))
            print()
        elif msg == "YOUR_TURN":
            move = str(input("Sua jogada (0-8): "))
            sock.sendall(f"MOVE {move}".encode())
        elif msg.startswith("END"):
            parts = msg.split()
            if parts[1] == "WINNER":
                print(f"Fim: vencedor {parts[2]}")
            else:
                print("Fim: empate")
            break
        elif msg == "INVALID":
            print("Movimento inválido, tente outra posição.")

    sock.close()
    print("Cliente finalizado.")

if __name__ == "__main__":
    main()