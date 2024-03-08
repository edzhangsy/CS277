from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_file', methods=['POST'])
def receive_file():
    # Get the uploaded file from the request
    uploaded_file = request.files['file']

    # Save the received file
    uploaded_file.save(uploaded_file.filename)

    return f"File received and saved: {uploaded_file.filename}"

if __name__ == '__main__':
    app.run(host='10.0.1.2', port=5000)
