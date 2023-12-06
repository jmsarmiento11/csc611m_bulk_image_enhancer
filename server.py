from PIL import ImageEnhance, Image
import io
import socket
import os
import time

# Server configuration
HOST = '192.168.100.32'  # IP Address
PORT = 12345
INPUT_FOLDER = 'input_images'  # Folder containing working images
OUTPUT_FOLDER = 'output_images'  # Folder to save enhanced images

# Get the directory where output and statistics will be saved
current_directory = os.path.dirname(os.path.abspath(__file__))

# Global variables to track statistics
num_images_processed = 0
start_time = None
machines_used = set()

# Function enhancing the image/s
def enhance_image(image_data):
    try:
        img = Image.open(io.BytesIO(image_data))

        # Enhance image (adjusting sharpness, brightness, and contrast by 10%)
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)  # 50% increase in sharpness

        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.5)  # 50% increase in brightness

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)  # 50% increase in contrast

        return img
    except Exception as e:
        print(f"Error enhancing image: {e}")
        return None

# Save the enhanced image
def save_image(img, idx):
    try:
        output_path = os.path.join(OUTPUT_FOLDER, f"enhanced_image_{idx}.jpg")
        img.save(output_path, format='JPEG')
        print(f"Enhanced image {idx} saved")
    except Exception as e:
        print(f"Error saving enhanced image {idx}: {e}")

# Update statistics
def update_statistics(client_address):
    global num_images_processed
    global start_time
    global machines_used

    num_images_processed += 1

    if start_time is None:
        start_time = time.time()

    machines_used.add(client_address[0])  # Lists the client IP address to the set of machines used

# Function to display summary statistics and export to a text file
def export_statistics():
    global num_images_processed
    global start_time
    global machines_used

    try:
        statistics_file_path = os.path.join(OUTPUT_FOLDER, 'statistics.txt')

        with open(statistics_file_path, 'w') as file:
            if num_images_processed > 0:
                elapsed_time = time.time() - start_time
                file.write(f"Number of images enhanced: {num_images_processed}\n")
                file.write(f"Time elapsed: {elapsed_time:.2f} seconds\n")
                file.write(f"Number of clients used [excluding the server]: {len(machines_used)}\n")
            else:
                file.write("No images processed yet.\n")

        print(f"Statistics file saved at: {statistics_file_path}")

    except Exception as e:
        print(f"Error occurred while saving statistics: {e}")


# Function to start the server
def start_server():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Server listening on port {PORT}...")

    while True:
        conn, addr = server_socket.accept()
        print(f"Connected by {addr}")

        with conn:
            data = conn.recv(4096)
            if not data:
                print("No data received")
            else:
                num_images = int.from_bytes(data[:4], byteorder='big')
                data = data[4:]
                print(f"Number of images to process: {num_images}")

                for idx in range(num_images):
                    input_path = os.path.join(INPUT_FOLDER, f"input_image_{idx}.jpg")
                    if not os.path.exists(input_path):
                        print(f"Input image {idx} not found")
                        continue

                    with open(input_path, 'rb') as file:
                        image_data = file.read()

                    enhanced_image = enhance_image(image_data)
                    if enhanced_image:
                        save_image(enhanced_image, idx)
                        update_statistics(addr)
                        export_statistics()  # Update statistics after processing each image

    server_socket.close()

if __name__ == "__main__":
    start_server()
