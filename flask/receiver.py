from flask import Flask, request, send_from_directory
import requests
import subprocess
import time
import threading
from werkzeug.serving import make_server

app = Flask(__name__)

shutdown_event = threading.Event()
server = None

def run_flask_app():
    # app.run(host='10.10.1.2', port=5000)
    make_server('10.10.1.2', 5000, app)
    
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route('/shutdown', methods=['GET'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

# Counter to keep track of received files
received_file_count = 0
expected_file_count = 4  # Set the expected number of files

waiting_for_sender_confirmation = True

# Define the IP address of the receiver node
sender_node_ip = "10.10.1.1:5000"
self_node_ip = "10.10.1.2:5000"

@app.route('/send_confirmation')
def send_confirmation():
    global waiting_for_sender_confirmation

    # This endpoint will be called by the sender to confirm completion
    waiting_for_sender_confirmation = False
    return "OK"

def send_confirmation_to_sender():
    global waiting_for_sender_confirmation

    # Send a confirmation request to the sender by making an HTTP request
    confirmation_endpoint = f"http://{sender_node_ip}/send_confirmation"
    response = requests.get(confirmation_endpoint)
    confirmation_text = response.text

    if confirmation_text == "OK":
        waiting_for_sender_confirmation = False
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
    # Define the command to run the separate Python file
    command = ["python", "../mnist_model/plaintext_aggregate.py"]
    
    if received_file_count == expected_file_count:
        try:
            # Execute the command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing process_files.py: {e}")
    else: 
        print("INCOMPLETE FILES")

def send_files_back():
    global waiting_for_sender_confirmation
    # Define the endpoint on the sender node to handle file receive
    endpoint_on_sender = f"http://{sender_node_ip}/receive_file"

    # Record the start time
    start_time = time.time()
    
    # Send back the four files
    for i in range(4):
        file_path = f"../mnist_model/aggregate/plain_weights{i}.json"  # Update with the actual file paths
        response_from_sender = send_file_to_sender(file_path, endpoint_on_sender)
        
        print(f"Response from sender node: {response_from_sender}")
        
    # Record the completion time
    end_time = time.time()
    
    waiting_for_sender_confirmation = True
    # Continuously check for confirmation from the sender
    while waiting_for_sender_confirmation:
        send_confirmation_to_sender()
        time.sleep(1)  # Wait for 1 second before checking again
        
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

if __name__ == '__main__':
    # app.run(host='10.10.1.2', port=5000)
    print('Starting Flask development server...')
    # run_flask_app()
    server = make_server('10.10.1.2', 5000, app)
    server.serve_forever()

    while waiting_for_sender_confirmation:
        time.sleep(1)  # Wait for 1 second before checking again
                             
    print('Stopping Flask development server...')
    # server.shutdown()
    # Register a signal handler for Ctrl+C
    raise KeyboardInterrupt()
    signal.signal(signal.SIGINT, lambda signum, frame: simulate_ctrl_c())
    print('Server has stopped.')
    
    run_process_file()
        
    send_files_back()
    
    endpoint_on_sender = f"http://{sender_node_ip}/shutdown"
    response = requests.get(endpoint_on_sender)
    