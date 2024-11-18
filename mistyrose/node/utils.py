import requests
from requests.auth import HTTPBasicAuth

def fetch_remote_data(node, endpoint):
    """
    Fetch data from a remote node.
    """
    try:
        response = requests.get(
            f"{node.host}{endpoint}",
            auth=HTTPBasicAuth(node.username, node.password)
        )
        response.raise_for_status()  # Raise exception for non-200 responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to remote node: {str(e)}")
    
def send_data_to_remote(node, endpoint, data):
    """
    Send data to a remote node via POST request.
    """
    try:
        response = requests.post(
            f"{node.host}{endpoint}",
            json=data,  # Send the data as JSON in the request body
            auth=HTTPBasicAuth(node.username, node.password)
        )
        response.raise_for_status()  # Raise exception for non-200 responses
        return response.json()  # Return the JSON response
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to remote node: {str(e)}")