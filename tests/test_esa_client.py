from unittest.mock import MagicMock, patch

import pytest
import requests

from src.mcp_esa_server.esa_client import EsaClient


@pytest.fixture
def client():
    "Return an instance of EsaClient with specified token and team_name."
    return EsaClient(token="test_token", team_name="test_team")


def test_esa_client_initialization(client):
    "Test if EsaClient initializes correctly with env vars."
    assert client.token == "test_token"
    assert client.team_name == "test_team"
    assert client.base_url == f"https://api.esa.io/v1/teams/{client.team_name}"
    assert client.session.headers["Authorization"] == f"Bearer {client.token}"


def test_esa_client_initialization_missing_token():
    "Test ValueError is raised if token is missing or invalid."
    with pytest.raises(ValueError, match="ESA_TOKEN is required"):
        EsaClient(token=None, team_name="test_team")
    with pytest.raises(ValueError, match="ESA_TOKEN is required"):
        EsaClient(token="", team_name="test_team")


def test_esa_client_initialization_missing_team_name():
    "Test ValueError is raised if team_name is missing or invalid."
    with pytest.raises(ValueError, match="ESA_TEAM_NAME is required"):
        EsaClient(token="test_token", team_name=None)
    with pytest.raises(ValueError, match="ESA_TEAM_NAME is required"):
        EsaClient(token="test_token", team_name="")


@patch("src.mcp_esa_server.esa_client.requests.Session.request")
def test_get_user_success(mock_request, client):
    "Test the get_user method success case."
    # Arrange: Configure the mock response
    mock_response = MagicMock()
    expected_user_data = {"screen_name": "test_user"}
    mock_response.json.return_value = expected_user_data
    mock_response.raise_for_status.return_value = None  # Simulate successful response
    mock_request.return_value = mock_response

    # Act: Call the method under test
    user_data = client.get_user()

    # Assert: Check if the request was made correctly and data is returned
    mock_request.assert_called_once_with("GET", "https://api.esa.io/v1/user")
    assert user_data == expected_user_data


@patch("src.mcp_esa_server.esa_client.requests.Session.request")
def test_get_user_api_error(mock_request, client):
    "Test the get_user method handles API errors."
    # Arrange: Configure the mock to raise an HTTPError
    mock_request.side_effect = requests.exceptions.HTTPError("API Error")

    # Act & Assert: Check if the exception is raised
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_user()


# --- Tests for get_posts --- #


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_posts_success_no_params(mock_request, client):
    "Test get_posts success with no parameters."
    # Arrange
    expected_response = {"posts": [{"number": 1, "name": "Test Post"}]}
    mock_request.return_value = expected_response

    # Act
    posts_data = client.get_posts()

    # Assert
    mock_request.assert_called_once_with("GET", "/posts", params={})
    assert posts_data == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_posts_success_with_query(mock_request, client):
    "Test get_posts success with a search query."
    # Arrange
    expected_response = {"posts": []}
    mock_request.return_value = expected_response
    query = "test query"

    # Act
    posts_data = client.get_posts(q=query)

    # Assert
    mock_request.assert_called_once_with("GET", "/posts", params={"q": query})
    assert posts_data == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_posts_success_with_pagination(mock_request, client):
    "Test get_posts success with pagination parameters."
    # Arrange
    expected_response = {"posts": []}
    mock_request.return_value = expected_response
    page = 2
    per_page = 50

    # Act
    posts_data = client.get_posts(page=page, per_page=per_page)

    # Assert
    mock_request.assert_called_once_with("GET", "/posts", params={"page": page, "per_page": per_page})
    assert posts_data == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_posts_success_with_all_params(mock_request, client):
    "Test get_posts success with all parameters."
    # Arrange
    expected_response = {"posts": []}
    mock_request.return_value = expected_response
    query = "all params"
    page = 3
    per_page = 20

    # Act
    posts_data = client.get_posts(q=query, page=page, per_page=per_page)

    # Assert
    mock_request.assert_called_once_with("GET", "/posts", params={"q": query, "page": page, "per_page": per_page})
    assert posts_data == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_posts_api_error(mock_request, client):
    "Test get_posts handles API errors from _request."
    # Arrange
    mock_request.side_effect = requests.exceptions.HTTPError("API Error")

    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_posts()


