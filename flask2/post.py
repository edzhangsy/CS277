import requests

def requests_post(address, files):
    requests.post(address, files=files)
    return
