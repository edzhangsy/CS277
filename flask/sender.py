from flask import Flask
import requests
import subprocess
import time

app = Flask(__name__)

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
    for i in range(0, 4):
        file_path = f"../mnist_model/state/torch_weights{i}.json"  # Update with the actu
al file paths
        response_from_receiver = send_file_to_receiver(file_path, endpoint_on_receiver)

        print(f"Response from receiver node: {response_from_receiver}")

     # Record the completion time
    end_time = time.time()

    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

def send_file_to_receiver(file_path):
    # Read the file and send it in the request
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file.read())}
        response = requests.post(endpoint_on_receiver, files=files)

    # Return the response from the receiver node
    return response.text

if __name__ == '__main__':
    #app.run(host='10.10.1.1', port=5000)

    # Run the initial Python file
    if run_initial_process():
        # Send the four files after the initial process
        send_files()