# --- Tests for get_post --- #


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_post_success(mock_request, client):
    "Test get_post success case."
    # Arrange
    test_post_number = 123
    expected_response = {"number": test_post_number, "name": "Test Post Detail"}
    mock_request.return_value = expected_response

    # Act
    post_data = client.get_post(post_number=test_post_number)

    # Assert
    mock_request.assert_called_once_with("GET", f"/posts/{test_post_number}")
    assert post_data == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_get_post_api_error(mock_request, client):
    "Test get_post handles API errors from _request."
    # Arrange
    test_post_number = 456
    mock_request.side_effect = requests.exceptions.HTTPError("API Error")

    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError):
        client.get_post(post_number=test_post_number)


# --- Tests for create_post (method to be added to EsaClient) ---


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_create_post_success(mock_request, client):
    """Test create_post successfully creates a post and returns its data."""
    # Arrange
    post_payload = {"name": "New Post Title", "body_md": "This is the body."}
    expected_response = {"number": 999, "name": "New Post Title", "url": "https://..."}
    mock_request.return_value = expected_response

    # Act
    result = client.create_post(payload=post_payload)

    # Assert
    mock_request.assert_called_once_with("POST", "/posts", json={"post": post_payload})
    assert result == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_create_post_api_error(mock_request, client):
    """Test create_post handles API errors from _request."""
    # Arrange
    post_payload = {"name": "Error Post"}
    mock_request.side_effect = requests.exceptions.HTTPError("API Create Error")

    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError):
        client.create_post(payload=post_payload)


# --- Tests for update_post (method to be added to EsaClient) ---


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_update_post_success(mock_request, client):
    """Test update_post successfully updates a post and returns its data."""
    # Arrange
    post_number = 123
    update_payload = {"name": "Updated Post Title"}
    expected_response = {"number": post_number, "name": "Updated Post Title"}
    mock_request.return_value = expected_response

    # Act
    result = client.update_post(post_number=post_number, payload=update_payload)

    # Assert
    mock_request.assert_called_once_with("PATCH", f"/posts/{post_number}", json={"post": update_payload})
    assert result == expected_response


@patch("src.mcp_esa_server.esa_client.EsaClient._request")
def test_update_post_api_error(mock_request, client):
    """Test update_post handles API errors from _request."""
    # Arrange
    post_number = 456
    update_payload = {"name": "Error Update"}
    mock_request.side_effect = requests.exceptions.HTTPError("API Update Error")

    # Act & Assert
    with pytest.raises(requests.exceptions.HTTPError):
        client.update_post(post_number=post_number, payload=update_payload)


# --- Tests for delete_post (method to be added to EsaClient) ---


def test_delete_post_success(client):
    """Test delete_post successfully deletes a post (no return value)."""
    # Arrange
    post_number = 789
    mock_session_request = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None  # Simulate successful 204
    mock_session_request.return_value = mock_response

    with patch.object(client.session, "request", mock_session_request):
        # Act
        result = client.delete_post(post_number=post_number)

        # Assert
        mock_session_request.assert_called_once_with("DELETE", f"{client.base_url}/posts/{post_number}")
        assert result is None


def test_delete_post_api_error(client):
    """Test delete_post handles API errors from client.session.request."""
    # Arrange
    post_number = 101
    mock_session_request = MagicMock()
    mock_session_request.side_effect = requests.exceptions.HTTPError("API Delete Error")

    with patch.object(client.session, "request", mock_session_request):
        # Act & Assert
        with pytest.raises(requests.exceptions.HTTPError):
            client.delete_post(post_number=post_number)
