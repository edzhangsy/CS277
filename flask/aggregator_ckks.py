from flask import Flask, request, send_from_directory
import requests
import subprocess
import time
import threading
from werkzeug.serving import make_server
from werkzeug.serving import run_simple
import multiprocessing
from werkzeug import Request, Response, run_simple

app = Flask(__name__)
    
def run_flask_app():
    # app.run(host='10.10.1.2', port=5000)
    make_server('10.10.1.2', 5000, app)

# Counter to keep track of received files
received_file_count = 0
expected_file_count = 8  # Set the expected number of files

waiting_for_sender1_confirmation = True
waiting_for_sender2_confirmation = True

# Define the IP address of the receiver node
sender1_node_ip = "10.10.1.1:5000"
sender1_node = "10.10.1.1"
sender2_node_ip = "10.10.1.3:5000"
sender2_node = "10.10.1.3"
self_node_ip = "10.10.1.2:5000"

@app.route('/send_confirmation')
def send_confirmation():
    # Accessing information about the request
    client_ip = request.remote_addr
    print(f"Confirmation received from IP: {client_ip}")
    
    global waiting_for_sender1_confirmation
    global waiting_for_sender2_confirmation

    # This endpoint will be called by the sender to confirm completion
    if client_ip == sender1_node:
        waiting_for_sender1_confirmation = False
    if client_ip == sender2_node:
        waiting_for_sender2_confirmation = False
    return "OK"

def send_confirmation_to_sender(sender_node_ip):
    global waiting_for_sender1_confirmation
    global waiting_for_sender2_confirmation

    # Send a confirmation request to the sender by making an HTTP request
    confirmation_endpoint = f"http://{sender_node_ip}/send_confirmation"
    response = requests.get(confirmation_endpoint)
    confirmation_text = response.text

    if sender_node_ip == sender1_node_ip:
        if confirmation_text == "OK":
            waiting_for_sender1_confirmation = False
            print("Confirmation received from sender.")
        else:
            print("Waiting for confirmation from sender...")
            
    if sender_node_ip == sender2_node_ip:
        if confirmation_text == "OK":
            waiting_for_sender2_confirmation = False
            print("Confirmation received from sender.")
        else:
            print("Waiting for confirmation from sender...")

@app.route('/receive_file', methods=['POST'])
def receive_file():
    global received_file_count

    # Get the uploaded file from the request
    uploaded_file = request.files['file']

    # Save the received file
    file_path = f"{uploaded_file.filename}"
    uploaded_file.save(file_path)

    # Increment the received file count
    received_file_count += 1

    return f"File received and saved: {uploaded_file.filename}"

def run_process_file():
    global received_file_count
    
    # Define the command to run the separate Python file
    command = ["python", "../mnist_model/ckks_aggregate_fl.py"]
    received_file_count = 0
    
    try:
        # Execute the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing process_files.py: {e}")

def send_files_back():
    global waiting_for_sender1_confirmation
    # Define the endpoint on the sender node to handle file receive
    endpoint_on_sender = f"http://{sender1_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()
    
    # Send back the four files
    for i in range(4):
        file_path = f"../mnist_model/aggregate/ckks_weights{i}.json"  # Update with the actual file paths
        response_from_sender = send_file_to_sender(file_path, endpoint_on_sender)
        
        print(f"Response from sender node: {response_from_sender}")
        
    # Record the completion time
    end_time = time.time()
    
    waiting_for_sender1_confirmation = True
    
    # Continuously check for confirmation from the sender
    while waiting_for_sender1_confirmation:
        send_confirmation_to_sender(sender1_node_ip)
        time.sleep(1)  # Wait for 1 second before checking again
        
    waiting_for_sender1_confirmation = True
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")
    
    ############################################################################################
    global waiting_for_sender2_confirmation
    # Define the endpoint on the sender node to handle file receive
    endpoint_on_sender = f"http://{sender2_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()
    
    # Send back the four files
    for i in range(4):
        file_path = f"../mnist_model/aggregate/ckks_weights{i}.json"  # Update with the actual file paths
        response_from_sender = send_file_to_sender(file_path, endpoint_on_sender)
        
        print(f"Response from sender node: {response_from_sender}")
        
    # Record the completion time
    end_time = time.time()
    
    waiting_for_sender2_confirmation = True
    
    # Continuously check for confirmation from the sender
    while waiting_for_sender2_confirmation:
        send_confirmation_to_sender(sender2_node_ip)
        time.sleep(1)  # Wait for 1 second before checking again
        
    waiting_for_sender2_confirmation = True
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

def send_file_to_sender(file_path, endpoint_on_sender):
    # Read the file and send it back in the response
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file.read())}
        response = requests.post(endpoint_on_sender, files=files)
        
    # Return the response from the receiver node
    return response.text

def send_context():
    global waiting_for_sender1_confirmation
    # Define the endpoint on the sender node to handle file receive
    endpoint_on_sender = f"http://{sender1_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()
    
    file_path = f"../mnist_model/ckks/context.pkl"  # Update with the actual file paths
    response_from_sender = send_file_to_sender(file_path, endpoint_on_sender)
    
    print(f"Response from sender node: {response_from_sender}")
        
    # Record the completion time
    end_time = time.time()
    
    waiting_for_sender1_confirmation = True
    
    # Continuously check for confirmation from the sender
    while waiting_for_sender1_confirmation:
        send_confirmation_to_sender(sender1_node_ip)
        time.sleep(1)  # Wait for 1 second before checking again
        
    waiting_for_sender1_confirmation = True
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")
    
    ############################################################################################
    global waiting_for_sender2_confirmation
    # Define the endpoint on the sender node to handle file receive
    endpoint_on_sender = f"http://{sender2_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()
    
    file_path = f"../mnist_model/ckks/context.pkl"  # Update with the actual file paths
    response_from_sender = send_file_to_sender(file_path, endpoint_on_sender)
    
    print(f"Response from sender node: {response_from_sender}")
        
    # Record the completion time
    end_time = time.time()
    
    waiting_for_sender2_confirmation = True
    
    # Continuously check for confirmation from the sender
    while waiting_for_sender2_confirmation:
        send_confirmation_to_sender(sender2_node_ip)
        time.sleep(1)  # Wait for 1 second before checking again
        
    waiting_for_sender2_confirmation = True
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    print(f"Total time elapsed: {elapsed_time:.2f} seconds")

if __name__ == '__main__':
    send_context()
    
    for count in range(1):
        # app.run(host='10.10.1.2', port=5000)
        print('Starting Flask development server...')
        # run_flask_app()
        # server = make_server('10.10.1.2', 5000, app)
        # server.serve_forever()
        run_simple('10.10.1.2', 5000, app, use_debugger=False)

        while received_file_count < expected_file_count:
            time.sleep(1)  # Wait for 1 second before checking again
            
        while waiting_for_sender1_confirmation or waiting_for_sender2_confirmation:
            time.sleep(1)  # Wait for 1 second before checking again
                                
        print('Stopping Flask development server...')
        # server.shutdown()
        
        print('Server has stopped.')
        
        run_process_file()
            
        send_files_back()