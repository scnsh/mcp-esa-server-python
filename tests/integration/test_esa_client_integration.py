import os
import random
import time

import pytest
import requests
from dotenv import load_dotenv

from esa_client import EsaClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(scope="module")
def integration_client():
    token = os.getenv("ESA_TOKEN")
    team_name = os.getenv("ESA_TEAM_NAME")
    if not token or not team_name:
        pytest.skip("ESA_TOKEN or ESA_TEAM_NAME not set for integration tests. Skipping integration tests.")
    try:
        client = EsaClient(token=token, team_name=team_name)
        return client
    except ValueError as e:
        pytest.fail(f"Failed to initialize EsaClient for integration tests: {e}. Is .env configured correctly?")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred during EsaClient initialization for integration tests: {e}")


# Note: These tests require a valid .env file with ESA_TOKEN and ESA_TEAM_NAME
# and will make actual API calls to esa.io.
# They might be skipped by default unless explicitly run.


@pytest.mark.integration
def test_get_user_integration(integration_client):
    "Test get_user against the actual esa.io API."
    client = integration_client
    try:
        print(f"\nRunning get_user_integration test for team: {client.team_name}")
        user_data = client.get_user()
        print(f"Received user data: {user_data}")

        # Basic assertions on the structure of the response
        assert isinstance(user_data, dict)
        assert "screen_name" in user_data
        assert "email" in user_data
        print("Integration test passed.")

    except requests.exceptions.RequestException as e:
        pytest.fail(f"Integration test API call failed: {e}")
    except Exception as e:
        pytest.fail(f"Integration test unexpected error: {e}")


@pytest.mark.integration
def test_get_posts_integration(integration_client):
    "Test get_posts against the actual esa.io API (no params)."
    client = integration_client
    try:
        print(f"\nRunning get_posts integration test for team: {client.team_name}")
        posts_data = client.get_posts()
        posts_list = posts_data.get("posts", [])
        print(f"Received {len(posts_list)} posts.")

        # Print title of a random post if available
        if posts_list:
            random_post = random.choice(posts_list)
            print(f"Random post title: {random_post.get('name', 'N/A')}")
        else:
            print("No posts found to display a random title.")

        # Basic assertions on the structure
        assert isinstance(posts_data, dict)
        assert "posts" in posts_data
        assert isinstance(posts_data["posts"], list)

        # Optionally, check structure of the first post if it exists
        if posts_data["posts"]:
            assert isinstance(posts_data["posts"][0], dict)
            assert "number" in posts_data["posts"][0]
            assert "name" in posts_data["posts"][0]

        print("get_posts integration test passed.")

    except ValueError as e:
        pytest.fail(f"Integration test setup failed: {e}. Is .env configured correctly?")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Integration test API call failed: {e}")
    except Exception as e:
        pytest.fail(f"Integration test unexpected error: {e}")


@pytest.mark.integration
def test_get_posts_pagination_integration(integration_client):
    "Test get_posts pagination against the actual esa.io API."
    client = integration_client
    test_page = 2
    test_per_page = 5
    try:
        print(f"\nRunning get_posts pagination integration test (page={test_page}, per_page={test_per_page})")
        posts_data = client.get_posts(page=test_page, per_page=test_per_page)
        posts_list = posts_data.get("posts", [])
        received_count = len(posts_list)
        print(f"Received {received_count} posts.")
        print(
            f"Response metadata: page={posts_data.get('page')}, "
            f"per_page={posts_data.get('per_page')}, "
            f"total_count={posts_data.get('total_count')}"
        )

        # Assertions on response structure and metadata
        assert isinstance(posts_data, dict)
        assert "posts" in posts_data
        assert isinstance(posts_list, list)
        assert posts_data.get("page") == test_page
        assert posts_data.get("per_page") == test_per_page
        # Check received count vs per_page, considering the last page case
        total_count = posts_data.get("total_count")
        if total_count is not None and total_count > (test_page - 1) * test_per_page:
            assert received_count <= test_per_page
            if total_count >= test_page * test_per_page:
                assert received_count == test_per_page  # Should receive full page if not last
        else:
            assert received_count == 0  # Should receive 0 if page is beyond total count

        print("get_posts pagination integration test passed.")

    except ValueError as e:
        pytest.fail(f"Integration test setup failed: {e}. Is .env configured correctly?")
    except requests.exceptions.RequestException as e:
        pytest.fail(f"Integration test API call failed: {e}")
    except Exception as e:
        pytest.fail(f"Integration test unexpected error: {e}")


