from urllib.parse import urlparse
import requests
import base64

from node.models import Node


def get_remote_authors_json(request):
    """
    Get authors from remote nodes and save them to the local database.
    """
  
    remote_authors = []
    failed_nodes_urls = []
    
    try:
        # get authors for each remote node
        for node in Node.objects.filter(is_whitelisted=True):
            
            # endpoint to get authors from remote node    
            authors_remote_endpoint = f"{node.remote_node_url.rstrip('/')}/api/authors/"
            
            # my local node's host with scheme
            parsed_url = urlparse(request.build_absolute_uri())
            host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # credentials to access remote node (encoded in base64)
            credentials = f"{node.remote_username}:{node.remote_password}"
            base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
            
            # make the request
            response = requests.get(
                authors_remote_endpoint,
                # params={"host": host_with_scheme},
                headers={"Authorization": f"Basic {base64_credentials}"},
            )
            
            # if successful, get the authors
            if response.status_code == 200:
                authors_data = response.json()["authors"]
                remote_authors.append(authors_data)
            else:
                failed_nodes_urls.append([node.remote_node_url, response.status_code])
            
        # show failed nodes
        if failed_nodes_urls:
            print(f"Could not get remote author(s) from these nodes: {failed_nodes_urls}")
        
        print(f"Got remote authors successfully: {remote_authors}")
        return remote_authors   
    except Exception as e:
        print("Could not get remote authors")
        raise e