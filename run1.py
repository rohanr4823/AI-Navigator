import tkinter as tk
import heapq
import random

GRID_SIZE = 10
CELL_SIZE = 60
TARGET_COUNT = 7
OBSTACLE_COUNT = 5

class AStarNavigator:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()

        self.start = (0, 0)
        self.goal = (GRID_SIZE - 1, GRID_SIZE - 1)

        all_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)]
        safe_cells = [cell for cell in all_cells if cell not in [self.start, self.goal]]
        self.targets = random.sample(safe_cells, TARGET_COUNT)
        remaining = [c for c in safe_cells if c not in self.targets]
        self.obstacles = random.sample(remaining, OBSTACLE_COUNT)

        self.current_pos = self.start
        self.path = self.find_path(self.current_pos)
        self.index = 0

        self.root.after(500, self.step)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(self, node):
        r, c = node
        neighbors = []
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            if (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and
                (nr, nc) not in self.obstacles and
                (nr, nc) not in self.targets):
                neighbors.append((nr, nc))
        return neighbors

    def find_path(self, start):
        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == self.goal:
                break
            for neighbor in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.heuristic(neighbor, self.goal)
                    heapq.heappush(frontier, (priority, neighbor))
                    came_from[neighbor] = current

        if self.goal not in came_from:
            return None

        path = []
        current = self.goal
        while current:
            path.append(current)
            current = came_from[current]
        return list(reversed(path))

    def move_obstacles(self):
        new_obstacles = []
        for obs in self.obstacles:
            neighbors = self.get_neighbors(obs)
            new_obstacles.append(random.choice(neighbors) if neighbors else obs)
        self.obstacles = new_obstacles

    def draw_everything(self):
        self.canvas.delete("all")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                cell = (r, c)
                if cell == self.start:
                    fill = "white"
                elif cell == self.goal:
                    fill = "green"
                elif cell in self.targets:
                    fill = "red"
                elif cell in self.obstacles:
                    fill = "black"
                elif self.path and cell in self.path:
                    fill = "lightblue"
                else:
                    fill = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="gray")

        if self.path and self.index < len(self.path) - 1:
            curr = self.path[self.index]
            nxt = self.path[self.index + 1]
            self.draw_ship(curr, nxt)

    def draw_ship(self, curr, nxt):
        r, c = curr
        nr, nc = nxt
        cx = c * CELL_SIZE + CELL_SIZE // 2
        cy = r * CELL_SIZE + CELL_SIZE // 2
        size = CELL_SIZE // 3

        if nr < r:
            points = [cx, cy - size, cx - size, cy + size, cx + size, cy + size]
        elif nr > r:
            points = [cx, cy + size, cx - size, cy - size, cx + size, cy - size]
        elif nc < c:
            points = [cx - size, cy, cx + size, cy - size, cx + size, cy + size]
        elif nc > c:
            points = [cx + size, cy, cx - size, cy - size, cx - size, cy + size]
        else:
            points = [cx - size, cy - size, cx + size, cy - size, cx, cy + size]

        self.canvas.create_polygon(points, fill="blue")

    def step(self):
        if not self.path or self.index >= len(self.path) - 1:
            print("✅ Reached goal or no path.")
            self.draw_everything()
            return

        self.current_pos = self.path[self.index + 1]
        self.index += 1

        self.move_obstacles()

        new_path = self.find_path(self.current_pos)
        if new_path:
            self.path = new_path
            self.index = 0
        else:
            print("⚠️ No path found. Waiting at current position.")

        self.draw_everything()
        self.root.after(300, self.step)

root = tk.Tk()
root.title("A* Ship Navigation with Moving Obstacles")
app = AStarNavigator(root)
root.mainloop()