@pytest.mark.integration
def test_get_post_integration(integration_client):
    "Test get_post against the actual esa.io API (existing post)."
    client = integration_client
    # Note: Assumes post number 1 exists in the test team.
    # Adjust post_number if necessary for your test environment.
    test_post_number = 1
    try:
        print(f"\nRunning get_post integration test for post #{test_post_number}")
        post_data = client.get_post(post_number=test_post_number)
        print(f"Received post title: {post_data.get('name')}")

        # Assertions on response structure and content
        assert isinstance(post_data, dict)
        assert post_data.get("number") == test_post_number
        assert "name" in post_data
        assert "body_md" in post_data

        print("get_post integration test passed.")

    except ValueError as e:
        pytest.fail(f"Integration test setup failed: {e}. Is .env configured correctly?")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            pytest.fail(f"Post #{test_post_number} not found. Please use an existing post number for the test.")
        else:
            pytest.fail(f"Integration test API call failed: {e}")
    except Exception as e:
        pytest.fail(f"Integration test unexpected error: {e}")


@pytest.mark.integration
def test_get_post_not_found_integration(integration_client):
    "Test get_post against the actual esa.io API (non-existent post)."
    client = integration_client
    # Use a post number that is guaranteed not to exist (e.g., 0 or a very large number)
    test_post_number = 0
    try:
        print(f"\nRunning get_post integration test for non-existent post #{test_post_number}")
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            client.get_post(post_number=test_post_number)

        # Assert that the error is a 404 Not Found
        assert exc_info.value.response.status_code == 404
        print("get_post 404 integration test passed.")

    except ValueError as e:
        pytest.fail(f"Integration test setup failed: {e}. Is .env configured correctly?")
    except requests.exceptions.RequestException as e:
        # If it's not an HTTPError or not 404, it's an unexpected failure
        if not isinstance(e, requests.exceptions.HTTPError) or e.response.status_code != 404:
            pytest.fail(f"Integration test API call failed unexpectedly: {e}")
        # If it IS a 404 HTTPError, the test should have passed inside the 'with' block.
        # This part should ideally not be reached if the exception is caught correctly.
    except Exception as e:
        pytest.fail(f"Integration test unexpected error: {e}")


@pytest.mark.integration
def test_create_post_integration(integration_client):
    """Test create_post and verify the created post."""
    client = integration_client
    unique_name = f"Test Post - {int(time.time())}"
    post_payload = {
        "name": unique_name,
        "body_md": "This post is created to be verified by an integration test.",
        "tags": ["test", "integration"],
        "category": "integration_tests/created",
        "wip": True,
    }

    created_post_data = None
    try:
        # 1. Create a post
        created_post_data = client.create_post(payload=post_payload)
        assert created_post_data is not None
        assert "number" in created_post_data
        post_number = created_post_data["number"]
        print(f"Successfully created post for verification test: #{post_number} - {created_post_data.get('url')}")

        # 2. Verify the post is created (attempting to get it should result in 200)
        get_post_data = client.get_post(post_number=post_number)
        assert get_post_data is not None
        assert get_post_data.get("number") == post_number
        assert get_post_data.get("name") == unique_name
        print(f"Verified post #{post_number} exists and matches the created post.")

    except Exception as e:
        if created_post_data and created_post_data.get("number"):
            post_number_to_clean = created_post_data["number"]
            try:
                print(
                    f"Test failed, attempting to clean up post #{post_number_to_clean} "
                    f"from test_create_post_integration."
                )
                client.delete_post(post_number_to_clean)
                print(f"Cleaned up post #{post_number_to_clean} after test failure.")
            except Exception as cleanup_e:
                print(f"Failed to clean up post #{post_number_to_clean} after test failure: {cleanup_e}")
        raise e
    finally:
        if created_post_data and created_post_data.get("number"):
            post_number_to_delete = created_post_data["number"]
            try:
                print(f"Attempting to clean up post #{post_number_to_delete} created by test_create_post_integration.")
                client.delete_post(post_number_to_delete)
                print(f"Successfully cleaned up post #{post_number_to_delete}.")
            except requests.exceptions.HTTPError as e:
                print(
                    f"Failed to clean up post #{post_number_to_delete} "
                    f"during test_create_post_integration: {e}. "
                    f"It might have been already deleted."
                )
            except Exception as e:
                print(f"An unexpected error occurred during cleanup of post #{post_number_to_delete}: {e}")
        pass


