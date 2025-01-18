import socket

# Step 1: Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP socket

# Step 2: Define IP and Port
host = "0.0.0.0"  # Listen on all available network interfaces
port = 12345      # Choose a port number (>1024 and <65535)

# Step 3: Bind the socket to an address and port
server_socket.bind((host, port))
print(f"Server started on {host}:{port}")

# Step 4: Start listening for connections
server_socket.listen(5)  # The server will accept up to 5 simultaneous connections
print("Waiting for a connection...")

while True:
    # Step 5: Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    # Step 6: Send and receive data
    welcome_message = "Welcome to the server!"
    client_socket.send(welcome_message.encode('utf-8'))  # Send a message to the client
    
    data = client_socket.recv(1024).decode('utf-8')  # Receive data from the client
    print(f"Received from client: {data}")
    
    # Step 7: Close the connection
    client_socket.close()
    print(f"Connection with {client_address} closed.")
