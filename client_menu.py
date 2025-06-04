# client_menu.py

import socket
import sys
import random
from game import create_board, print_board, is_winner, is_draw

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000

def play_vs_machine():
    board = create_board()
    current_player = 'X'  # o usuário sempre começa como X

    print("\nModo: Você (X) vs Máquina (O)\n")
    print_board(board)

    while True:
        if current_player == 'X':
            try:
                move = int(input("Sua jogada (0-8): ").strip())
            except ValueError:
                print("Digite um número de 0 a 8.")
                continue

            if move < 0 or move > 8:
                print("Posição inválida. Tente novamente.")
                continue

            if board[move] != ' ':
                print("Casa ocupada. Tente outra posição.")
                continue

            board[move] = 'X'
            print_board(board)

            if is_winner(board, 'X'):
                print("Parabéns! Você (X) venceu!")
                break

            if is_draw(board):
                print("Empate!")
                break

            current_player = 'O'  # passa para a máquina

        else:
            print("Máquina está jogando...")
            empty_indices = [i for i, cell in enumerate(board) if cell == ' ']
            if not empty_indices:
                # não deveria acontecer porque verificamos empate acima
                print("Empate!")
                break

            ai_move = random.choice(empty_indices)
            board[ai_move] = 'O'
            print(f"Máquina jogou em {ai_move}.")
            print_board(board)

            if is_winner(board, 'O'):
                print("A máquina (O) venceu!")
                break
            if is_draw(board):
                print("Empate!")
                break

            current_player = 'X'  # de volta para o humano

    print("Fim do jogo contra a máquina.\n")
    input("Pressione Enter para retornar ao menu...")

def play_vs_network():
    print(f"\nTentando conectar ao servidor em {SERVER_IP}:{SERVER_PORT}...\n")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor. Verifique se o servidor está rodando.")
        input("Pressione Enter para retornar ao menu...")
        return
    except Exception as e:
        print("Erro ao tentar conectar:", e)
        input("Pressione Enter para retornar ao menu...")
        return

    # 1) Recebe “MARKER X” ou “MARKER O”
    data = sock.recv(1024).decode()
    if not data.startswith("MARKER"):
        print("Resposta inesperada do servidor:", data)
        sock.close()
        input("Pressione Enter para retornar ao menu...")
        return

    _, marker = data.split()
    opponent_marker = 'O' if marker == 'X' else 'X'
    print(f"Conectado! Você é: {marker}\n")

    while True:
        try:
            msg = sock.recv(1024).decode()
        except ConnectionResetError:
            print("Conexão interrompida pelo servidor.")
            break

        if not msg:
            print("Servidor fechou a conexão.")
            break

        if msg == "START":
            print("Jogo iniciado pelo servidor! Aguardando atualizações...\n")

        elif msg.startswith("UPDATE"):
            # Extrai tudo que vem após "UPDATE ", preservando espaços
            state = msg[len("UPDATE "):]
            print("Tabuleiro atualizado:")
            for i in range(0, 9, 3):
                print("|".join(state[i:i+3]))
            print()

        elif msg == "YOUR_TURN":
            while True:
                try:
                    move = int(input("Sua jogada (0-8): ").strip())
                except ValueError:
                    print("Digite um número de 0 a 8.")
                    continue
                if move < 0 or move > 8:
                    print("Posição inválida. Tente novamente.")
                    continue
                break
            sock.sendall(f"MOVE {move}".encode())

        elif msg.startswith("END"):
            parts = msg.split()
            if parts[1] == "WINNER":
                winner = parts[2]
                if winner == marker:
                    print("Você venceu a partida!")
                else:
                    print("Você perdeu! O oponente venceu.")
            else:
                print("Empate!")
            break

        elif msg == "INVALID":
            print("Jogada inválida, tente outra posição.")

        else:
            print("Mensagem inesperada do servidor:", msg)

    sock.close()
    input("\nPressione Enter para retornar ao menu...")

def main():
    while True:
        print("\n=== JOGO DA VELHA ===")
        print("1. Jogar vs Máquina")
        print("2. Jogar vs Cliente (rede)")
        print("3. Sair")
        escolha = input("Escolha sua opção: ").strip()

        if escolha == '1':
            play_vs_machine()
        elif escolha == '2':
            play_vs_network()
        elif escolha == '3':
            print("Saindo do programa. Até mais!")
            sys.exit(0)
        else:
            print("Opção inválida. Digite 1, 2 ou 3.")

if __name__ == "__main__":
    main()
