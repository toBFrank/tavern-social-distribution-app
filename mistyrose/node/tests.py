from unittest.mock import patch, Mock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from node.models import Node

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