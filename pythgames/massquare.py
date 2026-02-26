import pygame
import random
import sys

# --- 初始化 ---
pygame.init()

# --- 常量设置 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 颜色定义 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)   # 玩家颜色
RED = (255, 0, 0)     # 敌人颜色

# 游戏设置
PLAYER_SIZE = 50
PLAYER_SPEED = 7
ENEMY_SIZE = 40
ENEMY_SPEED = 5
ENEMY_SPAWN_RATE = 30  # 敌人生成频率 (帧数间隔)
WIN_TIME = 180         # 胜利所需时间 (秒)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("绿色方块生存挑战 (WASD 版)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36)
big_font = pygame.font.SysFont("arial", 72)

# --- 函数定义 ---

def draw_text(text, font, color, x, y, center=False):
    """辅助函数：在屏幕上绘制文字"""
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

def reset_game():
    """重置游戏状态"""
    player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
    player_y = SCREEN_HEIGHT - 100  # 初始位置在下方
    enemies = []
    start_ticks = pygame.time.get_ticks()
    state = "PLAYING" # 状态：PLAYING, WIN, GAMEOVER
    return player_x, player_y, enemies, start_ticks, state

# --- 主程序 ---

def main():
    # 初始化游戏变量
    player_x, player_y, enemies, start_ticks, state = reset_game()
    spawn_timer = 0
    running = True

    while running:
        # 1. 控制帧率
        clock.tick(FPS)
        
        # 2. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and state != "PLAYING":
                    # 按 R 键重新开始
                    player_x, player_y, enemies, start_ticks, state = reset_game()

        # 3. 游戏逻辑更新
        if state == "PLAYING":
            # --- 玩家移动 (WASD + 方向键) ---
            keys = pygame.key.get_pressed()
            
            # 左右移动 (A 键 或 左箭头)
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_x > 0:
                player_x -= PLAYER_SPEED
            # 左右移动 (D 键 或 右箭头)
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_x < SCREEN_WIDTH - PLAYER_SIZE:
                player_x += PLAYER_SPEED
            
            # 上下移动 (W 键 或 上箭头)
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and player_y > 0:
                player_y -= PLAYER_SPEED
            # 上下移动 (S 键 或 下箭头)
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player_y < SCREEN_HEIGHT - PLAYER_SIZE:
                player_y += PLAYER_SPEED

            # --- 计时器逻辑 ---
            current_ticks = pygame.time.get_ticks()
            elapsed_seconds = (current_ticks - start_ticks) / 1000
            
            # 检查胜利条件
            if elapsed_seconds >= WIN_TIME:
                state = "WIN"

            # --- 敌人生成 ---
            spawn_timer += 1
            if spawn_timer >= ENEMY_SPAWN_RATE:
                spawn_timer = 0
                enemy_x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
                enemy_y = -ENEMY_SIZE # 从屏幕上方外开始
                enemies.append([enemy_x, enemy_y])

            # --- 敌人移动与碰撞检测 ---
            for enemy in enemies[:]:
                enemy[1] += ENEMY_SPEED # 向下移动
                
                # 创建矩形对象用于碰撞检测
                player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
                enemy_rect = pygame.Rect(enemy[0], enemy[1], ENEMY_SIZE, ENEMY_SIZE)

                # 检查碰撞
                if player_rect.colliderect(enemy_rect):
                    state = "GAMEOVER"

                # 移除超出屏幕的敌人
                if enemy[1] > SCREEN_HEIGHT:
                    enemies.remove(enemy)

        # 4. 画面绘制
        screen.fill(BLACK) # 清屏

        if state == "PLAYING":
            # 画玩家
            pygame.draw.rect(screen, GREEN, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
            # 画敌人
            for enemy in enemies:
                pygame.draw.rect(screen, RED, (enemy[0], enemy[1], ENEMY_SIZE, ENEMY_SIZE))
            # 画计时器
            draw_text(f"Time: {elapsed_seconds:.1f}s / {WIN_TIME}s", font, WHITE, 10, 10)
            draw_text("Controls: W,A,S,D", font, (200, 200, 200), 10, SCREEN_HEIGHT - 40)

        elif state == "WIN":
            draw_text("CHALLENGE SUCCESS!", big_font, GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            draw_text("Press 'R' to Restart", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)
            draw_text(f"Final Time: {WIN_TIME}s", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, center=True)

        elif state == "GAMEOVER":
            draw_text("GAME OVER", big_font, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            draw_text("Press 'R' to Restart", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)
            draw_text(f"Survived: {elapsed_seconds:.1f}s", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, center=True)

        # 5. 更新显示
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()