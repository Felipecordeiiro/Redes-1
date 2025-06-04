import socket
import threading
from game import create_board, print_board, is_winner, is_draw

HOST, PORT = '0.0.0.0', 5000

clients = []                # lista de (conn, addr, marker)
board = create_board()      # board será sempre lista de 9 strings
lock = threading.Lock()

def broadcast(msg):
    for conn, _, _ in clients:
        try:
            conn.sendall(msg.encode())
        except:
            pass

def handle_game():
    try:
        print(f"Jogo iniciado ({len(clients)} jogadores)")
        turn = 0

        # 1) sinal de início
        broadcast("START")
        print("\"START\" enviado para os dois jogadores")

        while True:
            conn, addr, marker = clients[turn]
            print(f"VEZ de {marker} em {addr}")

            # 2) fala que é a vez dele
            conn.sendall("YOUR_TURN".encode())

            # 3) espera “MOVE i”
            data = conn.recv(1024).decode()
            print(f"Recebeu do {marker}: {data!r}")

            if not data or not data.startswith("MOVE"):
                print("Dados inválidos ou conexão fechada:", data)
                break

            idx = int(data.split()[1])   # transforma “1” → 1

            with lock:
                if board[idx] == ' ':
                    board[idx] = marker
                else:
                    conn.sendall("INVALID".encode())
                    print(f"Jogada inválida na posição {idx}")
                    continue

                state = "".join(board)      # ex: " X  OX   "
                broadcast(f"UPDATE {state}")
                print(f"\"UPDATE {state}\" enviado")

                print_board(board)

                if is_winner(board, marker):
                    broadcast(f"END WINNER {marker}")
                    print(f"Vitória de {marker}, mandando \"END WINNER {marker}\"")
                    break

                if is_draw(board):
                    broadcast("END DRAW")
                    print("Empate, mandando \"END DRAW\"")
                    break

                turn = 1 - turn

    except Exception as e:
        import traceback
        traceback.print_exc()
        print("ERROR na função handle_game():", e)

    finally:
        print("Jogo da velha finalizado e fechando conexões")
        for conn, _, _ in clients:
            try:
                return conn.close()
            except Exception as e:
                traceback.print_exc()
                print("Erro ao fechar as conexões usando conn.close()", e)

def handle_client(conn, addr):
    marker = 'X' if len(clients) == 0 else 'O'
    clients.append((conn, addr, marker))
    print(f"Adicionado {addr} como {marker}. Total de clientes = {len(clients)}")
    conn.sendall(f"MARKER {marker}".encode())

    if len(clients) == 2:
        print("Dois clientes conectados — iniciando jogo da velha")
        t = threading.Thread(target=handle_game, daemon=True)
        t.start()

def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((HOST, PORT))
    srv.listen()
    print(f"Servidor aguardando conexões em {HOST}:{PORT}")
    while True:
        conn, addr = srv.accept()
        print(f"Conexão de {addr}")
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
