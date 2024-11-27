from urllib.parse import urlparse
import requests
import base64
from node.models import Node
from django.conf import settings

def get_remote_authors(request):
    """
    Get authors from remote nodes and save them to the local database if not already created.
    """
  
    from users.models import Author
    
    remote_authors = []
    failed_nodes_urls = []
    
    try:
        # get authors for each remote node
        for node in Node.objects.filter(is_whitelisted=True):
            
            # endpoint to get authors from remote node    
            # authors_remote_endpoint = f"{node.remote_node_url.rstrip('/')}/api/authors/"
            authors_remote_endpoint = f"{node.remote_node_url.rstrip('/')}/api/authors/all"
            print(f"INSIDE GET_REMOTE_AUTHORS: {authors_remote_endpoint}")
            
            # my local node's host with scheme
            parsed_url = urlparse(request.build_absolute_uri())
            print(f"INSIDE GET_REMOTE_AUTHORS PARSED URL: {parsed_url}")
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
            
            
            print(f"GET REMOTE AUTHORS RESPONSE {response}")
            
            if response.status_code == 200:                
                authors_data = response.json()
                
                # get usernames from authors_data
                displayNames = [author['displayName'] for author in authors_data]
                print(f"THE DISPLAY NAMES IN GET REMOTE AUTHORS ALL IS {displayNames}")
                
                for author_data in authors_data:
                    # get host from author id
                    # for example: https://cmput404-group-project.herokuapp.com/authors/1
                    # host = https://cmput404-group-project.herokuapp.com
                    host = author_data['id'].rstrip('/').split("/api/authors")[0] + "/api"
                    print(f"host: {host.strip('/api')}, node.remote_node_url: {node.remote_node_url.rstrip('/')}")
                    if author_data['id'].rstrip('/').split("/api/authors")[0] != node.remote_node_url.rstrip('/'):
                        # skip if author is not from the this node
                        continue
                    
                    # get author id
                    # - assuming the id is in the format: <host>/authors/<id>
                    author_id = author_data['id'].rstrip('/').split("/authors/")[-1]
                    print(f"author_data['id']: {author_data['id']}")
                    print(f"GET REMOTE AUTHORS AUTHOR ID {author_id}")
                    
                    
                    # get remote author
                    # - if author doesn't exist, create it
                    # - if author does exist, update it
                    if author_id:
                        author, created = Author.objects.get_or_create(id=author_id)
                        print(f"THE AUTHOR OBJECT IN GET REMOTE AUTHORS IS {author}")
                        author.url = author_data['id']
                        author.host = author_data['host']
                        author.display_name = author_data['displayName']
                        author.github = author_data.get('github', '')
                        author.profile_image = author_data.get('profileImage', '')
                        author.page = author_data['page']
                        author.save()

                        remote_authors.append(author)
            
            # if failed, try a different endpoint
            if response.status_code >= 400:
                authors_remote_endpoint = f"{node.remote_node_url.rstrip('/')}/api/authors/"
                response = requests.get(
                    authors_remote_endpoint,
                    # params={"host": host_with_scheme},
                    headers={"Authorization": f"Basic {base64_credentials}"},
                )
                
                print(f"THE AUTHOR DATA IN GET REMOTE AUTHORS IS {response.json()}")
                authors_erm = response.json()["authors"]
                print(f"THE AUTHOR DATA JUST AUTHORS IN GET REMOTE AUTHORS IS {authors_erm}")
                
                # if successful, get the authors
                if response.status_code == 200:
                    
                    authors_data = response.json()["authors"]
                    
                    for author_data in authors_data:
                        # get host from author id
                        # for example: https://cmput404-group-project.herokuapp.com/authors/1
                        # host = https://cmput404-group-project.herokuapp.com
                        host = author_data['id'].rstrip('/').split("/api/authors")[0] + "/api"
                        print(f"host: {host.strip('/api')}, node.remote_node_url: {node.remote_node_url.rstrip('/')}")
                        if author_data['id'].rstrip('/').split("/api/authors")[0] != node.remote_node_url.rstrip('/'):
                            # skip if author is not from the this node
                            continue
                        
                        # get author id
                        # - assuming the id is in the format: <host>/authors/<id>
                        author_id = author_data['id'].rstrip('/').split("/authors/")[-1]
                        print(f"author_data['id']: {author_data['id']}")
                        print(f"GET REMOTE AUTHORS AUTHOR ID {author_id}")
                        
                        
                        # get remote author
                        # - if author doesn't exist, create it
                        # - if author does exist, update it
                        if author_id:
                            author, created = Author.objects.get_or_create(id=author_id)
                            print(f"THE AUTHOR OBJECT IN GET REMOTE AUTHORS IS {author}")
                            author.url = author_data['id']
                            author.host = author_data['host']
                            author.display_name = author_data['displayName']
                            author.github = author_data.get('github', '')
                            author.profile_image = author_data.get('profileImage', '')
                            author.page = author_data['page']
                            author.save()

                            remote_authors.append(author)
                else:
                    failed_nodes_urls.append([node.remote_node_url, response.status_code])
                    continue
            
        # show failed nodes
        if failed_nodes_urls:
            print(f"Could not get remote author(s) from these nodes: {failed_nodes_urls}")
        
        print(f"Got remote authors successfully: {remote_authors}")
        return remote_authors   
    except Exception as e:
        print(f"Could not get remote authors due to error: {e}")
        raise e

def is_fqid(value):
    """
    Check if the value is an FQID (a URL) or a SERIAL (integer).
    """
    try:
        value_str = str(value)
        print (f"checking if {value} is a url")
        # Parse the value as a URL
        result = urlparse(value_str)
        print (f"result: {result}")
        print(f"result.scheme: {result.scheme}")
        print(f"result.netloc: {result.netloc}")
        return all([result.scheme, result.netloc])  # Valid URL requires scheme and netloc
    except ValueError as e:
        print(f"error: {e}")
        return False
    
def upload_to_imgur(image_data):
    """
    Upload image to imgur.
    """
    try:
        print(f"Image data: {image_data}")
        # endpoint + headers
        url = "https://api.imgur.com/3/image"
        headers = {
            "Authorization": f"Client-ID {settings.IMGUR_CLIENT_ID}",
        }
        files = {
            "image": image_data
        }
        
        # request
        response = requests.post(url, headers=headers, files=files)
        response_data = response.json()
        
        if response.status_code == 200:
            return [response_data["data"]["link"]], None
        else:
            return None, [response_data["data"].get("error", "Unknown error")]
    except Exception as e:
        return None, str(e)