import requests
from requests.auth import HTTPBasicAuth
from node.models import Node
from .views import get_remote_authors  

def notifyOtherNodes(request, post):
    try:
        remote_authors = get_remote_authors(request)
        print(f"Remote authors????? {remote_authors}")
    except Exception as e:
        print(f"Error updating remote authors: {str(e)}")
        return

    # Get all the connected nodes
    nodes = Node.objects.filter(is_whitelisted=True, is_authenticated=True)
    print("Notification function reached.")
    print("test nodes: ", nodes) # todo: delete test comments laterrrr!!!!!!

    if not nodes.exists():
        print("No nodes connected.")
        return  

    # Iterate over each node and send the post to their inbox
    for node in nodes:
        # Approach 1: response??? => Check if post is already updated with new content!!!!
        # response = requests.post(
        # author_inbox_url,
        # params={"host": host_with_scheme},
        # # auth=HTTPBasicAuth(local_node_of_remote.username, local_node_of_remote.password),
        # headers={"Authorization": f"Basic {base64_credentials}"},
        # json=post_data,
        #     )

        # print(f"Response Status Code: {response.status_code}")

        # Approach 2: make new post and then response???
        try:
            url = f"{node.host}/api/authors/{post.author_id.id}/inbox/"
            data = {
                "type": "post",
                "title": post.title,
                "content": post.content,
                "author": {
                    "id": str(post.author_id.id),
                    "displayName": post.author_id.display_name,
                },
                "published": post.published.isoformat(),
                "visibility": post.visibility,
            }
            # Send the request to the node's inbox
            response = requests.post(
                url,
                json=data,
                auth=HTTPBasicAuth(node.username, node.password)
            )
            if response.status_code == 200:
                print(f"Post sent to {node.name} successfully.")
            else:
                print(f"Failed to send post to {node.name}: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending post to {node.name}: {str(e)}")
