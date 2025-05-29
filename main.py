import pygame
import sys
import random
from pygame.locals import *
import amazon_style

# Constants
BOARD_SIZE = 4
TILE_SIZE = 100
WINDOW_WIDTH = BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * TILE_SIZE + 100  # Extra space for buttons and message
FPS = 30

# Direction constants
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

class SlidingPuzzle:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Amazon Sliding Puzzle')
        self.basic_font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 30, bold=True)

        # Amazon style background
        self.background = amazon_style.create_amazon_background(WINDOW_WIDTH, WINDOW_HEIGHT)

        # Button setup
        button_width = 90  # 少し小さくして3つのボタンが等間隔で配置できるようにする
        button_spacing = (WINDOW_WIDTH - (button_width * 3)) // 4  # 等間隔の計算
        button_y = WINDOW_HEIGHT - 80  # ボタンの位置をさらに上にずらす

        self.reset_button = amazon_style.create_amazon_button(button_width, 30, 'Reset', self.basic_font)
        self.reset_rect = self.reset_button.get_rect(topleft=(button_spacing, button_y))

        self.new_button = amazon_style.create_amazon_button(button_width, 30, 'New', self.basic_font)
        self.new_rect = self.new_button.get_rect(topleft=(button_spacing * 2 + button_width, button_y))

        self.solve_button = amazon_style.create_amazon_button(button_width, 30, 'Solve', self.basic_font)
        self.solve_rect = self.solve_button.get_rect(topleft=(button_spacing * 3 + button_width * 2, button_y))

        # Amazon logo
        self.logo = amazon_style.create_amazon_logo(100, 30)
        self.logo_rect = self.logo.get_rect(topleft=(WINDOW_WIDTH - 110, WINDOW_HEIGHT - 30))

        # Pre-generate tile images
        self.tile_images = {}
        for i in range(1, BOARD_SIZE * BOARD_SIZE):
            self.tile_images[i] = amazon_style.create_amazon_tile(TILE_SIZE, i, self.basic_font)

        # Initialize board
        self.solved_board = self.get_starting_board()
        self.main_board = self.get_starting_board()  # Initialize first
        self.all_moves = []
        self.main_board, self.solution_seq = self.generate_new_puzzle(80)

    def get_starting_board(self):
        # Return a solved board - 左上から右へ、そして下へと1,2,3...と番号を振る
        board = []
        for x in range(BOARD_SIZE):
            column = []
            for y in range(BOARD_SIZE):
                # 一番右下を空白にする
                if x == BOARD_SIZE - 1 and y == BOARD_SIZE - 1:
                    column.append(None)
                else:
                    # 左から右、上から下に1,2,3...と番号を振る
                    # y*BOARD_SIZE + x + 1 は行優先で番号を振る
                    number = y * BOARD_SIZE + x + 1
                    column.append(number)
            board.append(column)
        return board

    def get_blank_position(self, board):
        # Return the position of the blank space
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if board[x][y] is None:
                    return (x, y)
        return None

    def make_move(self, board, move):
        # Make the specified move
        blankx, blanky = self.get_blank_position(board)

        if move == UP:
            board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
        elif move == DOWN:
            board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
        elif move == LEFT:
            board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
        elif move == RIGHT:
            board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

    def is_valid_move(self, board, move):
        # Check if the specified move is valid
        blankx, blanky = self.get_blank_position(board)
        return (move == UP and blanky != BOARD_SIZE - 1) or \
               (move == DOWN and blanky != 0) or \
               (move == LEFT and blankx != BOARD_SIZE - 1) or \
               (move == RIGHT and blankx != 0)

    def get_random_move(self, board, last_move=None):
        # Get a random move (avoiding the opposite of the last move)
        valid_moves = [UP, DOWN, LEFT, RIGHT]

        # Remove the opposite of the last move
        if last_move == UP or not self.is_valid_move(board, DOWN):
            if DOWN in valid_moves:
                valid_moves.remove(DOWN)
        if last_move == DOWN or not self.is_valid_move(board, UP):
            if UP in valid_moves:
                valid_moves.remove(UP)
        if last_move == LEFT or not self.is_valid_move(board, RIGHT):
            if RIGHT in valid_moves:
                valid_moves.remove(RIGHT)
        if last_move == RIGHT or not self.is_valid_move(board, LEFT):
            if LEFT in valid_moves:
                valid_moves.remove(LEFT)

        if not valid_moves:
            return None

        return random.choice(valid_moves)

    def get_spot_clicked(self, x, y):
        # Get the tile clicked
        for tilex in range(BOARD_SIZE):
            for tiley in range(BOARD_SIZE):
                left, top = self.get_left_top_of_tile(tilex, tiley)
                tile_rect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
                if tile_rect.collidepoint(x, y):
                    return (tilex, tiley)
        return (None, None)

    def get_left_top_of_tile(self, tilex, tiley):
        # Get the top left coordinates of a tile
        left = tilex * TILE_SIZE
        top = tiley * TILE_SIZE
        return (left, top)

    def draw_board(self, message):
        # Draw the background
        self.display_surf.blit(self.background, (0, 0))

        # Draw the board
        for tilex in range(BOARD_SIZE):
            for tiley in range(BOARD_SIZE):
                if self.main_board and self.main_board[tilex][tiley]:
                    left, top = self.get_left_top_of_tile(tilex, tiley)
                    self.display_surf.blit(self.tile_images[self.main_board[tilex][tiley]], (left, top))

        # Draw the board border
        left, top = self.get_left_top_of_tile(0, 0)
        width = BOARD_SIZE * TILE_SIZE
        height = BOARD_SIZE * TILE_SIZE
        pygame.draw.rect(self.display_surf, amazon_style.AMAZON_ORANGE, (left - 2, top - 2, width + 4, height + 4), 2)

        # Draw the message and logo
        if message:
            text_surf = self.title_font.render(message, True, amazon_style.AMAZON_ORANGE)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))

            # 背景を追加して文字を見やすくする
            padding = 5
            bg_rect = pygame.Rect(text_rect.left - padding, text_rect.top - padding,
                                 text_rect.width + padding * 2, text_rect.height + padding * 2)
            pygame.draw.rect(self.display_surf, amazon_style.AMAZON_BLUE, bg_rect)
            pygame.draw.rect(self.display_surf, amazon_style.AMAZON_ORANGE, bg_rect, 1)

            self.display_surf.blit(text_surf, text_rect)

        # Draw the logo
        self.display_surf.blit(self.logo, self.logo_rect)

        # Draw the buttons
        self.display_surf.blit(self.reset_button, self.reset_rect)
        self.display_surf.blit(self.new_button, self.new_rect)
        self.display_surf.blit(self.solve_button, self.solve_rect)

    def slide_animation(self, direction, message, animation_speed):
        # Slide animation for tiles
        blankx, blanky = self.get_blank_position(self.main_board)

        # Check if the move is valid
        if direction == UP and blanky >= BOARD_SIZE - 1:
            return  # Invalid move
        elif direction == DOWN and blanky <= 0:
            return  # Invalid move
        elif direction == LEFT and blankx >= BOARD_SIZE - 1:
            return  # Invalid move
        elif direction == RIGHT and blankx <= 0:
            return  # Invalid move

        if direction == UP:
            movex = blankx
            movey = blanky + 1
        elif direction == DOWN:
            movex = blankx
            movey = blanky - 1
        elif direction == LEFT:
            movex = blankx + 1
            movey = blanky
        elif direction == RIGHT:
            movex = blankx - 1
            movey = blanky

        # Additional boundary check
        if movex < 0 or movex >= BOARD_SIZE or movey < 0 or movey >= BOARD_SIZE:
            return  # Out of bounds

        # Prepare for animation
        self.draw_board(message)
        base_surf = self.display_surf.copy()

        # Moving tile
        move_tile = self.main_board[movex][movey]
        move_left, move_top = self.get_left_top_of_tile(movex, movey)

        for i in range(0, TILE_SIZE, animation_speed):
            # Draw animation frame
            self.display_surf.blit(base_surf, (0, 0))

            if direction == UP:
                self.display_surf.blit(self.tile_images[move_tile], (move_left, move_top - i))
            elif direction == DOWN:
                self.display_surf.blit(self.tile_images[move_tile], (move_left, move_top + i))
            elif direction == LEFT:
                self.display_surf.blit(self.tile_images[move_tile], (move_left - i, move_top))
            elif direction == RIGHT:
                self.display_surf.blit(self.tile_images[move_tile], (move_left + i, move_top))

            pygame.display.update()
            self.clock.tick(FPS)

    def generate_new_puzzle(self, num_slides):
        # Generate a new puzzle
        sequence = []
        board = self.get_starting_board()

        # Set initial board state
        self.main_board = board

        self.draw_board('')
        pygame.display.update()
        pygame.time.wait(500)
        last_move = None

        for i in range(num_slides):
            move = self.get_random_move(board, last_move)
            if move is None:
                # Skip if no valid moves
                continue
            self.slide_animation(move, 'Generating puzzle...', int(TILE_SIZE / 3))
            self.make_move(board, move)
            sequence.append(move)
            last_move = move

        return (board, sequence)

    def reset_animation(self, all_moves):
        # Reset animation
        rev_all_moves = all_moves[:]
        rev_all_moves.reverse()

        for move in rev_all_moves:
            if move == UP:
                opposite_move = DOWN
            elif move == DOWN:
                opposite_move = UP
            elif move == RIGHT:
                opposite_move = LEFT
            elif move == LEFT:
                opposite_move = RIGHT
            self.slide_animation(opposite_move, '', int(TILE_SIZE / 2))
            self.make_move(self.main_board, opposite_move)

    def run(self):
        # Main game loop
        running = True
        msg = ''

        # カーソルの状態を追跡する変数
        cursor_on_button = False

        while running:
            slide_to = None

            # Check if the board is solved
            if self.main_board == self.solved_board:
                msg = 'Solved!'

            self.draw_board(msg)

            # マウスの位置を取得
            mouse_pos = pygame.mouse.get_pos()

            # ボタンの上にマウスがあるかチェック
            if (self.reset_rect.collidepoint(mouse_pos) or 
                self.new_rect.collidepoint(mouse_pos) or 
                self.solve_rect.collidepoint(mouse_pos)):
                if not cursor_on_button:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # 指差しカーソルに変更
                    cursor_on_button = True
            else:
                if cursor_on_button:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)  # 通常のカーソルに戻す
                    cursor_on_button = False

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONUP:
                    spotx, spoty = self.get_spot_clicked(event.pos[0], event.pos[1])

                    if (spotx, spoty) == (None, None):
                        # Check if buttons were clicked
                        if self.reset_rect.collidepoint(event.pos):
                            self.reset_animation(self.all_moves)
                            self.all_moves = []
                            msg = ''
                        elif self.new_rect.collidepoint(event.pos):
                            self.main_board, self.solution_seq = self.generate_new_puzzle(80)
                            self.all_moves = []
                            msg = ''
                        elif self.solve_rect.collidepoint(event.pos):
                            try:
                                # パズルを直接解決された状態に設定
                                self.main_board = self.get_starting_board()
                                # アニメーションで解決を表示
                                self.draw_board('Solving...')
                                pygame.display.update()
                                pygame.time.wait(500)
                                self.all_moves = []
                                msg = 'Solved!'
                            except Exception as e:
                                print(f"Error during solve: {e}")
                                msg = 'Solve failed'
                    else:
                        # Tile was clicked
                        blankx, blanky = self.get_blank_position(self.main_board)
                        if spotx == blankx + 1 and spoty == blanky:
                            slide_to = LEFT
                        elif spotx == blankx - 1 and spoty == blanky:
                            slide_to = RIGHT
                        elif spotx == blankx and spoty == blanky + 1:
                            slide_to = UP
                        elif spotx == blankx and spoty == blanky - 1:
                            slide_to = DOWN

                elif event.type == KEYUP:
                    # Keyboard input
                    if event.key in (K_LEFT, K_a) and self.is_valid_move(self.main_board, LEFT):
                        slide_to = LEFT
                    elif event.key in (K_RIGHT, K_d) and self.is_valid_move(self.main_board, RIGHT):
                        slide_to = RIGHT
                    elif event.key in (K_UP, K_w) and self.is_valid_move(self.main_board, UP):
                        slide_to = UP
                    elif event.key in (K_DOWN, K_s) and self.is_valid_move(self.main_board, DOWN):
                        slide_to = DOWN
                    elif event.key == K_r:
                        # Reset
                        self.main_board, self.solution_seq = self.generate_new_puzzle(80)
                        self.all_moves = []
                        msg = ''
                    elif event.key == K_ESCAPE:
                        running = False

            if slide_to:
                self.slide_animation(slide_to, '', 8)
                self.make_move(self.main_board, slide_to)
                self.all_moves.append(slide_to)
                msg = ''  # Clear message after move

            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = SlidingPuzzle()
    game.run()
