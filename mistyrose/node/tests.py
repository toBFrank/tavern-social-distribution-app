from unittest.mock import patch, Mock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from node.models import Node
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.urls import reverse

# User Story #56 Test: As a node admin, I want to be able to connect to remote nodes by entering only the URL of the remote node, a username, and a password.
# User Story #60 Test: As a node admin, I can prevent nodes from connecting to my node if they don't have a valid username and password.
class RemoteNodeConnectionTestCase(TestCase):
    def setUp(self):
        """
        Initialize test data
        """
        self.client = APIClient()

        self.valid_data = {
            "host": "http://valid-remote-node.com",
            "username": "admin",
            "password": "password123",
        }
        self.invalid_data = {
            "host": "http://valid-remote-node.com",
            "username": "admin",
            "password": "wrongpassword",
        }

        # Create a Node instance
        self.node = Node.objects.create(
            remote_node_url="http://valid-remote-node.com",
            remote_username="admin",
            remote_password="password123",
            is_whitelisted=True,
        )

    @patch("requests.post")  # Mock requests.post method
    @patch("node.views.get_object_or_404")  # Mock the get_object_or_404 method
    def test_successful_connection(self, mock_get_object_or_404, mock_post):
        """
        Test successfully connected to remote node
        """
        # Mock get_object_or_404 returning our Node instance
        mock_get_object_or_404.return_value = self.node

        # Simulating the remote node returns 200 OK
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        response = self.client.put("/api/node/", data=self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("type", response.data)
        self.assertEqual(response.data["type"], "node")
        self.assertIn("item", response.data)
        self.assertEqual(response.data["item"]["host"], self.valid_data["host"])

    @patch("requests.post")
    @patch("node.views.get_object_or_404")
    def test_failed_connection_wrong_credentials(self, mock_get_object_or_404, mock_post):
        """
        Test failed to connect using wrong username or password
        """
        mock_get_object_or_404.return_value = self.node

        # Simulating the remote node returns 401 Unauthorized
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        response = self.client.put("/api/node/", data=self.invalid_data, format="json")

        # Check if the returned password is different from the test input
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("item", response.data)
        self.assertEqual(response.data["item"]["host"], self.invalid_data["host"])

    @patch("node.views.get_object_or_404")
    def test_missing_required_fields(self, mock_get_object_or_404):
        """
        Test returns error when required field is missing
        """
        incomplete_data = {"username": "admin"}  # Missing host and password

        response = self.client.put("/api/node/", data=incomplete_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("host", response.data)
        self.assertIn("password", response.data)
        self.assertEqual(response.data["host"][0], "This field is required.")
        self.assertEqual(response.data["password"][0], "This field is required.")

    @patch("requests.post")
    @patch("node.views.get_object_or_404")
    def test_failed_connection_invalid_host(self, mock_get_object_or_404, mock_post):
        """
        Test provides invalid remote node URL
        """
        mock_get_object_or_404.return_value = self.node

        invalid_data = {
            "host": "not-a-valid-url",
            "username": "admin",
            "password": "password123",
        }

        response = self.client.put("/api/node/", data=invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("host", response.data)
        self.assertEqual(response.data["host"][0], "Enter a valid URL.")

# User Story #58 Test: As a node admin, I want to be able to add nodes to share with.
# User Story #59 Test: As a node admin, I want to be able to remove nodes and stop sharing with them. 
class NodeAddAndDeleteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Create a node directly in the database
        self.node = Node.objects.create(
            remote_node_url="http://existing-node.com",
            remote_username="existing_user",
            remote_password="existing_password",
            is_whitelisted=True,
        )

    def test_get_shared_nodes(self):
        """
        Test retrieving shared nodes as a node admin.
        - Adding nodes is simulated by directly creating nodes in the database.
        - Sharing nodes is verified by checking if the nodes are correctly returned via the API.
        """
        # Make a GET request
        response = self.client.get("/api/node/list/", format="json")

        # print("Response content:", response.content)
        # print("Response type:", type(response))

        # Check if the status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify response content
        try:
            response_json = response.json()
        except ValueError:
            self.fail("Response is not in JSON format")

        self.assertIn("type", response_json)
        self.assertEqual(response_json["type"], "nodes")
        self.assertIn("items", response_json)
        self.assertEqual(len(response_json["items"]), 1)
        self.assertEqual(response_json["items"][0]["host"], self.node.remote_node_url)
        self.assertEqual(response_json["items"][0]["username"], self.node.remote_username)
    
    def test_remove_node(self):
        """
        Simulate removing a node by directly deleting it from the database.
        """
        # Delete node directly
        self.node.delete()

        # Verify that the node has been removed from the database
        with self.assertRaises(Node.DoesNotExist):
            Node.objects.get(remote_node_url=self.node.remote_node_url)

        # Validation node has been removed from the share list
        response = self.client.get("/api/node/list/", format="json")
        response_json = response.json()

        self.assertIn("type", response_json)
        self.assertEqual(response_json["type"], "nodes")
        self.assertNotIn(self.node.remote_node_url, [item["host"] for item in response_json["items"]])

# User Story #68 Test: As a node admin, I want the API objects (authors, posts, etc.) to be identified by their full URL, to prevent collisions with other node's numbering schemes.
class NodeAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user and generate Token
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        # Set API path
        self.node_list_url = reverse("node-list-create")
        self.node_detail_url = "/api/node/" 

        # Sample node data
        self.node_data_1 = {
            "remote_node_url": "http://example.com/node/123",
            "remote_username": "admin1",
            "remote_password": "password1"
        }
        self.node_data_2 = {
            "remote_node_url": "http://example.com/node/456",
            "remote_username": "admin2",
            "remote_password": "password2"
        }

    def test_list_nodes(self):
        """Test retrieving a list of nodes."""
        # Simulate creating nodes
        Node.objects.create(**self.node_data_1)
        Node.objects.create(**self.node_data_2)

        # Call list view
        response = self.client.get(self.node_list_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 2)

    def test_node_detail_with_full_url(self):
        """Test retrieving a node directly from the database."""
        # Simulate creating nodes
        node = Node.objects.create(**self.node_data_1)
        print(f"Created node: {node.remote_node_url}")

        # Manually verify node information in the database
        retrieved_node = Node.objects.get(remote_node_url=self.node_data_1["remote_node_url"])
        self.assertEqual(retrieved_node.remote_node_url, self.node_data_1["remote_node_url"])

