import pygame
import sys
import random

# --- 設定と初期化 ---
pygame.init()
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
CELL_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("テトリスゲーム")
clock = pygame.time.Clock()

# 色の定義
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# テトリミノの形状
TETROMINOS = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(1, 1), (2, 1), (1, 2), (2, 2)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "S": [(1, 1), (2, 1), (0, 2), (1, 2)],
    "Z": [(0, 1), (1, 1), (1, 2), (2, 2)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}

# --- クラス定義 ---
class Block:
    def __init__(self, shape):
        self.shape = TETROMINOS[shape]
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.x = GRID_WIDTH // 2 - 2
        self.y = 0

    def rotate(self):
        self.shape = [(y, -x) for x, y in self.shape]

    def draw(self, surface):
        for pos in self.shape:
            pygame.draw.rect(
                surface, self.color,
                ((self.x + pos[0]) * CELL_SIZE, (self.y + pos[1]) * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            )

# --- ヘルパー関数 ---
def get_new_block():
    return Block(random.choice(list(TETROMINOS.keys())))

def check_collision(block, grid):
    for pos in block.shape:
        x, y = block.x + pos[0], block.y + pos[1]
        if x < 0 or x >= GRID_WIDTH or y >= GRID_HEIGHT:
            return True
        if y >= 0 and grid[y][x]:
            return True
    return False

def clear_lines(grid):
    lines_to_clear = [y for y, row in enumerate(grid) if all(row)]
    for y in lines_to_clear:
        del grid[y]
        grid.insert(0, [0 for _ in range(GRID_WIDTH)])
    return len(lines_to_clear)

def draw_text_center(text, size, color, y_offset):
    font = pygame.font.SysFont("Arial", size, bold=True)
    rendered_text = font.render(text, True, color)
    rect = rendered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
    screen.blit(rendered_text, rect)

# --- 各画面の処理 ---
def show_title():
    screen.fill(BLACK)
    draw_text_center("TETRIS", 50, WHITE, -100)
    draw_text_center("Press SPACE to Start", 20, WHITE, 20)
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: return "QUIT"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return "PLAYING"
    return "TITLE"

def show_game_over(score):
    screen.fill(BLACK)
    draw_text_center("GAME OVER", 40, RED, -50)
    draw_text_center(f"Score: {score}", 30, WHITE, 10)
    draw_text_center("Press R to Title", 20, GRAY, 80)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: return "QUIT"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return "TITLE"
    return "GAMEOVER"

def show_clear(score):
    screen.fill(BLACK)
    draw_text_center("GAME CLEAR!", 40, GOLD, -50)
    draw_text_center(f"Final Score: {score}", 30, WHITE, 10)
    draw_text_center("Press R to Title", 20, GRAY, 80)
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: return "QUIT"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            return "TITLE"
    return "CLEAR"

# --- メインループ管理 ---
def main():
    state = "TITLE"
    score = 0
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    current_block = get_new_block()
    
    # タイマー
    MOVE_DOWN = pygame.USEREVENT + 1
    pygame.time.set_timer(MOVE_DOWN, 500)

    while True:
        if state == "TITLE":
            res = show_title()
            if res == "PLAYING": # 初期化
                grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                score = 0
                current_block = get_new_block()
            state = res

        elif state == "GAMEOVER":
            state = show_game_over(score)

        elif state == "CLEAR":
            state = show_clear(score)

        elif state == "PLAYING":
            screen.fill(WHITE)
            
            # グリッド描画
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                
                if event.type == MOVE_DOWN:
                    current_block.y += 1
                    if check_collision(current_block, grid):
                        current_block.y -= 1
                        for pos in current_block.shape:
                            grid[current_block.y + pos[1]][current_block.x + pos[0]] = current_block.color
                        score += clear_lines(grid) * 100
                        current_block = get_new_block()
                        # 出現即衝突でゲームオーバー
                        if check_collision(current_block, grid):
                            state = "GAMEOVER"
                        # 1000点でクリア判定（例）
                        if score >= 1000:
                            state = "CLEAR"

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        current_block.x -= 1
                        if check_collision(current_block, grid): current_block.x += 1
                    if event.key == pygame.K_RIGHT:
                        current_block.x += 1
                        if check_collision(current_block, grid): current_block.x -= 1
                    if event.key == pygame.K_DOWN:
                        current_block.y += 1
                        if check_collision(current_block, grid): current_block.y -= 1
                    if event.key == pygame.K_SPACE:
                        current_block.rotate()
                        if check_collision(current_block, grid):
                            for _ in range(3): current_block.rotate()

            # ブロックと固定済みブロックの描画
            for y, row in enumerate(grid):
                for x, color in enumerate(row):
                    if color:
                        pygame.draw.rect(screen, color, (x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
            current_block.draw(screen)

            # スコア表示
            draw_text_center(f"Score: {score}", 20, BLACK, -280)
            pygame.display.update()

        elif state == "QUIT":
            break
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
