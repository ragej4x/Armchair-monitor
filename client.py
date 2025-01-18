import tkinter as tk
from tkinter import simpledialog
from tkinter.ttk import Frame
import socket
import threading
import json


class PaintClient:
    def __init__(self, root, server_ip, server_port):
        self.root = root
        self.root.title("Armchair Monitor - Client")

        self.server_ip = server_ip
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<ButtonRelease-1>", self.end_draw)

        self.brush_color = "black"
        self.eraser_color = "white"
        self.brush_size = 5
        self.start_x = None
        self.start_y = None

        self.canvas_image = self.canvas.create_rectangle(0, 0, 800, 600, fill="white", outline="")

        self.connect_to_server()

        #if ever nag loloko uncomment nyo lng ung time.sleep
        #time.sleep(0.1)


        threading.Thread(target=self.listen_for_updates, daemon=True).start()

    def connect_to_server(self):
        try:
            self.socket.connect((self.server_ip, self.server_port))
            print("Connected to the server.")
        except Exception as e:
            print(f"Unable to connect to the server: {e}")
            self.root.destroy()

    def listen_for_updates(self):
        data_buffer = ""
        while True:
            try:
                chunk = self.socket.recv(4096).decode()
                if not chunk:
                    break
                data_buffer += chunk
                while "\n" in data_buffer:
                    message, data_buffer = data_buffer.split("\n", 1)
                    action = json.loads(message)
                    self.handle_server_action(action)
            except (ConnectionResetError, json.JSONDecodeError):
                print("Disconnected from the server.")
                break
        self.socket.close()

    def handle_server_action(self, action):
        action_type = action.get("action")
        if action_type == "line":
            self.draw_line(action)
        elif action_type == "rectangle":
            self.draw_rectangle(action)
        elif action_type == "oval":
            self.draw_oval(action)
        elif action_type == "text":
            self.draw_text(action)
        elif action_type == "clear":
            self.clear_canvas()

    def draw_line(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle=tk.ROUND, smooth=True)

    def draw_rectangle(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=width)

    def draw_oval(self, action):
        x1, y1, x2, y2 = action["x1"], action["y1"], action["x2"], action["y2"]
        color = action["color"]
        width = action["width"]
        self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)

    def draw_text(self, action):
        x, y, text, color, size = action["x"], action["y"], action["text"], action["color"], action["size"]
        self.canvas.create_text(x, y, text=text, fill=color, font=("Arial", size))

    def clear_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, 800, 600, fill="white", outline="")

    def paint(self, event):
        x, y = event.x, event.y
        self.draw_action("line", self.start_x, self.start_y, x, y)
        self.start_x, self.start_y = x, y

    def start_draw(self, event):
        self.start_x, self.start_y = event.x, event.y

    def end_draw(self, event):
        pass

    def draw_action(self, action_type, x1, y1, x2, y2):
        if x1 is None or y1 is None:
            return

        if action_type == "line":
            self.canvas.create_line(x1, y1, x2, y2, fill=self.brush_color, width=self.brush_size, capstyle=tk.ROUND, smooth=True)

        self.send_action_to_server({
            "action": action_type,
            "x1": x1, "y1": y1,
            "x2": x2, "y2": y2,
            "color": self.brush_color,
            "width": self.brush_size
        })

    def send_action_to_server(self, action):
        try:
            self.socket.sendall((json.dumps(action) + "\n").encode())
        except Exception as e:
            print(f"Error sending action to server: {e}")


root = tk.Tk()
root.withdraw() 
server_ip = simpledialog.askstring("Server IP", "Enter server IP, example 127.0.0.1")
root.deiconify() 
server_port = 9999
app = PaintClient(root, server_ip, server_port)
root.mainloop()