@pytest.mark.integration
def test_delete_post_integration(integration_client):
    """Test create_post, then delete_post, and verify deletion."""
    client = integration_client
    unique_name = f"Test Post for Deletion - {int(time.time())}"
    post_payload = {
        "name": unique_name,
        "body_md": "This post is created to be deleted by an integration test.",
        "tags": ["test", "delete"],
        "category": "integration_tests/to_be_deleted",
        "wip": True,
    }

    created_post_data = None
    try:
        created_post_data = client.create_post(payload=post_payload)
        assert created_post_data is not None
        assert "number" in created_post_data
        post_number = created_post_data["number"]
        print(f"Successfully created post for deletion test: #{post_number} - {created_post_data.get('url')}")

        client.delete_post(post_number)
        print(f"Successfully called delete_post for #{post_number}")

        with pytest.raises(requests.exceptions.HTTPError) as excinfo:
            client.get_post(post_number)
        assert excinfo.value.response.status_code == 404
        print(f"Verified post #{post_number} is no longer accessible (404 received).")

    except Exception as e:
        if created_post_data and created_post_data.get("number"):
            post_number_to_clean = created_post_data["number"]
            try:
                print(
                    f"Test failed, attempting to clean up post #{post_number_to_clean} "
                    f"from test_delete_post_integration."
                )
                client.delete_post(post_number_to_clean)
                print(f"Cleaned up post #{post_number_to_clean} after test failure.")
            except Exception as cleanup_e:
                print(f"Failed to clean up post #{post_number_to_clean} after test failure: {cleanup_e}")
        raise e


@pytest.mark.integration
def test_delete_post_non_existent_integration(integration_client):
    """Test delete_post with a non-existent post_number."""
    client = integration_client
    non_existent_post_number = 0
    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        client.delete_post(non_existent_post_number)
    assert excinfo.value.response.status_code == 404
    print(f"Verified deleting non-existent post #{non_existent_post_number} results in 404.")


@pytest.mark.integration
def test_update_post_integration(integration_client):
    """Test creating, updating, and verifying a post."""
    client = integration_client
    original_name = f"Original Post Title - {int(time.time())}"
    updated_name = f"Updated Post Title - {int(time.time())}"
    post_payload = {
        "name": original_name,
        "body_md": "This is the original body of the post.",
        "tags": ["original", "test"],
        "category": "integration_tests/original_category",
        "wip": True,
    }

    created_post_data = None
    try:
        # 1. Create an initial post
        created_post_data = client.create_post(payload=post_payload)
        assert created_post_data is not None
        post_number = created_post_data["number"]
        print(f"Successfully created post #{post_number} for update test: {created_post_data.get('url')}")

        # 2. Update the post
        update_payload = {
            "name": updated_name,
            "body_md": "This is the updated body.",
            "tags": ["updated", "test", "integration"],
            "category": "integration_tests/updated_category",
            "wip": False,  # Change WIP status as well
            "message": "Updating post via integration test",
        }
        updated_post_data = client.update_post(post_number, payload=update_payload)
        assert updated_post_data is not None
        assert updated_post_data["number"] == post_number
        assert updated_post_data["name"] == updated_name
        assert updated_post_data["wip"] is False  # Verify WIP status change
        print(f"Successfully updated post #{post_number}. New URL: {updated_post_data.get('url')}")

        # 3. Verify the updated post by fetching it again
        fetched_post_data = client.get_post(post_number)
        assert fetched_post_data["name"] == updated_name
        assert fetched_post_data["body_md"] == update_payload["body_md"]
        assert sorted(fetched_post_data["tags"]) == sorted(update_payload["tags"])
        assert fetched_post_data["category"] == update_payload["category"]
        assert fetched_post_data["wip"] == update_payload["wip"]
        print(f"Successfully verified updated content for post #{post_number}.")

    finally:
        # Cleanup: Delete the post if it was created
        if created_post_data and created_post_data.get("number"):
            post_number_to_delete = created_post_data["number"]
            try:
                print(f"Attempting to clean up post #{post_number_to_delete} from test_update_post_integration.")
                client.delete_post(post_number_to_delete)
                print(f"Successfully cleaned up post #{post_number_to_delete}.")
            except Exception as e:
                print(f"Failed to clean up post #{post_number_to_delete} during test_update_post_integration: {e}")


