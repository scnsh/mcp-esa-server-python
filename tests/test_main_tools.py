from unittest.mock import MagicMock, patch

import pytest

from src.mcp_esa_server.server import (
    posts_create,
    posts_delete,
    posts_get_detail,
    posts_get_list,
    posts_update,
    user_get_info,
)


# Fixture to mock esa_client in main.py
@pytest.fixture
def mock_esa_client_in_main():
    # Patch 'main.esa_client' which is used by the MCP tools
    with patch("src.mcp_esa_server.server.esa_client", new_callable=MagicMock) as mock_client:
        yield mock_client


# Fixture to mock a non-initialized esa_client in main.py
@pytest.fixture
def mock_esa_client_none_in_main():
    with patch("src.mcp_esa_server.server.esa_client", None) as mock_client_none:
        yield mock_client_none


def test_user_get_info_success(mock_esa_client_in_main):
    """Test user_get_info MCP tool successfully returns user data."""
    # Arrange
    expected_user_data = {"id": 1, "screen_name": "test_user_tool"}
    mock_esa_client_in_main.get_user.return_value = expected_user_data

    # Act
    result = user_get_info()

    # Assert
    assert result == expected_user_data
    mock_esa_client_in_main.get_user.assert_called_once()


def test_user_get_info_client_not_initialized(mock_esa_client_none_in_main):
    """Test user_get_info MCP tool raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        user_get_info()


def test_user_get_info_client_raises_exception(mock_esa_client_in_main):
    """Test user_get_info MCP tool raises RuntimeError if esa_client.get_user() fails."""
    # Arrange
    mock_esa_client_in_main.get_user.side_effect = Exception("Tool API Error")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error getting user info: Tool API Error"):
        user_get_info()


def test_posts_get_list_success_no_params(mock_esa_client_in_main):
    """Test posts_get_list MCP tool successfully returns data with no params."""
    # Arrange
    expected_posts_data = {"posts": [{"id": 10, "name": "Tool Test Post"}]}
    mock_esa_client_in_main.get_posts.return_value = expected_posts_data

    # Act
    result = posts_get_list()

    # Assert
    assert result == expected_posts_data
    mock_esa_client_in_main.get_posts.assert_called_once_with()


def test_posts_get_list_success_with_params(mock_esa_client_in_main):
    """Test posts_get_list MCP tool successfully returns data with query and pagination."""
    # Arrange
    expected_posts_data = {"posts": []}
    mock_esa_client_in_main.get_posts.return_value = expected_posts_data
    query = "tool test query"
    page = 20
    per_page = 100

    # Act
    result = posts_get_list(q=query, page=page, per_page=per_page)

    # Assert
    assert result == expected_posts_data
    mock_esa_client_in_main.get_posts.assert_called_once_with(q=query, page=page, per_page=per_page)


def test_posts_get_list_client_not_initialized(mock_esa_client_none_in_main):
    """Test posts_get_list MCP tool raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        posts_get_list()


def test_posts_get_list_client_raises_exception(mock_esa_client_in_main):
    """Test posts_get_list MCP tool raises RuntimeError if esa_client.get_posts() fails."""
    # Arrange
    mock_esa_client_in_main.get_posts.side_effect = Exception("Tool API Error Posts")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error getting posts list: Tool API Error Posts"):
        posts_get_list(q="tool_test")


def test_posts_get_detail_success(mock_esa_client_in_main):
    """Test posts_get_detail MCP tool successfully returns data for a post."""
    # Arrange
    post_number = 1230
    expected_post_data = {"number": post_number, "name": "Specific Tool Post"}
    mock_esa_client_in_main.get_post.return_value = expected_post_data

    # Act
    result = posts_get_detail(post_number=post_number)

    # Assert
    assert result == expected_post_data
    mock_esa_client_in_main.get_post.assert_called_once_with(post_number)


def test_posts_get_detail_client_not_initialized(mock_esa_client_none_in_main):
    """Test posts_get_detail MCP tool raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        posts_get_detail(post_number=1230)


def test_posts_get_detail_client_raises_exception(mock_esa_client_in_main):
    """Test posts_get_detail MCP tool raises RuntimeError if esa_client.get_post() fails."""
    # Arrange
    post_number = 4560
    mock_esa_client_in_main.get_post.side_effect = Exception("Tool API Error Detail")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error getting post detail: Tool API Error Detail"):
        posts_get_detail(post_number=post_number)


def test_posts_create_success(mock_esa_client_in_main):
    """Test posts_create successfully calls esa_client.create_post and returns data."""
    # Arrange
    name = "Test Post via MCP"
    body_md = "This is a test."
    tags = ["mcp", "test"]
    category = "mcp_tests"
    wip = False
    message = "Test commit message"

    expected_payload_to_esa_client = {
        "name": name,
        "body_md": body_md,
        "tags": tags,
        "category": category,
        "wip": wip,
        "message": message,
    }
    filtered_payload = {k: v for k, v in expected_payload_to_esa_client.items() if v is not None}

    expected_response_from_tool = {
        "url": "https://example.esa.io/posts/123",
        "name": name,
    }
    mock_esa_client_in_main.create_post.return_value = expected_response_from_tool

    # Act
    result = posts_create(
        name=name,
        body_md=body_md,
        tags=tags,
        category=category,
        wip=wip,
        message=message,
    )

    # Assert
    assert result == expected_response_from_tool
    mock_esa_client_in_main.create_post.assert_called_once_with(payload=filtered_payload)


def test_posts_create_success_minimal_params(mock_esa_client_in_main):
    """Test posts_create with minimal parameters (name, body_md)."""
    # Arrange
    name = "Minimal Test Post"
    body_md = "Minimal body."
    expected_payload_to_esa_client = {
        "name": name,
        "body_md": body_md,
        "tags": [],
        "category": "",
        "wip": True,
        "message": "",
    }
    filtered_payload = {k: v for k, v in expected_payload_to_esa_client.items() if v is not None}

    expected_response_from_tool = {
        "url": "https://example.esa.io/posts/124",
        "name": name,
    }
    mock_esa_client_in_main.create_post.return_value = expected_response_from_tool

    # Act
    result = posts_create(name=name, body_md=body_md)

    # Assert
    assert result == expected_response_from_tool
    mock_esa_client_in_main.create_post.assert_called_once_with(payload=filtered_payload)


def test_posts_create_client_not_initialized(mock_esa_client_none_in_main):
    """Test posts_create raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        posts_create(name="Test", body_md="Test")


