import main

def print_board(board):
    for y in range(main.BOARD_SIZE):
        row = []
        for x in range(main.BOARD_SIZE):
            value = board[x][y]
            if value is None:
                row.append("None")
            else:
                row.append(str(value).ljust(4))
        print(' '.join(row))

game = main.SlidingPuzzle()
print('Solved board:')
print_board(game.solved_board)
