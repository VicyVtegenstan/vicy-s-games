import pygame
import random
from collections import deque

# --- 配置常量 ---
WIDTH, HEIGHT = 800, 600
CELL_SIZE = 40
COLS = WIDTH // CELL_SIZE
ROWS = HEIGHT // CELL_SIZE
FPS = 60

# 颜色定义
COLOR_BG = (30, 30, 30)
COLOR_WALL = (200, 200, 200)
COLOR_PATH = (100, 255, 100)      # 最终路径颜色
COLOR_VISITED = (50, 100, 200)    # 搜索过程中的访问颜色
COLOR_START = (255, 50, 50)
COLOR_END = (50, 50, 255)
COLOR_TEXT = (255, 255, 255)

# 墙壁方向索引：0:上，1:右，2:下，3:左
WALL_TOP, WALL_RIGHT, WALL_BOTTOM, WALL_LEFT = 0, 1, 2, 3

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 默认四面都有墙
        self.walls = [True, True, True, True] 
        self.visited = False  # 用于生成算法
        
    def draw(self, surface):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE
        
        # 绘制墙壁
        if self.walls[WALL_TOP]:
            pygame.draw.line(surface, COLOR_WALL, (x, y), (x + CELL_SIZE, y), 2)
        if self.walls[WALL_RIGHT]:
            pygame.draw.line(surface, COLOR_WALL, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[WALL_BOTTOM]:
            pygame.draw.line(surface, COLOR_WALL, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 2)
        if self.walls[WALL_LEFT]:
            pygame.draw.line(surface, COLOR_WALL, (x, y), (x, y + CELL_SIZE), 2)

        # 绘制起点和终点背景
        if (self.x, self.y) == (0, 0):
            pygame.draw.rect(surface, COLOR_START, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10))
        if (self.x, self.y) == (COLS - 1, ROWS - 1):
            pygame.draw.rect(surface, COLOR_END, (x + 5, y + 5, CELL_SIZE - 10, CELL_SIZE - 10))

    def check_neighbors(self, grid):
        neighbors = []
        # 上、右、下、左
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < COLS and 0 <= ny < ROWS:
                if not grid[ny][nx].visited:
                    neighbors.append((nx, ny))
        
        if neighbors:
            return random.choice(neighbors)
        return None

class Maze:
    def __init__(self):
        self.grid = [[Cell(x, y) for x in range(COLS)] for y in range(ROWS)]
        self.generate()
        self.solution_path = []
        self.searched_cells = [] # 用于动画展示搜索过程
        
    def generate(self):
        """使用 DFS + 回溯算法生成迷宫"""
        stack = []
        start_cell = self.grid[0][0]
        start_cell.visited = True
        stack.append(start_cell)
        
        while stack:
            current = stack[-1]
            neighbor_pos = current.check_neighbors(self.grid)
            
            if neighbor_pos:
                nx, ny = neighbor_pos
                next_cell = self.grid[ny][nx]
                
                # 移除墙壁
                # 判断方向
                if nx > current.x: # 右边
                    current.walls[WALL_RIGHT] = False
                    next_cell.walls[WALL_LEFT] = False
                elif nx < current.x: # 左边
                    current.walls[WALL_LEFT] = False
                    next_cell.walls[WALL_RIGHT] = False
                elif ny > current.y: # 下边
                    current.walls[WALL_BOTTOM] = False
                    next_cell.walls[WALL_TOP] = False
                elif ny < current.y: # 上边
                    current.walls[WALL_TOP] = False
                    next_cell.walls[WALL_BOTTOM] = False
                
                next_cell.visited = True
                stack.append(next_cell)
            else:
                stack.pop()
                
        # 重置 visited 标记，以便后续使用（虽然求解算法不需要这个标记，但为了整洁）
        for row in self.grid:
            for cell in row:
                cell.visited = False

    def solve_bfs(self):
        """使用 BFS 寻找最短路径"""
        start = (0, 0)
        end = (COLS - 1, ROWS - 1)
        
        queue = deque([start])
        visited = {start}
        parent = {start: None}
        self.searched_cells = []
        
        found = False
        
        while queue:
            current = queue.popleft()
            self.searched_cells.append(current)
            
            if current == end:
                found = True
                break
            
            x, y = current
            current_cell = self.grid[y][x]
            
            # 检查四个方向，注意要检查墙壁
            # 0:上，1:右，2:下，3:左
            moves = [
                ((0, -1), WALL_TOP),
                ((1, 0), WALL_RIGHT),
                ((0, 1), WALL_BOTTOM),
                ((-1, 0), WALL_LEFT)
            ]
            
            for (dx, dy), wall_idx in moves:
                if not current_cell.walls[wall_idx]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        parent[(nx, ny)] = current
                        queue.append((nx, ny))
        
        # 回溯路径
        if found:
            path = []
            curr = end
            while curr is not None:
                path.append(curr)
                curr = parent[curr]
            self.solution_path = path[::-1] # 反转路径
        else:
            self.solution_path = []

    def draw(self, surface, solve_step=-1):
        for row in self.grid:
            for cell in row:
                cell.draw(surface)
        
        # 绘制搜索过程 (动画)
        if 0 <= solve_step < len(self.searched_cells):
            for i in range(solve_step + 1):
                x, y = self.searched_cells[i]
                rect = pygame.Rect(x * CELL_SIZE + 5, y * CELL_SIZE + 5, CELL_SIZE - 10, CELL_SIZE - 10)
                pygame.draw.rect(surface, COLOR_VISITED, rect)

        # 绘制最终路径
        if self.solution_path:
            for x, y in self.solution_path:
                rect = pygame.Rect(x * CELL_SIZE + 10, y * CELL_SIZE + 10, CELL_SIZE - 20, CELL_SIZE - 20)
                pygame.draw.rect(surface, COLOR_PATH, rect)

# --- 主程序 ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pygame 迷宫生成与求解演示")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    maze = Maze()
    
    solving = False
    solve_animation_index = 0
    animation_timer = 0
    animation_delay = 50 # 毫秒，控制求解动画速度

    running = True
    while running:
        clock.tick(FPS)
        dt = clock.get_time()
        
        # 1. 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g: # 生成新迷宫
                    maze = Maze()
                    solving = False
                    solve_animation_index = 0
                if event.key == pygame.K_s: # 开始求解
                    if not maze.solution_path:
                        maze.solve_bfs()
                    solving = True
                    solve_animation_index = -1
                if event.key == pygame.K_r: # 重置路径
                    solving = False
                    solve_animation_index = 0
                    maze.solution_path = []
                    maze.searched_cells = []
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 2. 逻辑更新 (求解动画)
        if solving and maze.searched_cells:
            animation_timer += dt
            if animation_timer > animation_delay:
                animation_timer = 0
                solve_animation_index += 1
                if solve_animation_index >= len(maze.searched_cells):
                    solving = False # 动画结束

        # 3. 绘制
        screen.fill(COLOR_BG)
        maze.draw(screen, solve_animation_index if solving else -1)
        
        # UI 提示
        info_text = [
            "按 [G] 生成新迷宫",
            "按 [S] 自动求解 (BFS)",
            "按 [R] 重置路径",
            f"状态：{'求解中...' if solving else '就绪'}"
        ]
        
        for i, text in enumerate(info_text):
            surf = font.render(text, True, COLOR_TEXT)
            screen.blit(surf, (10, 10 + i * 25))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()