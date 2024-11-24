from unittest.mock import patch, Mock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from node.models import Node
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

# User Story #56 Test: As a node admin, I want to be able to connect to remote nodes by entering only the URL of the remote node, a username, and a password.
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
class NodeAddingTestCase(TestCase):
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
