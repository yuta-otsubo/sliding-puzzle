import pygame
import os

# Amazonカラー
AMAZON_ORANGE = (255, 153, 0)  # Amazon's orange color
AMAZON_BLUE = (35, 47, 62)     # Amazon's dark blue color
AMAZON_LIGHT_BLUE = (0, 119, 182)  # Amazon's light blue color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def create_amazon_tile(size, number, font):
    """
    Amazonスタイルのタイルを作成する
    """
    # タイルのサーフェスを作成
    tile_surf = pygame.Surface((size, size))
    
    # グラデーション効果
    for i in range(size):
        color_value = 255 - int(i * 0.5)
        if color_value < 0:
            color_value = 0
        pygame.draw.rect(tile_surf, (color_value, color_value, color_value), (0, i, size, 1))
    
    # タイルの枠線
    pygame.draw.rect(tile_surf, AMAZON_ORANGE, (0, 0, size, size), 2)
    
    # 数字を描画
    if number is not None:
        text_surf = font.render(str(number), True, WHITE)
        text_rect = text_surf.get_rect(center=(size // 2, size // 2))
        
        # 数字の背景円
        pygame.draw.circle(tile_surf, AMAZON_BLUE, (size // 2, size // 2), size // 4)
        tile_surf.blit(text_surf, text_rect)
    
    # Amazonスマイルのような曲線を描画
    start_pos = (size // 5, size * 3 // 4)
    end_pos = (size * 4 // 5, size * 3 // 4)
    control_point = (size // 2, size * 7 // 8)
    
    points = []
    for t in range(0, 101, 5):
        t = t / 100
        # 二次ベジェ曲線の計算
        x = (1-t)**2 * start_pos[0] + 2*(1-t)*t * control_point[0] + t**2 * end_pos[0]
        y = (1-t)**2 * start_pos[1] + 2*(1-t)*t * control_point[1] + t**2 * end_pos[1]
        points.append((int(x), int(y)))
    
    if len(points) > 1:
        pygame.draw.lines(tile_surf, AMAZON_ORANGE, False, points, 2)
    
    return tile_surf

def create_amazon_background(width, height):
    """
    Amazonスタイルの背景を作成する
    """
    bg_surf = pygame.Surface((width, height))
    bg_surf.fill(AMAZON_BLUE)
    
    # 背景にAmazonスタイルのパターンを追加
    for i in range(0, width, 20):
        pygame.draw.line(bg_surf, (45, 57, 72), (i, 0), (i, height), 1)
    
    for i in range(0, height, 20):
        pygame.draw.line(bg_surf, (45, 57, 72), (0, i), (width, i), 1)
    
    return bg_surf

def create_amazon_button(width, height, text, font):
    """
    Amazonスタイルのボタンを作成する
    """
    button_surf = pygame.Surface((width, height))
    button_surf.fill(AMAZON_ORANGE)
    
    # ボタンの枠線
    pygame.draw.rect(button_surf, WHITE, (0, 0, width, height), 1)
    
    # テキストを描画
    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(width // 2, height // 2))
    button_surf.blit(text_surf, text_rect)
    
    return button_surf

def create_amazon_logo(width, height):
    """
    シンプルなAmazonロゴを作成する
    """
    logo_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # "amazon" テキスト
    font = pygame.font.SysFont('Arial', height // 2, bold=True)
    text_surf = font.render("amazon", True, AMAZON_ORANGE)
    text_rect = text_surf.get_rect(center=(width // 2, height // 2))
    logo_surf.blit(text_surf, text_rect)
    
    # スマイル
    start_pos = (width // 4, height * 2 // 3)
    end_pos = (width * 3 // 4, height * 2 // 3)
    control_point = (width // 2, height * 5 // 6)
    
    points = []
    for t in range(0, 101, 5):
        t = t / 100
        # 二次ベジェ曲線の計算
        x = (1-t)**2 * start_pos[0] + 2*(1-t)*t * control_point[0] + t**2 * end_pos[0]
        y = (1-t)**2 * start_pos[1] + 2*(1-t)*t * control_point[1] + t**2 * end_pos[1]
        points.append((int(x), int(y)))
    
    if len(points) > 1:
        pygame.draw.lines(logo_surf, AMAZON_ORANGE, False, points, 2)
    
    # 矢印
    arrow_start = points[0]
    arrow_end = (arrow_start[0] + 10, arrow_start[1] - 5)
    pygame.draw.line(logo_surf, AMAZON_ORANGE, arrow_start, arrow_end, 2)
    
    return logo_surf
