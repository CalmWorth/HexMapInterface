import tkinter as tk
from tkinter import simpledialog, filedialog
import math
import json

class HexGroupDefiner:
    def __init__(self, root, hex_size):
        self.root = root
        self.canvas = tk.Canvas(root, width=800, height=600, bg='white')
        self.canvas.pack()
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

        # Draw hexagonal grid
        self.draw_hex_grid()

        # Bind click events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)

        # Add buttons
        self.add_buttons()

    def add_buttons(self):
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()

        self.new_group_button = tk.Button(self.button_frame, text="New Group", command=self.new_group)
        self.new_group_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.button_frame, text="Save Groups", command=self.save_groups)
        self.save_button.pack(side=tk.LEFT)

    def load_image(self):
        image_path = filedialog.askopenfilename()
        if image_path:
            self.image_path = image_path
            image = tk.PhotoImage(file=image_path)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image)
            self.canvas.image = image

    def new_group(self):
        group_name = simpledialog.askstring("Group Name", "Enter the name for the new group:")
        if group_name and group_name not in self.groups:
            self.groups[group_name] = []
            self.group_colors[group_name] = self.colors[self.color_index % len(self.colors)]
            self.color_index += 1
            self.current_group = group_name
            print(f"Created new group: {group_name} with color {self.group_colors[group_name]}")
        elif group_name in self.groups:
            print(f"Group {group_name} already exists. Please choose another name.")

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
        hexagon = self.canvas.create_polygon(points, outline='black', fill='', tags=("hexagon", f"hex_{col}_{row}"))
        self.hexagons.append((hexagon, col, row))

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
                self.draw_hex(x_offset, y_offset, col, row)

    def on_click(self, event):
        if self.current_group is None:
            print("No group selected. Please create a new group first.")
            return

        x, y = event.x, event.y
        clicked_item = self.canvas.find_closest(x, y)[0]
        tags = self.canvas.gettags(clicked_item)
        for tag in tags:
            if tag.startswith("hex_"):
                _, col, row = tag.split("_")
                col, row = int(col), int(row)
                self.add_to_group(col, row)
                self.canvas.itemconfig(clicked_item, fill=self.group_colors[self.current_group])
                print(f"Added hexagon ({col}, {row}) to {self.current_group}")
                return

    def on_right_click(self, event):
        print('Right Clicked')
        x, y = event.x, event.y
        clicked_item = self.canvas.find_closest(x, y)[0]
        tags = self.canvas.gettags(clicked_item)
        print("Tags:", tags)

        if len(tags) > 1:
            hex_tag = tags[1]
            group_tag = None

            # Find which group this hex belongs to
            for group, hexes in self.groups.items():
                if any(hex_tag == f"hex_{col}_{row}" for col, row in hexes):
                    group_tag = group
                    break

            if group_tag:
                col, row = map(int, hex_tag.split("_")[1:])
                print(f"Right-clicked Hexagon: ({col}, {row}) in {group_tag}")

                if (col, row) in self.groups[group_tag]:
                    self.groups[group_tag].remove((col, row))
                    print(f"Hexagon ({col}, {row}) deselected from {group_tag}")
                    self.canvas.itemconfig(clicked_item, fill='')  # Reset fill color
                else:
                    print(f"Hexagon ({col}, {row}) not found in {group_tag}")
            else:
                print("No group tag found for the clicked item.")
        else:
            print("No tags found for the clicked item.")

    def add_to_group(self, col, row):
        if self.current_group not in self.groups:
            self.groups[self.current_group] = []
        if (col, row) not in self.groups[self.current_group]:
            self.groups[self.current_group].append((col, row))

if __name__ == "__main__":
    root = tk.Tk()
    hex_size = 20  # Size of each hexagon
    app = HexGroupDefiner(root, hex_size)
    root.mainloop()
