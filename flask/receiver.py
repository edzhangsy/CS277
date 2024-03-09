from flask import Flask, request
import subprocess

app = Flask(__name__)

# Counter to keep track of received files
received_file_count = 0
expected_file_count = 4  # Set the expected number of files

@app.route('/receive_file', methods=['POST'])
def receive_file():
    global received_file_count

    # Get the uploaded file from the request
    uploaded_file = request.files['file']

    # Save the received file
    file_path = f"state/{uploaded_file.filename}"
    uploaded_file.save(file_path)

    # Increment the received file count
    received_file_count += 1

    if received_file_count == expected_file_count:
        # Run the separate Python file after receiving the expected number of files
        run_process_file()

    return f"File received and saved: {uploaded_file.filename}"

def run_process_file():
    # Define the command to run the separate Python file
    command = ["python", "../mnist_model/tenseal_ckks.py"]

    try:
        # Execute the command
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing process_files.py: {e}")

if __name__ == '__main__':
    app.run(host='10.10.1.2', port=5000)
