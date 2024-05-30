import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import math
import json

class HexTileApp:
    def __init__(self, root, hex_size):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
        self.hex_size = hex_size
        self.image = None
        self.hexagons = []
        self.groups = {}

        # Load groups from file
        self.load_groups()

        # Bind click event
        self.canvas.bind("<Button-1>", self.on_click)

    def load_groups(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
                self.image_path = data["image_path"]
                self.groups = data["groups"]
            print(f"Groups loaded from {file_path}")
            self.load_image()

    def load_image(self):
        if self.image_path:
            image = Image.open(self.image_path)
            self.image = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
            self.draw_hex_grid()

    def draw_hex(self, x_center, y_center, tag):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = x_center + self.hex_size * math.cos(angle_rad)
            y = y_center + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        hexagon = self.canvas.create_polygon(points, outline='black', fill='', tags=("hexagon", tag))
        self.hexagons.append((hexagon, x_center, y_center, tag))

    def draw_hex_grid(self):
        width = self.canvas.winfo_reqwidth()
        height = self.canvas.winfo_reqheight()
        hex_height = self.hex_size * 2
        hex_width = math.sqrt(3) * self.hex_size
        vert_spacing = hex_height * 3/4

        for row in range(int(height // vert_spacing) + 1):
            for col in range(int(width // hex_width) + 1):
                x_offset = col * hex_width
                y_offset = row * vert_spacing
                if row % 2 == 1:
                    x_offset += hex_width / 2

                tag = self.get_hex_tag(col, row)
                if tag:
                    self.draw_hex(x_offset, y_offset, tag)

    def get_hex_tag(self, col, row):
        for tag, hexes in self.groups.items():
            for hex_coords in hexes:
                if (col, row) == tuple(hex_coords):
                    return tag
        return None


    # def on_click(self, event):
    #     x, y = event.x, event.y
    #     clicked_item = self.canvas.find_closest(x, y)[0]
    #     tags = self.canvas.gettags(clicked_item)
    #     print("Clicked Item Tags:", tags)


    def on_click(self, event):
        x, y = event.x, event.y
        clicked_item = self.canvas.find_closest(x, y)[0]
        tags = self.canvas.gettags(clicked_item)
        if len(tags) > 1:
            group_tag = tags[1]
            for item in self.canvas.find_withtag("hexagon"):
                item_tags = self.canvas.gettags(item)
                if group_tag in item_tags:
                    self.canvas.itemconfig(item, fill="lightblue")
        else:
            print("No group tag found for the clicked item.")



if __name__ == "__main__":
    root = tk.Tk()
    hex_size = 20  # Size of each hexagon
    app = HexTileApp(root, hex_size)
    root.mainloop()
