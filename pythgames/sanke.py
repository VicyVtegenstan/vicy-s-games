import pygame
import random
import sys

# --- 配置常量 ---
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 10  # 控制游戏速度

# 颜色定义
COLOR_BG = (30, 30, 30)
COLOR_SNAKE = (100, 255, 100)
COLOR_SNAKE_HEAD = (50, 200, 50)
COLOR_FOOD = (255, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (255, 100, 100)

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        # 蛇身初始位置（从中间开始）
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), 
                     (start_x - 1, start_y), 
                     (start_x - 2, start_y)]
        self.direction = RIGHT
        self.grow = False  # 是否要生长
    
    def move(self):
        # 计算新头部位置
        head_x, head_y = self.body[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)
        
        # 插入新头部
        self.body.insert(0, new_head)
        
        # 如果不生长，移除尾部
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False  # 生长后重置标志
    
    def change_direction(self, new_direction):
        # 不能直接掉头（比如正在向右不能直接向左）
        opposite = (-self.direction[0], -self.direction[1])
        if new_direction != opposite:
            self.direction = new_direction
    
    def check_collision(self):
        head = self.body[0]
        
        # 撞墙检测
        if head[0] < 0 or head[0] >= GRID_WIDTH:
            return True
        if head[1] < 0 or head[1] >= GRID_HEIGHT:
            return True
        
        # 撞自己检测（从第二节开始检查）
        if head in self.body[1:]:
            return True
        
        return False
    
    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, 
                             CELL_SIZE - 1, CELL_SIZE - 1)
            # 头部颜色不同
            color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE
            pygame.draw.rect(surface, color, rect)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.spawn()
    
    def spawn(self, snake_body=None):
        # 随机生成食物，确保不在蛇身上
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if snake_body is None or (x, y) not in snake_body:
                self.position = (x, y)
                break
    
    def draw(self, surface):
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                         CELL_SIZE - 4, CELL_SIZE - 4)
        pygame.draw.rect(surface, COLOR_FOOD, rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("🐍 贪吃蛇 - Pygame 版")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24)
        self.big_font = pygame.font.SysFont("Arial", 48)
        
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.restart()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.change_direction(RIGHT)
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_ESCAPE:
                        return False
        
        return True
    
    def update(self):
        if self.game_over or self.paused:
            return
        
        # 移动蛇
        self.snake.move()
        
        # 检查碰撞
        if self.snake.check_collision():
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
            return
        
        # 检查是否吃到食物
        if self.snake.body[0] == self.food.position:
            self.snake.grow = True
            self.score += 10
            self.food.spawn(self.snake.body)
    
    def draw(self):
        self.screen.fill(COLOR_BG)
        
        # 绘制网格（可选，帮助视觉）
        for x in range(0, WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), 
                           (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), 
                           (0, y), (WIDTH, y))
        
        # 绘制游戏对象
        self.food.draw(self.screen)
        self.snake.draw(self.screen)
        
        # 绘制分数
        score_text = self.font.render(f"分数：{self.score}", True, COLOR_TEXT)
        high_score_text = self.font.render(f"最高分：{self.high_score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 40))
        
        # 游戏结束画面
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.big_font.render("游戏结束!", True, COLOR_GAME_OVER)
            restart_text = self.font.render("按 SPACE 重新开始", True, COLOR_TEXT)
            quit_text = self.font.render("按 ESC 退出", True, COLOR_TEXT)
            
            self.screen.blit(game_over_text, 
                           (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
            self.screen.blit(restart_text, 
                           (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2))
            self.screen.blit(quit_text, 
                           (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 40))
        
        # 暂停画面
        if self.paused and not self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.big_font.render("已暂停", True, COLOR_TEXT)
            self.screen.blit(pause_text, 
                           (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2))
        
        pygame.display.flip()
    
    def restart(self):
        self.snake.reset()
        self.food.spawn()
        self.score = 0
        self.game_over = False
        self.paused = False
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# --- 主程序入口 ---
if __name__ == "__main__":
    game = Game()
    game.run()