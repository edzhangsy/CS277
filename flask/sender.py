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

shutdown_event = threading.Event()
server = None

def get_token(q: multiprocessing.Queue) -> None:
    @Request.application
    def app(request: Request) -> Response:
        q.put(request.args["token"])
        return Response("", 204)

    run_simple('10.10.1.1', 5000, app)
    
def run_flask_app():
    # app.run(host='10.10.1.1', port=5000)
    make_server('10.10.1.1', 5000, app)
    
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

waiting_for_receiver_confirmation = True

# Define the IP address of the receiver node
receiver_node_ip = "10.10.1.2:5000"
self_node_ip = "10.10.1.1:5000"

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

@app.route('/send_confirmation')
def send_confirmation():
    global waiting_for_receiver_confirmation

    # This endpoint will be called by the receiver to confirm completion
    waiting_for_receiver_confirmation = False
    return "OK"

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
    global waiting_for_receiver_confirmation
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

    waiting_for_receiver_confirmation = True
    
    # Continuously check for confirmation from the receiver
    while waiting_for_receiver_confirmation:
        send_confirmation_to_receiver()
        time.sleep(1)  # Wait for 1 second before checking again
    
    waiting_for_receiver_confirmation = True
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

# Flask route to handle file receive
@app.route('/receive_file/', methods=['POST'])
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
    command = ["python", "../mnist_model/replace_weights_mnist.py"]

    if received_file_count == expected_file_count:
        try:
            # Execute the command
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing process_files.py: {e}")
    else: 
        print("INCOMPLETE FILES")

if __name__ == '__main__':
    #app.run(host='10.10.1.1', port=5000)
    
    # Run the initial Python file
    # if run_initial_process():
    #     # Send the four files after the initial process
    #     send_files()
    
    run_initial_process()
    
    for count in range(3):
        send_files()
        # endpoint_on_receiver = f"http://{receiver_node_ip}/shutdown"
        # response = requests.get(endpoint_on_receiver)
        
        # Run the Flask app to handle file downloads
        # app.run(host='10.10.1.1', port=5000)
        print('Starting Flask development server...')
        # run_flask_app()
        # server = make_server('10.10.1.1', 5000, app)
        # server.serve_forever()
        run_simple('10.10.1.1', 5000, app, use_debugger=False)
            
        while waiting_for_receiver_confirmation:
            time.sleep(1)  # Wait for 1 second before checking again
        
        print('Stopping Flask development server...')
        # server.shutdown()

        print('Server has stopped.')
        print('Server has stopped.')
        run_process_file()
        expected_file_count = expected_file_count * count
    