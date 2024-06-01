import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, colorchooser
import json
import math

class HexGroupViewer:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_frame = tk.Frame(self.frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.focus_set()  # Ensure canvas has focus

        self.v_scrollbar = tk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scrollbar = tk.Scrollbar(self.root, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        self.groups = {}
        self.group_colors = {}
        self.image_path = None
        self.hex_size = None
        self.hexagons = []

        self.load_json()

        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.root.bind("<Left>", self.scroll_left)
        self.root.bind("<Right>", self.scroll_right)
        self.root.bind("<Up>", self.scroll_up)
        self.root.bind("<Down>", self.scroll_down)
        
        self.root.bind("<a>", self.scroll_left)
        self.root.bind("<d>", self.scroll_right)
        self.root.bind("<w>", self.scroll_up)
        self.root.bind("<s>", self.scroll_down)

        self.add_group_listbox()

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not file_path:
            messagebox.showerror("Error", "No JSON file selected.")
            self.root.destroy()
            return

        with open(file_path, 'r') as file:
            data = json.load(file)
            self.image_path = data.get("image_path")
            self.hex_size = data.get("hex_size")
            groups_data = data.get("groups", {})
            for group_name, hexagons in groups_data.items():
                self.groups[group_name] = set(tuple(hexagon) for hexagon in hexagons)
            self.group_colors = data.get("group_colors", {})
        
        self.load_image()
        
    def load_image(self):
        """Load an image and display it on the canvas."""
        
        try:
            self.image = tk.PhotoImage(file=self.image_path)
        except tk.TclError:
            print("Failed to load the image. Please select a valid image file.")
            return
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.image = self.image
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        self.draw_hex_grid()


    def draw_hex(self, x_center, y_center, col, row):
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = x_center + self.hex_size * math.cos(angle_rad)
            y = y_center + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        hexagon = self.canvas.create_polygon(points, outline='', fill='', tags=(f"hex_{col}_{row}",))
        self.hexagons.append((hexagon, col, row))

    def draw_hex_grid(self):

        width = self.image.width()
        height = self.image.height()
        hex_height = self.hex_size * 2
        hex_width = math.sqrt(3) * self.hex_size
        vert_spacing = hex_height * 3 / 4

        for row in range(int(height // vert_spacing) + 1):
            for col in range(int(width // hex_width) + 1):
                x_offset = col * hex_width
                y_offset = row * vert_spacing
                if row % 2 == 1:
                    x_offset += hex_width / 2
                self.draw_hex(x_offset, y_offset, col, row)

        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_canvas_click(self, event):
        
        clicked_item = self.canvas.find_closest(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))[0]
        tags = self.canvas.gettags(clicked_item)
        for tag in tags:
            if tag.startswith("hex_"):
                _, col, row = tag.split("_")
                col, row = int(col), int(row)
                self.highlight_group(col, row)
                return

    def highlight_group(self, col, row):
        for group, hexes in self.groups.items():
            if (col, row) in hexes:
                color = self.group_colors.get(group, "lightblue")
                for hexagon, c, r in self.hexagons:
                    if (c, r) in hexes:
                        self.canvas.itemconfig(hexagon, fill=color)
            else:
                for hexagon, c, r in self.hexagons:
                    if (c, r) in hexes:
                        self.canvas.itemconfig(hexagon, fill="")


    def add_group_listbox(self):
        """Add a listbox to display the names of the created groups."""
        self.group_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.group_listbox.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_listbox.bind("<<ListboxSelect>>", self.on_group_select)
        for group in self.groups.keys():
            self.group_listbox.insert(tk.END, group)


    def on_group_select(self, event):
        selection = self.group_listbox.curselection()
        if selection:
            group_name = self.group_listbox.get(selection[0])
            if group_name in self.groups:
                self.highlight_group_by_name(group_name)




    def highlight_group_by_name(self, group_name):
        for hexagon, col, row in self.hexagons:
            if (col, row) in self.groups[group_name]:
                color = self.group_colors.get(group_name, "lightblue")
                self.canvas.itemconfig(hexagon, fill=color)
            else:
                self.canvas.itemconfig(hexagon, fill="")


    def scroll_left(self, event):
        print('Left')
        self.canvas.xview_scroll(-1, "units")

    def scroll_right(self, event):
        print('Right')
        self.canvas.xview_scroll(1, "units")

    def scroll_up(self, event):
        print('Up')
        self.canvas.yview_scroll(-1, "units")

    def scroll_down(self, event):
        print('Down')
        self.canvas.yview_scroll(1, "units")


if __name__ == "__main__":
    root = tk.Tk()
    app = HexGroupViewer(root)
    root.mainloop()
