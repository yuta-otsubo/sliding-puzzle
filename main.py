import pygame
import sys
import random
from pygame.locals import *
import amazon_style

# 定数
BOARD_SIZE = 4
TILE_SIZE = 100
WINDOW_WIDTH = BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * TILE_SIZE + 50  # ボタン用の余白
FPS = 30

# 方向定数
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

class SlidingPuzzle:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display_surf = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Amazon スライドパズル')
        self.basic_font = pygame.font.SysFont('Arial', 20)
        self.title_font = pygame.font.SysFont('Arial', 30, bold=True)
        
        # Amazonスタイルの背景
        self.background = amazon_style.create_amazon_background(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # ボタンの設定
        self.reset_button = amazon_style.create_amazon_button(100, 30, 'リセット', self.basic_font)
        self.reset_rect = self.reset_button.get_rect(topleft=(10, WINDOW_HEIGHT - 40))
        
        self.new_button = amazon_style.create_amazon_button(100, 30, '新規', self.basic_font)
        self.new_rect = self.new_button.get_rect(topleft=(120, WINDOW_HEIGHT - 40))
        
        self.solve_button = amazon_style.create_amazon_button(100, 30, '解く', self.basic_font)
        self.solve_rect = self.solve_button.get_rect(topleft=(230, WINDOW_HEIGHT - 40))
        
        # Amazonロゴ
        self.logo = amazon_style.create_amazon_logo(100, 30)
        self.logo_rect = self.logo.get_rect(topleft=(WINDOW_WIDTH - 110, WINDOW_HEIGHT - 40))
        
        # タイルの画像を事前に生成
        self.tile_images = {}
        for i in range(1, BOARD_SIZE * BOARD_SIZE):
            self.tile_images[i] = amazon_style.create_amazon_tile(TILE_SIZE, i, self.basic_font)
        
        # ボードの初期化
        self.solved_board = self.get_starting_board()
        self.main_board = self.get_starting_board()  # 先に初期化
        self.all_moves = []
        self.main_board, self.solution_seq = self.generate_new_puzzle(80)
    
    def get_starting_board(self):
        # 解決された状態のボードを返す
        counter = 1
        board = []
        for x in range(BOARD_SIZE):
            column = []
            for y in range(BOARD_SIZE):
                if counter == BOARD_SIZE * BOARD_SIZE:
                    column.append(None)
                else:
                    column.append(counter)
                counter += 1
            board.append(column)
        return board
    
    def get_blank_position(self, board):
        # 空白の位置を返す
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if board[x][y] is None:
                    return (x, y)
        return None
    
    def make_move(self, board, move):
        # 指定された方向に移動
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
        # 指定された方向への移動が有効かどうかをチェック
        blankx, blanky = self.get_blank_position(board)
        return (move == UP and blanky != BOARD_SIZE - 1) or \
               (move == DOWN and blanky != 0) or \
               (move == LEFT and blankx != BOARD_SIZE - 1) or \
               (move == RIGHT and blankx != 0)
    
    def get_random_move(self, board, last_move=None):
        # ランダムな移動を取得（前回の移動と逆の移動は避ける）
        valid_moves = [UP, DOWN, LEFT, RIGHT]
        
        # 前回の移動と逆の移動を削除
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
        # クリックされた位置のタイルを取得
        for tilex in range(BOARD_SIZE):
            for tiley in range(BOARD_SIZE):
                left, top = self.get_left_top_of_tile(tilex, tiley)
                tile_rect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
                if tile_rect.collidepoint(x, y):
                    return (tilex, tiley)
        return (None, None)
    
    def get_left_top_of_tile(self, tilex, tiley):
        # タイルの左上の座標を取得
        left = tilex * TILE_SIZE
        top = tiley * TILE_SIZE
        return (left, top)
    
    def draw_board(self, message):
        # 背景を描画
        self.display_surf.blit(self.background, (0, 0))
        
        # ボードを描画
        for tilex in range(BOARD_SIZE):
            for tiley in range(BOARD_SIZE):
                if self.main_board and self.main_board[tilex][tiley]:
                    left, top = self.get_left_top_of_tile(tilex, tiley)
                    self.display_surf.blit(self.tile_images[self.main_board[tilex][tiley]], (left, top))
        
        # ボードの枠線
        left, top = self.get_left_top_of_tile(0, 0)
        width = BOARD_SIZE * TILE_SIZE
        height = BOARD_SIZE * TILE_SIZE
        pygame.draw.rect(self.display_surf, amazon_style.AMAZON_ORANGE, (left - 2, top - 2, width + 4, height + 4), 2)
        
        # メッセージを描画
        if message:
            text_surf = self.title_font.render(message, True, amazon_style.AMAZON_ORANGE)
            text_rect = text_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
            self.display_surf.blit(text_surf, text_rect)
        
        # ボタンを描画
        self.display_surf.blit(self.reset_button, self.reset_rect)
        self.display_surf.blit(self.new_button, self.new_rect)
        self.display_surf.blit(self.solve_button, self.solve_rect)
        self.display_surf.blit(self.logo, self.logo_rect)
    
    def slide_animation(self, direction, message, animation_speed):
        # タイルのスライドアニメーション
        blankx, blanky = self.get_blank_position(self.main_board)
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
        
        # アニメーションの準備
        self.draw_board(message)
        base_surf = self.display_surf.copy()
        
        # 移動するタイル
        move_tile = self.main_board[movex][movey]
        move_left, move_top = self.get_left_top_of_tile(movex, movey)
        
        for i in range(0, TILE_SIZE, animation_speed):
            # アニメーションフレームを描画
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
        # 新しいパズルを生成
        sequence = []
        board = self.get_starting_board()
        
        # 初期状態のボードを設定
        self.main_board = board
        
        self.draw_board('')
        pygame.display.update()
        pygame.time.wait(500)
        last_move = None
        
        for i in range(num_slides):
            move = self.get_random_move(board, last_move)
            if move is None:
                # 有効な移動がない場合はスキップ
                continue
            self.slide_animation(move, 'パズル生成中...', int(TILE_SIZE / 3))
            self.make_move(board, move)
            sequence.append(move)
            last_move = move
        
        return (board, sequence)
    
    def reset_animation(self, all_moves):
        # リセットアニメーション
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
        # メインゲームループ
        running = True
        msg = ''
        
        while running:
            slide_to = None
            
            # ボードが解かれたかチェック
            if self.main_board == self.solved_board:
                msg = 'クリア!'
            
            self.draw_board(msg)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == MOUSEBUTTONUP:
                    spotx, spoty = self.get_spot_clicked(event.pos[0], event.pos[1])
                    
                    if (spotx, spoty) == (None, None):
                        # ボタンがクリックされたかチェック
                        if self.reset_rect.collidepoint(event.pos):
                            self.reset_animation(self.all_moves)
                            self.all_moves = []
                            msg = ''
                        elif self.new_rect.collidepoint(event.pos):
                            self.main_board, self.solution_seq = self.generate_new_puzzle(80)
                            self.all_moves = []
                            msg = ''
                        elif self.solve_rect.collidepoint(event.pos):
                            self.reset_animation(self.solution_seq + self.all_moves)
                            self.all_moves = []
                            msg = ''
                    else:
                        # タイルがクリックされた
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
                    # キーボード入力
                    if event.key in (K_LEFT, K_a) and self.is_valid_move(self.main_board, LEFT):
                        slide_to = LEFT
                    elif event.key in (K_RIGHT, K_d) and self.is_valid_move(self.main_board, RIGHT):
                        slide_to = RIGHT
                    elif event.key in (K_UP, K_w) and self.is_valid_move(self.main_board, UP):
                        slide_to = UP
                    elif event.key in (K_DOWN, K_s) and self.is_valid_move(self.main_board, DOWN):
                        slide_to = DOWN
                    elif event.key == K_r:
                        # リセット
                        self.main_board, self.solution_seq = self.generate_new_puzzle(80)
                        self.all_moves = []
                        msg = ''
                    elif event.key == K_ESCAPE:
                        running = False
            
            if slide_to:
                self.slide_animation(slide_to, '', 8)
                self.make_move(self.main_board, slide_to)
                self.all_moves.append(slide_to)
                msg = ''  # 移動したらメッセージをクリア
            
            pygame.display.update()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = SlidingPuzzle()
    game.run()
