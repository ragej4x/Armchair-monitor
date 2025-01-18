import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageDraw, ImageTk
import socket
import threading
import json


class PaintClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint Client")

        self.brush_color = "black"
        self.eraser_color = "white"
        self.brush_size = 5
        self.image = Image.new("RGB", (1024, 600), "white")
        self.draw = ImageDraw.Draw(self.image)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "127.0.0.1" 
        self.port = 12345
        self.connect_to_server()

        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        threading.Thread(target=self.receive_updates, daemon=True).start()

    def connect_to_server(self):
        try:
            self.client_socket.connect(('localhost', self.port))
            print("Connected to the server!")
        except Exception as e:
            print(f"Failed to connect to the server: {e}")
            self.root.destroy()

    def receive_updates(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
                if data:
                    action = json.loads(data)
                    self.process_action(action)
            except (ConnectionResetError, json.JSONDecodeError):
                print("Disconnected from server.")
                break

    def process_action(self, action):
        act = action.get("action")
        if act == "line":
            self.draw_line(action)
        elif act == "rectangle":
            self.draw_rectangle(action)
        elif act == "oval":
            self.draw_oval(action)
        elif act == "text":
            self.draw_text(action)
        elif act == "clear":
            self.clear_canvas()

    def draw_line(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND, smooth=True)
        self.draw.line([x1, y1, x2, y2], fill=color, width=width)

    def draw_rectangle(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=width)
        self.draw.rectangle([x1, y1, x2, y2], outline=color, width=width)

    def draw_oval(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)
        self.draw.ellipse([x1, y1, x2, y2], outline=color, width=width)

    def draw_text(self, action):
        x, y = action["x"], action["y"]
        text = action["text"]
        color = action["color"]
        size = action["size"]
        self.canvas.create_text(x, y, text=text, fill=color, font=("Arial", size))
        self.draw.text((x, y), text, fill=color)

    def clear_canvas(self):
        self.canvas.delete("all")
        self.image = Image.new("RGB", (1024, 600), "white")
        self.draw = ImageDraw.Draw(self.image)


root = tk.Tk()
app = PaintClient(root)
root.mainloop()
