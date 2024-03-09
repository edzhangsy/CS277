from flask import Flask, send_from_directory
import requests
import subprocess
import time

app = Flask(__name__)
waiting_for_receiver_confirmation = True

# Define the IP address of the receiver node
receiver_node_ip = "10.10.1.2:5000"

def run_initial_process():
    # Define the command to run the initial Python file
    initial_command = ["python", "../mnist_model/mnist.py"]

    try:
        # Execute the command
        subprocess.run(initial_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing initial_process.py: {e}")
        return False

    return True

def send_files():
    # Define the endpoint on the receiver node to handle file uploads
    endpoint_on_receiver = f"http://{receiver_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()

    # Send four files
    for i in range(4):
        file_path = f"../mnist_model/state/torch_weights{i}.json"  # Update with the actual file paths
        response_from_receiver = send_file_to_receiver(file_path, endpoint_on_receiver)

        print(f"Response from receiver node: {response_from_receiver}")

    # Record the completion time
    end_time = time.time()

    # Continuously check for confirmation from the receiver
    while waiting_for_receiver_confirmation:
        send_confirmation_to_receiver()
        time.sleep(1)  # Wait for 1 second before checking again
        
        # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

def send_file_to_receiver(file_path, endpoint_on_receiver):
    # Read the file and send it in the request
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file.read())}
        response = requests.post(endpoint_on_receiver, files=files)

    # Return the response from the receiver node
    return response.text

def send_confirmation_to_receiver():
    global waiting_for_receiver_confirmation

    # Send a confirmation request to the receiver by making an HTTP request
    confirmation_endpoint = f"http://{receiver_node_ip}/send_confirmation"
    response = requests.get(confirmation_endpoint)
    confirmation_text = response.text

    if confirmation_text == "OK":
        waiting_for_receiver_confirmation = False
        print("Confirmation received from receiver.")
    else:
        print("Waiting for confirmation from receiver...")

def download_processed_files():
    # Define the endpoint on the receiver node to handle file downloads
    endpoint_on_receiver = f"http://{receiver_node_ip}/download_file"

    # Download the four processed files
    for i in range(0, 4):
        filename = f"plain_weights{i}.json"
        download_file_from_receiver(endpoint_on_receiver, filename)

def download_file_from_receiver(endpoint_on_receiver, filename):
    # Save the downloaded file locally
    response = requests.get(f"{endpoint_on_receiver}/{filename}")
    with open(f"../mnist_model/aggregate/{filename}", 'wb') as file:
        file.write(response.content)
        
        print(f"File downloaded from receiver: {filename}")

# Flask route to handle file downloads
@app.route('/download_file/')
def download_file(filename):
    return send_from_directory("../mnist_model/aggregate/", filename)

if __name__ == '__main__':
    #app.run(host='10.10.1.1', port=5000)

    # Run the initial Python file
    if run_initial_process():
        # Send the four files after the initial process
        send_files()

        # Download the processed files from the receiver
        download_processed_files()

        # Run the Flask app to handle file downloads
        #app.run(host='10.10.1.1', port=5000)