import tkinter as tk

GRID_SIZE = 5
CELL_SIZE = 60

class GridApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE)
        self.canvas.pack()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.on_click)

    def draw_grid(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x1 = j * CELL_SIZE
                y1 = i * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        print(f"Clicked at cell ({row}, {col})")
        self.mark_cell(row, col)

    def mark_cell(self, row, col):
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue")  # Mark point

root = tk.Tk()
root.title("AI Navigator - Grid Click Detector")
app = GridApp(root)
root.mainloop()
