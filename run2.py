import tkinter as tk
import heapq
import random

GRID_SIZE = 10
CELL_SIZE = 60
OBSTACLE_COUNT = 10
TARGET_COUNT = 5

class AStarNavigator:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()

        self.start = (0, 0)
        self.goal = (GRID_SIZE - 1, GRID_SIZE - 1)

        all_cells = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if (r, c) not in [self.start, self.goal]]
        self.targets = random.sample(all_cells, TARGET_COUNT)
        remaining_cells = [c for c in all_cells if c not in self.targets]
        self.obstacles = random.sample(remaining_cells, OBSTACLE_COUNT)

        self.current_pos = self.start
        self.path = self.find_path(self.start)
        self.index = 0

        self.draw_everything()
        self.root.after(500, self.step)

    def draw_everything(self):
        self.canvas.delete("all")
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                cell = (r, c)
                if cell == self.goal:
                    color = "green"
                elif cell in self.targets:
                    color = "red"
                elif cell in self.obstacles:
                    color = "black"
                else:
                    color = "white"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

        self.draw_ship(*self.current_pos)

    def draw_ship(self, row, col):
        margin = 10
        x1 = col * CELL_SIZE + margin
        y1 = row * CELL_SIZE + margin
        x2 = x1 + CELL_SIZE - 2 * margin
        y2 = y1 + CELL_SIZE - 2 * margin
        self.canvas.create_oval(x1, y1, x2, y2, fill="blue")

    def step(self):
        if self.current_pos == self.goal:
            print("✅ Goal reached!")
            return

        self.move_obstacles()

        # Replan path after obstacles move
        new_path = self.find_path(self.current_pos)
        if new_path:
            self.path = new_path
            self.index = 0
        else:
            print("⚠️ No path found. Waiting...")
            self.draw_everything()
            self.root.after(300, self.step)
            return

        # Move along path
        if self.index < len(self.path) - 1:
            self.index += 1
            self.current_pos = self.path[self.index]

        self.draw_everything()
        self.root.after(300, self.step)

    def heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def find_path(self, start):
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, self.goal)}
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == self.goal:
                return self.reconstruct_path(came_from, current)

            visited.add(current)
            for neighbor in self.get_neighbors(current):
                if neighbor in visited:
                    continue
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, self.goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return list(reversed(path))

    def get_neighbors(self, cell):
        r, c = cell
        neighbors = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = r + dr, c + dc
            new_pos = (nr, nc)
            if (0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and
                new_pos not in self.obstacles and
                new_pos not in self.targets):
                neighbors.append(new_pos)
        return neighbors

    def move_obstacles(self):
        new_obstacles = []
        for obs in self.obstacles:
            moves = self.get_neighbors(obs)
            valid = [m for m in moves if m != self.current_pos and m != self.goal and m not in self.obstacles]
            new_obstacles.append(random.choice(valid) if valid else obs)
        self.obstacles = new_obstacles

# Launch the GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("🚀 A* Navigator with Moving Obstacles")
    app = AStarNavigator(root)
    root.mainloop()
