from urllib.parse import urlparse
import requests
import base64

from users.models import Author
from node.models import Node
from users.models import Follows


def get_remote_authors(request):
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
        
        print("Got remote authors successfully")
        return remote_authors   
    except Exception as e:
        print("Could not get remote authors")
        raise e
        

def get_remote_friends(author):
    """
    Get remote friends of an author.
    """
    try:
        # Set of remote authors that the given author is following (URLs)
        remote_following_urls = set(
            Follows.objects.filter(
                remote_follower_url=author.url, status='ACCEPTED', is_remote=True
            ).values_list('followed_id__url', flat=True)  # Get URLs of followed authors
        )
        
        # Set of remote authors that are following the given author (URLs)
        remote_followers_urls = set(
            Follows.objects.filter(
                followed_id=author, status='ACCEPTED', is_remote=True
            ).values_list('remote_follower_url', flat=True)  # Get remote follower URLs
        )
        return remote_following_urls.intersection(remote_followers_urls)
    
        print("Got remote friends successfully")
    except Exception as e:
        print(f"Could not get remote friends for author {author.url}")
        raise Exception(f"Could not get remote friends for author {author.url}: {e}")

def post_to_remote_inboxes(request, remote_authors, post_data):
    """
    Post data to the inboxes of remote authors.
    """
    
    failed_authors_urls = []
    
    try:
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
        
        print("Posted to remote author inboxes successfully")
        
        # show failed authors
        if failed_authors_urls:
            print(f"Could not post to these remote author inboxes: {failed_authors_urls}")
    except Exception as e:
        print("Could not post to remote author inboxes")
        raise Exception(f"Could not post to remote author inboxes: {e}")