import tkinter as tk
from tkinter import simpledialog, filedialog, colorchooser, Toplevel
import math
import json
import random

class HexGroupDefiner:
    def __init__(self, root, hex_size):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.frame, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.hex_size = hex_size
        self.hexagons = []
        self.groups = {}
        self.group_colors = {}
        self.current_group = None
        self.color_index = 0
        self.colors = [
            "red", "green", "blue", "yellow", "orange", "purple", "cyan", "magenta",
            "lime", "pink", "teal", "lavender", "brown", "beige", "maroon", "mint",
            "olive", "coral", "navy", "grey", "white", "black", "violet", "indigo", "gold"
        ]

        # Load map image
        self.load_image()

        # Bind click events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag_left)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_drag_right)

        # Add buttons
        self.add_buttons()

    def add_buttons(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.new_group_button = tk.Button(self.button_frame, text="New Group", command=self.new_group)
        self.new_group_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.button_frame, text="Save Groups", command=self.save_groups)
        self.save_button.pack(side=tk.LEFT)

    def load_image(self):
        image_path = filedialog.askopenfilename()
        if image_path:
            self.image_path = image_path
            self.image = tk.PhotoImage(file=image_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
            self.canvas.image = self.image
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

            # Draw hexagonal grid after loading image to get correct dimensions
            self.draw_hex_grid()

    def new_group(self):
        group_name = simpledialog.askstring("Group Name", "Enter the name for the new group:")
        if group_name and group_name not in self.groups:
            self.group_creation_window(group_name)
        elif group_name in self.groups:
            print(f"Group {group_name} already exists. Please choose another name.")

    def group_creation_window(self, group_name):
        self.current_group_name = group_name
        self.color_window = Toplevel(self.root)
        self.color_window.title("Choose Group Color")

        choose_color_button = tk.Button(self.color_window, text="Choose Color", command=self.choose_color)
        choose_color_button.pack(pady=10)

        random_color_button = tk.Button(self.color_window, text="Random Color", command=self.choose_random_color)
        random_color_button.pack(pady=10)

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose color")
        if color[1]:
            self.finalize_group_creation(color[1])

    def choose_random_color(self):
        color = random.choice(self.colors)
        self.finalize_group_creation(color)

    def finalize_group_creation(self, color):
        group_name = self.current_group_name
        self.groups[group_name] = []
        self.group_colors[group_name] = color
        self.current_group = group_name
        self.color_window.destroy()
        print(f"Created new group: {group_name} with color {color}")

    def save_groups(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump({"image_path": self.image_path, "groups": self.groups, "group_colors": self.group_colors}, f)
            print(f"Groups saved to {file_path}")

    def draw_hex(self, x_center, y_center, col, row):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = x_center + self.hex_size * math.cos(angle_rad)
            y = y_center + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        hexagon = self.canvas.create_polygon(points, outline='', fill='', tags=("hexagon", f"hex_{col}_{row}"))
        self.hexagons.append((hexagon, col, row))

    def draw_hex_grid(self):
        width = self.image.width()  # Use image dimensions instead of canvas dimensions
        height = self.image.height()
        hex_height = self.hex_size * 2
        hex_width = math.sqrt(3) * self.hex_size
        vert_spacing = hex_height * 3/4

        for row in range(int(height // vert_spacing) + 1):
            for col in range(int(width // hex_width) + 1):
                x_offset = col * hex_width
                y_offset = row * vert_spacing
                if row % 2 == 1:
                    x_offset += hex_width / 2
                self.draw_hex(x_offset, y_offset, col, row)

    def on_click(self, event):
        if self.current_group is None:
            print("No group selected. Please create a new group first.")
            return

        self.handle_click(event.x, event.y)

    def on_drag_left(self, event):
        if self.current_group is None:
            print("No group selected. Please create a new group first.")
            return

        self.handle_click(event.x, event.y)

    def on_right_click(self, event):
        self.handle_right_click(event.x, event.y)

    def on_drag_right(self, event):
        self.handle_right_click(event.x, event.y)

    def handle_click(self, x, y):
        clicked_item = self.canvas.find_closest(self.canvas.canvasx(x), self.canvas.canvasy(y))[0]
        tags = self.canvas.gettags(clicked_item)
        for tag in tags:
            if tag.startswith("hex_"):
                _, col, row = tag.split("_")
                col, row = int(col), int(row)
                self.add_to_group(col, row)
                self.canvas.itemconfig(clicked_item, fill=self.group_colors[self.current_group])
                print(f"Added hexagon ({col}, {row}) to {self.current_group}")
                return

    def handle_right_click(self, x, y):
        clicked_item = self.canvas.find_closest(self.canvas.canvasx(x), self.canvas.canvasy(y))[0]
        tags = self.canvas.gettags(clicked_item)
        for tag in tags:
            if tag.startswith("hex_"):
                _, col, row = tag.split("_")
                col, row = int(col), int(row)
                self.remove_from_group(col, row)
                self.canvas.itemconfig(clicked_item, fill='')
                print(f"Removed hexagon ({col}, {row}) from its group")
                return

    def add_to_group(self, col, row):
        if self.current_group not in self.groups:
            self.groups[self.current_group] = []
        if (col, row) not in self.groups[self.current_group]:
            self.groups[self.current_group].append((col, row))

    def remove_from_group(self, col, row):
        for group, hexes in self.groups.items():
            if (col, row) in hexes:
                hexes.remove((col, row))
                break

if __name__ == "__main__":
    root = tk.Tk()
    hex_size = 20  # Size of each hexagon
    app = HexGroupDefiner(root, hex_size)
    root.mainloop()
