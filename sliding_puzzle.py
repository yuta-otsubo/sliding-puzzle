import pygame
import sys
import random
from pygame.locals import *

# 定数
BOARD_SIZE = 4
TILE_SIZE = 100
WINDOW_WIDTH = BOARD_SIZE * TILE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * TILE_SIZE
FPS = 30
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)  # Amazonカラー

# メイン関数
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT, SOLVE_SURF, SOLVE_RECT
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('スライドパズル')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 20)
    
    # ボタンの設定
    RESET_SURF, RESET_RECT = makeText('リセット', BLUE, WHITE, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 90)
    NEW_SURF, NEW_RECT = makeText('新規', BLUE, WHITE, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 60)
    SOLVE_SURF, SOLVE_RECT = makeText('解く', BLUE, WHITE, WINDOW_WIDTH - 120, WINDOW_HEIGHT - 30)
    
    # ボードの初期化
    main_board, solution_seq = generateNewPuzzle(80)
    SOLVEDBOARD = getStartingBoard()
    all_moves = []
    
    while True:  # メインゲームループ
        slideTo = None
        msg = ''
        
        # ボードが解かれたかチェック
        if main_board == SOLVEDBOARD:
            msg = 'クリア!'
        
        drawBoard(main_board, msg)
        
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(main_board, event.pos[0], event.pos[1])
                
                if (spotx, spoty) == (None, None):
                    # ボタンがクリックされたかチェック
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(main_board, all_moves)
                        all_moves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        main_board, solution_seq = generateNewPuzzle(80)
                        all_moves = []
                    elif SOLVE_RECT.collidepoint(event.pos):
                        resetAnimation(main_board, solution_seq + all_moves)
                        all_moves = []
                else:
                    # タイルがクリックされた
                    blankx, blanky = getBlankPosition(main_board)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN
            
            elif event.type == KEYUP:
                # キーボード入力
                if event.key in (K_LEFT, K_a) and isValidMove(main_board, LEFT):
                    slideTo = LEFT
                elif event.key in (K_RIGHT, K_d) and isValidMove(main_board, RIGHT):
                    slideTo = RIGHT
                elif event.key in (K_UP, K_w) and isValidMove(main_board, UP):
                    slideTo = UP
                elif event.key in (K_DOWN, K_s) and isValidMove(main_board, DOWN):
                    slideTo = DOWN
                elif event.key == K_r:
                    # リセット
                    main_board, solution_seq = generateNewPuzzle(80)
                    all_moves = []
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        if slideTo:
            slideAnimation(main_board, slideTo, 'タイルをスライド', 8)
            makeMove(main_board, slideTo)
            all_moves.append(slideTo)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def makeText(text, color, bgcolor, top, left):
    # テキストオブジェクトを作成
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

def getStartingBoard():
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

def getBlankPosition(board):
    # 空白の位置を返す
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            if board[x][y] is None:
                return (x, y)

def makeMove(board, move):
    # 指定された方向に移動
    blankx, blanky = getBlankPosition(board)
    
    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]

def isValidMove(board, move):
    # 指定された方向への移動が有効かどうかをチェック
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != BOARD_SIZE - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != BOARD_SIZE - 1) or \
           (move == RIGHT and blankx != 0)

def getRandomMove(board, lastMove=None):
    # ランダムな移動を取得（前回の移動と逆の移動は避ける）
    validMoves = [UP, DOWN, LEFT, RIGHT]
    
    # 前回の移動と逆の移動を削除
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)
    
    return random.choice(validMoves)

def getSpotClicked(board, x, y):
    # クリックされた位置のタイルを取得
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)

def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    # タイルを描画
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, ORANGE, (left + adjx, top + adjy, TILE_SIZE, TILE_SIZE))
    textSurf = BASICFONT.render(str(number), True, WHITE)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILE_SIZE / 2) + adjx, top + int(TILE_SIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)

def getLeftTopOfTile(tilex, tiley):
    # タイルの左上の座標を取得
    left = tilex * TILE_SIZE
    top = tiley * TILE_SIZE
    return (left, top)

def drawBoard(board, message):
    # ボードを描画
    DISPLAYSURF.fill(BLACK)
    
    if message:
        textSurf, textRect = makeText(message, WHITE, BLACK, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)
    
    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])
    
    left, top = getLeftTopOfTile(0, 0)
    width = BOARD_SIZE * TILE_SIZE
    height = BOARD_SIZE * TILE_SIZE
    pygame.draw.rect(DISPLAYSURF, BLACK, (left - 5, top - 5, width + 11, height + 11), 4)

def slideAnimation(board, direction, message, animationSpeed):
    # タイルのスライドアニメーション
    blankx, blanky = getBlankPosition(board)
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
    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    
    # タイルを空白にする
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BLACK, (moveLeft, moveTop, TILE_SIZE, TILE_SIZE))
    
    for i in range(0, TILE_SIZE, animationSpeed):
        # アニメーションフレームを描画
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        elif direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        elif direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        elif direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generateNewPuzzle(numSlides):
    # 新しいパズルを生成
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500)
    lastMove = None
    
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'パズル生成中...', int(TILE_SIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    
    return (board, sequence)

def resetAnimation(board, allMoves):
    # リセットアニメーション
    revAllMoves = allMoves[:]
    revAllMoves.reverse()
    
    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', int(TILE_SIZE / 2))
        makeMove(board, oppositeMove)

# 方向定数
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

if __name__ == '__main__':
    main()
