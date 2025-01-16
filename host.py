import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from tkinter.ttk import Button, Frame
from PIL import Image, ImageDraw, ImageTk

class PaintApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint Application")
        
        self.brush_color = "black"
        self.eraser_color = "white"
        self.brush_size = 5
        self.tool = "brush"
        self.start_x = None
        self.start_y = None
        self.current_shape = None
        self.selection_rectangle = None
        self.selected_item = None
        self.is_dragging = False

        self.image = Image.new("RGB", (1024, 600), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.layout = Frame(self.root)
        self.layout.pack(fill=tk.BOTH, expand=True)

        #
        self.create_toolbar()

        self.canvas = tk.Canvas(self.layout, bg="white", width=800, height=600, cursor="cross")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)
        self.canvas.bind("<Button-3>", self.show_context_menu)
        self.canvas.bind("<Escape>", self.deselect_tool)


    def create_toolbar(self):
        toolbar = Frame(self.layout)
        toolbar.pack(side=tk.LEFT, fill=tk.Y)

        # Brush tool
        Button(toolbar, text="Brush", command=lambda: self.select_tool("brush")).pack(padx=2, pady=2)

        # Eraser tool
        Button(toolbar, text="Eraser", command=lambda: self.select_tool("eraser")).pack(padx=2, pady=2)

        # Line tool
        Button(toolbar, text="Line", command=lambda: self.select_tool("line")).pack(padx=2, pady=2)

        # Rectangle tool
        Button(toolbar, text="Rectangle", command=lambda: self.select_tool("rectangle")).pack(padx=2, pady=2)

        # Oval tool
        Button(toolbar, text="Oval", command=lambda: self.select_tool("oval")).pack(padx=2, pady=2)

        # Text tool
        Button(toolbar, text="Text", command=lambda: self.select_tool("text")).pack(padx=2, pady=2)

        # Selection tool
        Button(toolbar, text="Select", command=lambda: self.select_tool("select")).pack(padx=2, pady=2)

        # Color chooser
        Button(toolbar, text="Color", command=self.choose_color).pack(padx=2, pady=2)

        # Brush size
        tk.Scale(toolbar, from_=1, to=100, orient=tk.HORIZONTAL, label="      Brush Size", command=self.change_brush_size).pack(padx=2, pady=2)

        # Save button
        Button(toolbar, text="Save", command=self.save_image).pack(padx=2, pady=2)

        Button(toolbar, text="Clear", command=self.clear_canvas).pack(padx=2, pady=2)


    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (1024, 600), "white")
        self.draw = ImageDraw.Draw(self.image)


    def select_tool(self, tool):
        self.tool = tool

    def choose_color(self):
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color

    def change_brush_size(self, value):
        self.brush_size = int(value)

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.tool == "text":
            self.add_text(event)
        elif self.tool == "select":
            if self.selection_rectangle:
                self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="blue", dash=(2, 2))
        elif self.tool == "move" and self.selection_rectangle:
            self.is_dragging = True

    def paint(self, event):
        x, y = event.x, event.y

        if self.tool == "brush":
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.brush_color, width=self.brush_size, capstyle=tk.ROUND, smooth=True)
            self.draw.line([self.start_x, self.start_y, x, y], fill=self.brush_color, width=self.brush_size)
            self.start_x, self.start_y = x, y
        elif self.tool == "eraser":
            self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.eraser_color, width=self.brush_size, capstyle=tk.ROUND, smooth=True)
            self.draw.line([self.start_x, self.start_y, x, y], fill=self.eraser_color, width=self.brush_size)
            self.start_x, self.start_y = x, y
        elif self.tool == "select" and self.selection_rectangle:
            self.canvas.coords(self.selection_rectangle, self.start_x, self.start_y, x, y)
        elif self.tool == "move" and self.is_dragging:
            x_offset = x - self.start_x
            y_offset = y - self.start_y
            self.move_selection(x_offset, y_offset)
            self.start_x, self.start_y = x, y



    def end_draw(self, event):
        if self.tool in ["line", "rectangle", "oval"]:
            x, y = event.x, event.y
            if self.tool == "line":
                self.canvas.create_line(self.start_x, self.start_y, x, y, fill=self.brush_color, width=self.brush_size)
                self.draw.line([self.start_x, self.start_y, x, y], fill=self.brush_color, width=self.brush_size)
            elif self.tool == "rectangle":
                self.canvas.create_rectangle(self.start_x, self.start_y, x, y, outline=self.brush_color, width=self.brush_size)
                self.draw.rectangle([self.start_x, self.start_y, x, y], outline=self.brush_color, width=self.brush_size)
            elif self.tool == "oval":
                self.canvas.create_oval(self.start_x, self.start_y, x, y, outline=self.brush_color, width=self.brush_size)
                self.draw.ellipse([self.start_x, self.start_y, x, y], outline=self.brush_color, width=self.brush_size)
        
        elif self.tool == "move":
            self.is_dragging = False
        self.start_x, self.start_y = None, None

    def move_selection(self, x_offset, y_offset):
        if self.selection_rectangle:
            coords = self.canvas.coords(self.selection_rectangle)
            self.canvas.move(self.selection_rectangle, x_offset, y_offset)
            cropped = self.image.crop((coords[0], coords[1], coords[2], coords[3]))
            self.image.paste((255, 255, 255), (int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])))
            new_coords = (coords[0] + x_offset, coords[1] + y_offset, coords[2] + x_offset, coords[3] + y_offset)
            self.image.paste(cropped, (int(new_coords[0]), int(new_coords[1])))
            self.redraw_canvas()

    def add_text(self, event):
        text = simpledialog.askstring("Text Input", "Enter text:")
        if text:
            x, y = event.x, event.y
            self.canvas.create_text(x, y, text=text, fill=self.brush_color, font=("Arial", self.brush_size * 2))
            self.draw.text((x, y), text, fill=self.brush_color)

    def show_context_menu(self, event):
        if self.tool == "select" and self.selection_rectangle:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Delete", command=self.delete_selection)
            menu.post(event.x_root, event.y_root)

    def delete_selection(self):
        if self.selection_rectangle:
            coords = self.canvas.coords(self.selection_rectangle)
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None
            self.draw.rectangle(coords, fill="white")
            self.redraw_canvas()

    def redraw_canvas(self):
        self.canvas.delete("all")
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def deselect_tool(self, event):
        if self.selection_rectangle:
            self.canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None
        self.selected_item = None
        self.tool = "brush"

    def save_image(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            self.image.save(file_path)


root = tk.Tk()
app = PaintApp(root)
root.mainloop()