def test_posts_create_client_raises_exception(mock_esa_client_in_main):
    """Test posts_create raises RuntimeError if esa_client.create_post() fails."""
    # Arrange
    mock_esa_client_in_main.create_post.side_effect = Exception("Create API Error")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error creating post: Create API Error"):
        posts_create(name="Test", body_md="Test")


def test_posts_update_success(mock_esa_client_in_main):
    """Test posts_update successfully calls esa_client.update_post with all params."""
    # Arrange
    post_number = 123
    name = "Updated Title"
    body_md = "Updated body."
    tags = ["updated", "test"]
    category = "updated/category"
    wip = False
    message = "Update commit message"

    expected_payload_to_esa_client = {
        "name": name,
        "body_md": body_md,
        "tags": tags,
        "category": category,
        "wip": wip,
        "message": message,
    }
    filtered_payload = {k: v for k, v in expected_payload_to_esa_client.items() if v is not None}

    expected_response_from_tool = {
        "url": f"https://example.esa.io/posts/{post_number}",
        "name": name,
    }
    mock_esa_client_in_main.update_post.return_value = expected_response_from_tool

    # Act
    result = posts_update(
        post_number=post_number,
        name=name,
        body_md=body_md,
        tags=tags,
        category=category,
        wip=wip,
        message=message,
    )

    # Assert
    assert result == expected_response_from_tool
    mock_esa_client_in_main.update_post.assert_called_once_with(post_number=post_number, payload=filtered_payload)


def test_posts_update_success_partial_params(mock_esa_client_in_main):
    """Test posts_update successfully calls esa_client.update_post with partial params."""
    # Arrange
    post_number = 456
    name = "Partially Updated Title"
    expected_payload_to_esa_client = {
        "name": name,
    }
    filtered_payload = {k: v for k, v in expected_payload_to_esa_client.items() if v is not None}
    expected_response_from_tool = {
        "url": f"https://example.esa.io/posts/{post_number}",
        "name": name,
    }
    mock_esa_client_in_main.update_post.return_value = expected_response_from_tool

    # Act
    result = posts_update(post_number=post_number, name=name)

    # Assert
    assert result == expected_response_from_tool
    mock_esa_client_in_main.update_post.assert_called_once_with(post_number=post_number, payload=filtered_payload)


def test_posts_update_no_params_provided(mock_esa_client_in_main, caplog):
    """Test posts_update returns specific message when no update params are given."""
    # Arrange
    post_number = 789
    expected_message = {"message": f"No update parameters provided for post {post_number}. Nothing changed."}

    # Act
    result = posts_update(post_number=post_number)

    # Assert
    assert result == expected_message
    mock_esa_client_in_main.update_post.assert_not_called()  # Ensure esa_client.update_post was not called
    assert f"No update parameters provided for post {post_number}." in caplog.text


def test_posts_update_client_not_initialized(mock_esa_client_none_in_main):
    """Test posts_update raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        posts_update(post_number=1, name="Test")


def test_posts_update_client_raises_exception(mock_esa_client_in_main):
    """Test posts_update raises RuntimeError if esa_client.update_post() fails."""
    # Arrange
    post_number = 101112
    mock_esa_client_in_main.update_post.side_effect = Exception("Update API Error")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error updating post: Update API Error"):
        posts_update(post_number=post_number, name="Test Update Fail")


def test_posts_delete_success(mock_esa_client_in_main):
    """Test posts_delete successfully calls esa_client.delete_post and returns empty dict."""
    # Arrange
    post_number = 987
    # esa_client.delete_post should return None or raise an exception on failure
    mock_esa_client_in_main.delete_post.return_value = None
    expected_response = {}

    # Act
    result = posts_delete(post_number=post_number)

    # Assert
    assert result == expected_response
    mock_esa_client_in_main.delete_post.assert_called_once_with(post_number)


def test_posts_delete_client_not_initialized(mock_esa_client_none_in_main):
    """Test posts_delete raises RuntimeError if esa_client is None."""
    # Act & Assert
    with pytest.raises(RuntimeError, match="EsaClient not initialized"):
        posts_delete(post_number=1)


def test_posts_delete_client_raises_exception(mock_esa_client_in_main):
    """Test posts_delete raises RuntimeError if esa_client.delete_post() fails."""
    # Arrange
    post_number = 654
    mock_esa_client_in_main.delete_post.side_effect = Exception("Delete API Error")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Error deleting post: Delete API Error"):
        posts_delete(post_number=post_number)
