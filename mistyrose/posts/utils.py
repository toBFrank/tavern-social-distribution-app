from urllib.parse import urlparse
import requests
import base64

from .models import Author
from node.models import Node


def get_remote_authors(request):
    """
    Get authors from remote nodes and save them to the local database.
    """
  
    remote_authors = []
    failed_nodes_urls = []
    
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
            params={"host": host_with_scheme},
            headers={"Authorization": f"Basic {base64_credentials}"},
        )
        
        # if successful, get the authors
        if response.status_code == 200:
            authors_data = response.json()["authors"]
            for author_data in authors_data:
                # get author id
                # - assuming the id is in the format: <host>/authors/<id>
                author_id = author_data['id'].rstrip('/').split("/authors/")[-1]
                
                # get remote author
                # - if author doesn't exist, create it
                # - if author does exist, update it
                if author_id:
                    author, created = Author.objects.get_or_create(id=author_id)
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
        
    # show failed nodes
    if failed_nodes_urls:
        print(f"Could not get remote author(s) from these nodes: {failed_nodes_urls}")
        
    return remote_authors

def post_to_remote_inboxes(request, remote_authors, post_data):
    """
    Post data to the inboxes of remote authors.
    """
    
    failed_authors_urls = []
    
    for remote_author in remote_authors:
        node = Node.objects.filter(host=remote_author.host.rstrip('/')).first()
        if node:
          author_inbox_remote_endpoint = f"{remote_author.url.rstrip('/')}/inbox/"
          
          # my local node's host with scheme
          parsed_url = urlparse(request.build_absolute_uri())
          host_with_scheme = f"{parsed_url.scheme}://{parsed_url.netloc}"
          
          # credentials to access remote node (encoded in base64)
          credentials = f"{node.remote_username}:{node.remote_password}"
          base64_credentials = base64.b64encode(credentials.encode()).decode("utf-8")
          
          # make the request
          response = requests.post(
              author_inbox_remote_endpoint,
              params={"host": host_with_scheme},
              headers={"Authorization": f"Basic {base64_credentials}"},
              json=post_data,
          )
          
          # check for errors
          if response.status_code != 200 and response.status_code != 201:
              failed_authors_urls.append([remote_author.url, response.status_code])
          
    # show failed authors
    if failed_authors_urls:
        print(f"Could not post to these remote author inboxes: {failed_authors_urls}")     