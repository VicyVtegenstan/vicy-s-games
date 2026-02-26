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
YELLOW = (255, 255, 0)# 子弹颜色

# 游戏设置
PLAYER_SIZE = 50
PLAYER_SPEED = 7
ENEMY_SIZE = 40
ENEMY_SPEED = 5
ENEMY_SPAWN_RATE = 30  # 敌人生成频率
WIN_TIME = 10         # 胜利所需时间 (秒)

# 子弹设置
BULLET_SIZE = 10
BULLET_SPEED = 10
SHOOT_COOLDOWN = 15    # 射击冷却帧数 (数值越大射得越慢)

# 设置屏幕
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("绿色方块射击生存战")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36)
big_font = pygame.font.SysFont("arial", 72)

# --- 函数定义 ---

def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)

def reset_game():
    player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
    player_y = SCREEN_HEIGHT - 100
    enemies = []
    bullets = []
    start_ticks = pygame.time.get_ticks()
    state = "PLAYING"
    score = 0
    cooldown = 0
    return player_x, player_y, enemies, bullets, start_ticks, state, score, cooldown

# --- 主程序 ---

def main():
    player_x, player_y, enemies, bullets, start_ticks, state, score, cooldown = reset_game()
    spawn_timer = 0
    running = True

    while running:
        clock.tick(FPS)
        
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # 按 ESC 退出
                    running = False
                if event.key == pygame.K_r and state != "PLAYING":
                    player_x, player_y, enemies, bullets, start_ticks, state, score, cooldown = reset_game()

        # 2. 游戏逻辑更新
        if state == "PLAYING":
            # --- 玩家移动 (WASD) ---
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player_x > 0:
                player_x -= PLAYER_SPEED
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player_x < SCREEN_WIDTH - PLAYER_SIZE:
                player_x += PLAYER_SPEED
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and player_y > 0:
                player_y -= PLAYER_SPEED
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player_y < SCREEN_HEIGHT - PLAYER_SIZE:
                player_y += PLAYER_SPEED

            # --- 射击逻辑 ---
            if cooldown > 0:
                cooldown -= 1
            if keys[pygame.K_SPACE] and cooldown == 0:
                # 发射子弹：从玩家中心顶部出发
                bullet_x = player_x + PLAYER_SIZE // 2 - BULLET_SIZE // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])
                cooldown = SHOOT_COOLDOWN

            # --- 计时器与胜利条件 ---
            current_ticks = pygame.time.get_ticks()
            elapsed_seconds = (current_ticks - start_ticks) / 1000
            if elapsed_seconds >= WIN_TIME:
                state = "WIN"

            # --- 敌人生成 ---
            spawn_timer += 1
            if spawn_timer >= ENEMY_SPAWN_RATE:
                spawn_timer = 0
                enemy_x = random.randint(0, SCREEN_WIDTH - ENEMY_SIZE)
                enemy_y = -ENEMY_SIZE
                enemies.append([enemy_x, enemy_y])

            # --- 子弹移动与碰撞检测 ---
            for bullet in bullets[:]:
                bullet[1] -= BULLET_SPEED # 子弹向上飞
                # 移除超出屏幕顶部的子弹
                if bullet[1] < -BULLET_SIZE:
                    bullets.remove(bullet)

            # --- 敌人移动与碰撞检测 ---
            for enemy in enemies[:]:
                enemy[1] += ENEMY_SPEED # 敌人向下落
                
                player_rect = pygame.Rect(player_x, player_y, PLAYER_SIZE, PLAYER_SIZE)
                enemy_rect = pygame.Rect(enemy[0], enemy[1], ENEMY_SIZE, ENEMY_SIZE)

                # 1. 玩家碰到敌人 -> 游戏结束
                if player_rect.colliderect(enemy_rect):
                    state = "GAMEOVER"

                # 2. 子弹碰到敌人 -> 敌人消失，加分
                for bullet in bullets[:]:
                    bullet_rect = pygame.Rect(bullet[0], bullet[1], BULLET_SIZE, BULLET_SIZE)
                    if bullet_rect.colliderect(enemy_rect):
                        if enemy in enemies: # 确保敌人还在列表里
                            enemies.remove(enemy)
                        if bullet in bullets: # 确保子弹还在列表里
                            bullets.remove(bullet)
                        score += 1
                        break # 子弹消失后跳出子弹循环

                # 移除超出屏幕底部的敌人
                if enemy in enemies and enemy[1] > SCREEN_HEIGHT:
                    enemies.remove(enemy)

        # 3. 画面绘制
        screen.fill(BLACK)

        if state == "PLAYING":
            # 画玩家
            pygame.draw.rect(screen, GREEN, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
            # 画敌人
            for enemy in enemies:
                pygame.draw.rect(screen, RED, (enemy[0], enemy[1], ENEMY_SIZE, ENEMY_SIZE))
            # 画子弹
            for bullet in bullets:
                pygame.draw.rect(screen, YELLOW, (bullet[0], bullet[1], BULLET_SIZE, BULLET_SIZE))
            
            # 画 UI
            draw_text(f"Time: {elapsed_seconds:.1f}s / {WIN_TIME}s", font, WHITE, 10, 10)
            draw_text(f"Score: {score}", font, WHITE, 10, 50)
            draw_text("Controls: WASD Move, SPACE Shoot, ESC Exit", font, (200, 200, 200), 10, SCREEN_HEIGHT - 40)

        elif state == "WIN":
            draw_text("CHALLENGE SUCCESS!", big_font, GREEN, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            draw_text(f"Final Score: {score}", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)
            draw_text("Press 'R' to Restart | ESC to Quit", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, center=True)

        elif state == "GAMEOVER":
            draw_text("GAME OVER", big_font, RED, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, center=True)
            draw_text(f"Final Score: {score}", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, center=True)
            draw_text("Press 'R' to Restart | ESC to Quit", font, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100, center=True)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()