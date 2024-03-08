from flask import Flask
import requests

app = Flask(__name__)

# Define the IP address of the receiver node
receiver_node_ip = "10.0.1.2"

@app.route('/')
def send_file():
    file_path = "./hello_world.txt"  # Update with the actual file path
    response_from_receiver = send_file_to_receiver(file_path)

    return f"Response from receiver node: {response_from_receiver}"

def send_file_to_receiver(file_path):
    # Define the endpoint on the receiver node to handle file uploads
    endpoint_on_receiver = f"http://{receiver_node_ip}/receive_file"

    # Read the file and send it in the request
    with open(file_path, 'rb') as file:
        files = {'file': (file_path, file.read())}
        response = requests.post(endpoint_on_receiver, files=files)

    # Return the response from the receiver node
    return response.text

if __name__ == '__main__':
    app.run(host='10.0.1.1', port=5000)
