from flask import Flask, send_from_directory
import requests
import subprocess
import time

app = Flask(__name__)

# Counter to keep track of received files
received_file_count = 0
expected_file_count = 4  # Set the expected number of files

waiting_for_receiver_confirmation = True

# Define the IP address of the receiver node
receiver_node_ip = "10.10.1.2:5000"

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

# Flask route to handle file receive
@app.route('/receive_file/', methods=['POST'])
def receive_file(filename):
    global received_file_count
    global waiting_for_sender_confirmation

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

    try:
        # Execute the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing process_files.py: {e}")

if __name__ == '__main__':
    #app.run(host='10.10.1.1', port=5000)

    # Run the initial Python file
    if run_initial_process():
        # Send the four files after the initial process
        send_files()
        
    waiting_for_receiver_confirmation = True
    while waiting_for_receiver_confirmation:
        time.sleep(1)  # Wait for 1 second before checking again
    
    if received_file_count == expected_file_count:
        # Run the separate Python file after receiving the expected number of files
        run_process_file()
    else:
        print('ERROR: FILES INCOMPLETE')
    
        # Run the Flask app to handle file downloads
        #app.run(host='10.10.1.1', port=5000)