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
                # params={"host": host_with_scheme},
                headers={"Authorization": f"Basic {base64_credentials}"},
            )
            
            # if successful, get the authors
            if response.status_code == 200:
                authors_data = response.json()["authors"]
                for author_data in authors_data:
                    # get host from author id
                    # for example: https://cmput404-group-project.herokuapp.com/authors/1
                    # host = https://cmput404-group-project.herokuapp.com
                    host = author_data['id'].rstrip('/').split("/api/authors")[0]
                    print(f"host: {host}, node.remote_node_url: {node.remote_node_url.rstrip('/')}")
                    if host != node.remote_node_url.rstrip('/'):
                        # skip if author is not from the this node
                        continue
                    
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
        
        print(f"Got remote authors successfully: {remote_authors}")
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
        remote_following_ids = set(
            Follows.objects.filter(
                remote_follower_url=author.url, status='ACCEPTED', is_remote=True #maybe include local follower as well? some items in db don't have remote_follower_url...
            ).values_list('followed_id', flat=True)  # Get URLs of followed authors
        )

        print(f"AUTHOR IS FOLLOWING THESE REMOTE PPL: {remote_following_ids}")
        
        # Set of remote authors that are following the given author (URLs)
        remote_followers_ids = set(
            Follows.objects.filter(
                followed_id=author, status='ACCEPTED' #remove is_remote or set it because its not set .... for Sapan following Kelly
            ).values_list('local_follower_id', flat=True)  # Get remote follower URLs
        )

        print(f"REMOTE AUTHORS FOLLOWING AUTHOR: {remote_followers_ids}")

        intersection = remote_following_ids.intersection(remote_followers_ids)
        print(f"SEND TO FRIENDS: {intersection}")

        friend_authors = []
        for author_id in intersection:
            author_obj = Author.objects.filter(id=author_id).first()
            if author_obj:
                friend_authors.append(author_obj)
            else:
                print(f"Warning: Author with URL {author_id} not found in the database.")
        
            
        #should be returning authors instead of urls...
        return friend_authors
    
    except Exception as e:
        print(f"Could not get remote friends for author {author.url}: {e}")
        raise Exception(f"Could not get remote friends for author {author.url}: {e}")

def post_to_remote_inboxes(request, remote_authors, post_data):
    """
    Post data to the inboxes of remote authors.
    """
    
    failed_authors_urls = []
    
    try:
        for remote_author in remote_authors:
            node = Node.objects.filter(remote_node_url=remote_author.host.rstrip('/')).first()
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
                    # params={"host": host_with_scheme},
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
    
def get_remote_followers_you(author):
    """
    Get remote authors who follow the given author.
    """
    try:
        # Get remote authors who are following the given author
        remote_followers_ids = set(
            Follows.objects.filter(
                followed_id=author, 
                status='ACCEPTED', 
                is_remote=True  # Ensure we only consider remote followers
            ).values_list('local_follower_id', flat=True)  # Get remote follower URLs
        )

        print(f"REMOTE AUTHORS FOLLOWING AUTHOR {author.id}: {remote_followers_ids}")

        # Convert the IDs into `Author` objects
        remote_followers = []
        for author_id in remote_followers_ids:
            author_obj = Author.objects.filter(id=author_id).first()
            if author_obj:
                remote_followers.append(author_obj)
            else:
                print(f"Warning: Author with ID {author_id} not found in the database.")
        
        return remote_followers

    except Exception as e:
        print(f"Error retrieving remote followers for author {author.url}: {e}")
        raise Exception(f"Could not get remote followers for author {author.url}: {e}")
