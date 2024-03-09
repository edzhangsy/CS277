from flask import Flask, request, send_from_directory
import requests
import subprocess
import time

app = Flask(__name__)

# Counter to keep track of received files
received_file_count = 0
expected_file_count = 4  # Set the expected number of files

waiting_for_sender_confirmation = True

@app.route('/send_confirmation')
def send_confirmation():
    global waiting_for_sender_confirmation

    # This endpoint will be called by the sender to confirm completion
    waiting_for_sender_confirmation = False
    return "OK"

@app.route('/receive_file', methods=['POST'])
def receive_file():
    global received_file_count
    global waiting_for_sender_confirmation

    # Get the uploaded file from the request
    uploaded_file = request.files['file']

    # Save the received file
    file_path = f"{uploaded_file.filename}"
    uploaded_file.save(file_path)

    # Increment the received file count
    received_file_count += 1

    if received_file_count == expected_file_count:
        # Run the separate Python file after receiving the expected number of files
        run_process_file()

        # Send back the four files to the sender after the Python file finishes
        #send_files_back()

    return f"File received and saved: {uploaded_file.filename}"

def run_process_file():
    # Define the command to run the separate Python file
    command = ["python", "../mnist_model/plaintext_aggregate.py"]

    try:
        # Execute the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing process_files.py: {e}")

def send_files_back():
    # Define the endpoint on the sender node to handle file downloads
    endpoint_on_sender = "http://10.10.1.1:5000/download_file"

    # Send back the four files
    for i in range(0, 4):
        file_path = f"../mnist_model/aggregate/plain_weights{i}.json"  # Update with the
actual file paths
        send_file_to_sender(file_path, endpoint_on_sender)

def send_file_to_sender(file_path, endpoint_on_sender):
    # Read the file and send it back in the response
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file.read())}
        requests.post(endpoint_on_sender, files=files)

if __name__ == '__main__':
    app.run(host='10.10.1.2', port=5000)

    while waiting_for_sender_confirmation:
        time.sleep(1)  # Wait for 1 second before checking again

    send_files_back()