import tkinter as tk
import socket
import threading
import pickle

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Paint Client")

        # Canvas setup
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Networking setup
        self.client_socket = None
        threading.Thread(target=self.start_client, daemon=True).start()

    def start_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("localhost", 12345))
            print("Connected to server!")
            self.receive_events()
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.root.destroy()

    def receive_events(self):
        """Continuously receive events from the server."""
        try:
            while True:
                data = self.client_socket.recv(4096)
                if not data:
                    break
                event = pickle.loads(data)
                self.handle_event(event)
        except Exception as e:
            print(f"Error receiving events: {e}")
            self.client_socket.close()
            self.root.destroy()

    def handle_event(self, event):
        """Handle drawing events received from the server."""
        event_type = event["type"]
        data = event["data"]

        if event_type == "draw" and data["tool"] == "brush":
            self.canvas.create_line(data["x1"], data["y1"], data["x2"], data["y2"], fill=data["color"], width=data["size"], capstyle=tk.ROUND, smooth=True)
        elif event_type == "clear":
            self.canvas.delete("all")


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
