def create_board():
    return [' '] * 9  # 0..8 posições

def print_board(b):
    # Apenas para debug no servidor
    for i in range(0, 9, 3):
        print("|".join(b[i:i+3]))
    print()

def is_winner(b, marker):
    wins = [
        (0,1,2), (3,4,5), (6,7,8),
        (0,3,6), (1,4,7), (2,5,8),
        (0,4,8), (2,4,6)
    ]
    for (x, y, z) in wins:
        if b[x] == b[y] == b[z] == marker:
            return True
    return False


def is_draw(b):
    return all(cell != ' ' for cell in b)
