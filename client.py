import socket
import os

# Server configuration
SERVER_HOST = '192.168.100.32'  # Replace with the server's IP address
SERVER_PORT = 12345
INPUT_FOLDER = 'input_images'  # Folder containing input images

def send_images_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    # Send the number of images to be processed to the server
    num_images = len(os.listdir(INPUT_FOLDER))
    client_socket.sendall(num_images.to_bytes(4, byteorder='big'))

    # Send each image to the server for processing
    for idx, filename in enumerate(os.listdir(INPUT_FOLDER), 1):
        with open(os.path.join(INPUT_FOLDER, filename), 'rb') as f:
            image_data = f.read()
            client_socket.sendall(image_data)

    client_socket.close()

if __name__ == "__main__":
    send_images_to_server()
