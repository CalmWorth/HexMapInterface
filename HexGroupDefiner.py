import tkinter as tk
from tkinter import simpledialog, filedialog, colorchooser, messagebox, Toplevel
import math
import json
import random

class HexGroupDefiner:
    COLORS = [
        "red", "green", "blue", "yellow", "orange", "purple", "cyan", "magenta",
        "lime", "pink", "teal", "lavender", "brown", "beige", "maroon", "mint",
        "olive", "coral", "navy", "grey", "white", "black", "violet", "indigo", "gold"
    ]

    def __init__(self, root):
        """Initialize the hex group definer with a given root Tkinter window."""
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

        self.hex_size = None
        self.hexagons = []
        self.groups = {}
        self.group_colors = {}
        self.current_group = None
        self.color_index = 0
        self.colors = self.COLORS

        # Load map image
        self.load_image()

        # Bind click events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag_left)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_drag_right)

        # Bind arrow key events
        self.root.bind("<Left>", self.scroll_left)
        self.root.bind("<Right>", self.scroll_right)
        self.root.bind("<Up>", self.scroll_up)
        self.root.bind("<Down>", self.scroll_down)
        
        self.root.bind("<a>", self.scroll_left)
        self.root.bind("<d>", self.scroll_right)
        self.root.bind("<w>", self.scroll_up)
        self.root.bind("<s>", self.scroll_down)

        # Add buttons
        self.add_buttons()

        # Add group listbox
        self.add_group_listbox()

    def add_buttons(self):
        """Add control buttons for creating new groups and saving them."""
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.new_group_button = tk.Button(self.button_frame, text="New Group", command=self.new_group)
        self.new_group_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(self.button_frame, text="Save Groups", command=self.save_groups)
        self.save_button.pack(side=tk.LEFT)

    def add_group_listbox(self):
        """Add a listbox to display the names of the created groups."""
        self.group_listbox = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.group_listbox.pack(side=tk.RIGHT, fill=tk.Y)
        self.group_listbox.bind("<<ListboxSelect>>", self.on_group_select)

    def load_image(self):
        """Load an image and display it on the canvas."""
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        if not image_path:
            return  # User cancelled the file dialog
        self.image_path = image_path
        try:
            self.image = tk.PhotoImage(file=image_path)
        except tk.TclError:
            print("Failed to load the image. Please select a valid image file.")
            return
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image)
        self.canvas.image = self.image
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        self.prompt_hex_size()

    def prompt_hex_size(self):
        """Prompt the user to input the hex size."""
        self.hex_size = simpledialog.askinteger("Hex Size", "Enter the size of the hexagons:")
        if self.hex_size:
            self.draw_hex_grid()
        else:
            print("Hex size input cancelled. Please restart the application and input a valid hex size.")
            self.root.destroy()

    def new_group(self):
        """Create a new group with a unique name."""
        while True:
            group_name = simpledialog.askstring("Group Name", "Enter the name for the new group:")
            if not group_name:
                return  # User cancelled the input
            if group_name in self.groups:
                messagebox.showerror("Error", "Group name already exists. Please choose another name.")
            else:
                self.group_creation_window(group_name)
                break

    def group_creation_window(self, group_name):
        """Open a window to choose a color for the new group."""
        self.current_group_name = group_name
        self.color_window = Toplevel(self.root)
        self.color_window.title("Choose Group Color")

        choose_color_button = tk.Button(self.color_window, text="Choose Color", command=self.choose_color)
        choose_color_button.pack(pady=10)

        random_color_button = tk.Button(self.color_window, text="Random Color", command=self.choose_random_color)
        random_color_button.pack(pady=10)

    def choose_color(self):
        """Open a color chooser dialog and finalize group creation with the chosen color."""
        color = colorchooser.askcolor(title="Choose color")
        if color[1]:
            self.finalize_group_creation(color[1])

    def choose_random_color(self):
        """Finalize group creation with a randomly chosen color."""
        color = random.choice(self.colors)
        self.finalize_group_creation(color)

    def finalize_group_creation(self, color):
        """Finalize the creation of a new group with a specified color."""
        group_name = self.current_group_name
        self.groups[group_name] = set()
        self.group_colors[group_name] = color
        self.current_group = group_name
        self.color_window.destroy()
        print(f"Created new group: {group_name} with color {color}")
        self.update_group_listbox()

    def update_group_listbox(self):
        """Update the group listbox with the names of the created groups."""
        self.group_listbox.delete(0, tk.END)
        for group_name in self.groups.keys():
            self.group_listbox.insert(tk.END, group_name)

    def on_group_select(self, event):
        """Handle the selection of a group from the group listbox."""
        selection = self.group_listbox.curselection()
        if selection:
            group_name = self.group_listbox.get(selection[0])
            if group_name in self.groups:
                self.current_group = group_name
                print(f"Selected group: {group_name}")

    def save_groups(self):
        """Save the groups and their colors to a JSON file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, 'w') as f:
                json.dump({"image_path": self.image_path, "hex_size": self.hex_size, "groups": {k: list(v) for k, v in self.groups.items()}, "group_colors": self.group_colors}, f)
            print(f"Groups saved to {file_path}")

    def draw_hex(self, x_center, y_center, col, row):
        """Draw a single hexagon at the specified coordinates."""
        points = []
        for i in range(6):
            angle_deg = 60 * i - 30
            angle_rad = math.radians(angle_deg)
            x = x_center + self.hex_size * math.cos(angle_rad)
            y = y_center + self.hex_size * math.sin(angle_rad)
            points.append((x, y))
        hexagon = self.canvas.create_polygon(points, outline='grey', fill='', tags=("hexagon", f"hex_{col}_{row}"))
        self.hexagons.append((hexagon, col, row))

    def draw_hex_grid(self):
        """Draw a grid of hexagons covering the image."""
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

    def on_click(self, event):
        """Handle left mouse button click events."""
        if self.current_group is None:
            print("No group selected. Please create a new group first.")
            return

        self.handle_click(event.x, event.y)

    def on_drag_left(self, event):
        """Handle left mouse button drag events."""
        if self.current_group is None:
            print("No group selected. Please create a new group first.")
            return

        self.handle_click(event.x, event.y)

    def on_right_click(self, event):
        """Handle right mouse button click events."""
        self.handle_right_click(event.x, event.y)

    def on_drag_right(self, event):
        """Handle right mouse button drag events."""
        self.handle_right_click(event.x, event.y)

    def handle_click(self, x, y):
        """Add the clicked hexagon to the current group."""
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
        """Remove the clicked hexagon from its group."""
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
        """Add a hexagon to the current group."""
        if self.current_group not in self.groups:
            self.groups[self.current_group] = set()
        if (col, row) not in self.groups[self.current_group]:
            self.groups[self.current_group].add((col, row))

    def remove_from_group(self, col, row):
        """Remove a hexagon from its group."""
        for group, hexes in self.groups.items():
            if (col, row) in hexes:
                hexes.remove((col, row))
                break

    def scroll_left(self, event):
        # print('Left')
        self.canvas.xview_scroll(-1, "units")

    def scroll_right(self, event):
        # print('Right')
        self.canvas.xview_scroll(1, "units")

    def scroll_up(self, event):
        # print('Up')
        self.canvas.yview_scroll(-1, "units")

    def scroll_down(self, event):
        # print('Down')
        self.canvas.yview_scroll(1, "units")

if __name__ == "__main__":
    root = tk.Tk()
    app = HexGroupDefiner(root)
    root.mainloop()