@pytest.mark.integration
def test_update_post_not_found_integration(integration_client):
    """Test updating a non-existent post."""
    client = integration_client
    non_existent_post_number = 0  # A post number that is guaranteed not to exist
    update_payload = {"name": "Attempt to update non-existent post", "body_md": "This should not succeed."}

    with pytest.raises(requests.exceptions.HTTPError) as excinfo:
        client.update_post(non_existent_post_number, payload=update_payload)

    assert excinfo.value.response.status_code == 404
    print(f"Verified updating non-existent post #{non_existent_post_number} results in 404.")


@pytest.mark.integration
def test_create_post_with_all_fields_integration(integration_client):
    """Test create_post with all optional fields and verify them."""
    client = integration_client
    unique_suffix = int(time.time())
    post_name = f"Test All Fields - {unique_suffix}"
    post_body = f"Body for all fields test created at {unique_suffix}."
    post_tags = [f"tag1-{unique_suffix}", f"tag2-{unique_suffix}", "all-fields-test"]
    post_category = f"integration_tests/all_fields_test_category/{unique_suffix}"
    post_wip = False  # Test with a specific WIP status
    post_message = f"Commit message for all fields test - {unique_suffix}"

    post_payload = {
        "name": post_name,
        "body_md": post_body,
        "tags": post_tags,
        "category": post_category,
        "wip": post_wip,
        "message": post_message,
    }

    created_post_data = None
    try:
        # 1. Create a post with all specified fields
        created_post_data = client.create_post(payload=post_payload)
        assert created_post_data is not None
        post_number = created_post_data["number"]
        print(f"Successfully created post #{post_number} for all_fields test: {created_post_data.get('url')}")

        # 2. Assertions on the creation response (fields that are usually in create response)
        assert created_post_data.get("name") == post_name
        # Tags might be empty in create response if not processed immediately, check fetched one later.
        # Category might be different if it's a new category path, check fetched one.
        assert created_post_data.get("wip") == post_wip
        assert created_post_data.get("message") == post_message

        # 3. Verify the post by fetching it to check all fields accurately
        fetched_post_data = client.get_post(post_number=post_number)
        assert fetched_post_data is not None
        assert fetched_post_data.get("number") == post_number
        assert fetched_post_data.get("name") == post_name
        assert fetched_post_data.get("body_md") == post_body
        assert sorted(fetched_post_data.get("tags", [])) == sorted(post_tags)
        assert fetched_post_data.get("category") == post_category
        assert fetched_post_data.get("wip") == post_wip
        # The commit message is part of the revision, not directly on the fetched post data usually.
        # The check on created_post_data['message'] is the primary one for the commit message.
        print(f"Successfully verified created post #{post_number} with all fields.")

    finally:
        # Cleanup: Delete the post if it was created
        if created_post_data and created_post_data.get("number"):
            post_number_to_delete = created_post_data["number"]
            try:
                print(
                    f"Attempting to clean up post #{post_number_to_delete} from "
                    f"test_create_post_with_all_fields_integration."
                )
                client.delete_post(post_number_to_delete)
                print(f"Successfully cleaned up post #{post_number_to_delete}.")
            except Exception as e:
                print(
                    f"Failed to clean up post #{post_number_to_delete} during "
                    f"test_create_post_with_all_fields_integration: {e}"
                )
