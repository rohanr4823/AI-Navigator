import tkinter as tk
import random

GRID_SIZE = 10          
CELL_SIZE = 60          
TARGET_COUNT = 10       
OBSTACLE_COUNT = 5      

class AINavigatorApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=GRID_SIZE * CELL_SIZE, height=GRID_SIZE * CELL_SIZE)
        self.canvas.pack()
        self.targets = random.sample(
            [(row, col) for row in range(GRID_SIZE) for col in range(GRID_SIZE)],
            TARGET_COUNT
        )

        free_cells = [cell for cell in [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)] if cell not in self.targets]
        self.obstacles = random.sample(free_cells, OBSTACLE_COUNT)
        self.detected_targets = set()    
        self.ship_position = [0, 0]     
        self.draw_everything()
        self.root.after(300, self.move_ship_step_by_step)
        self.root.after(1000, self.move_obstacles_randomly)

    def draw_everything(self):
    
        self.canvas.delete("all")

        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

               
                if (row, col) in self.targets:
                    color = "red"
                elif (row, col) in self.obstacles:
                    color = "black"
                else:
                    color = "white"

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray", fill=color)

        ship_row, ship_col = self.ship_position
        self.draw_ship(ship_row, ship_col)

    def draw_ship(self, row, col):
        margin = 10
        x1 = col * CELL_SIZE + margin
        y1 = row * CELL_SIZE + margin
        x2 = x1 + CELL_SIZE - 2 * margin
        y2 = y1 + CELL_SIZE - 2 * margin
        self.canvas.create_oval(x1, y1, x2, y2, fill="blue")

    def move_ship_step_by_step(self):
        row, col = self.ship_position

        if (row, col) in self.targets and (row, col) not in self.detected_targets:
            print(f" Found a target at ({row}, {col})")
            self.detected_targets.add((row, col))
        if (row, col) == (GRID_SIZE - 1, GRID_SIZE - 1):
            print("\n Scan complete")
            print("Detected targets:", self.detected_targets)
            return
        if col < GRID_SIZE - 1:
            col += 1
        else:
            col = 0
            row += 1

        self.ship_position = [row, col]
        self.draw_everything()
        self.root.after(300, self.move_ship_step_by_step)

    def move_obstacles_randomly(self):
        new_positions = []
        for r, c in self.obstacles:
            directions = [(0,1),(0,-1),(1,0),(-1,0)]
            random.shuffle(directions)

            for dr, dc in directions:
                new_r = (r + dr) % GRID_SIZE
                new_c = (c + dc) % GRID_SIZE
                new_pos = (new_r, new_c)

                
                if new_pos not in self.targets and new_pos != tuple(self.ship_position):
                    new_positions.append(new_pos)
                    break
            else:
                new_positions.append((r, c))

        self.obstacles = new_positions
        self.draw_everything()
        self.root.after(1000, self.move_obstacles_randomly)

root = tk.Tk()
root.title("AI Navigator - 🚢")
app = AINavigatorApp(root)
root.mainloop()
