import logging

import requests

logger = logging.getLogger(__name__)


class EsaClient:
    def __init__(self, token: str, team_name: str):
        self.token = token
        self.team_name = team_name

        if not self.token:
            logger.error("Token is required but was not provided.")
            raise ValueError("ESA_TOKEN is required")
        if not self.team_name:
            logger.error("Team name is required but was not provided.")
            raise ValueError("ESA_TEAM_NAME is required")

        self.base_url = f"https://api.esa.io/v1/teams/{self.team_name}"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )

    def _request(self, method: str, path: str, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx/5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            # Consider more specific error handling or re-raising
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    def get_user(self):
        "Get authenticated user information."
        # User endpoint is not team-specific
        user_url = "https://api.esa.io/v1/user"
        try:
            response = self.session.request("GET", user_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for {user_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred during get_user: {e}")
            raise

    def get_posts(self, q: str | None = None, page: int | None = None, per_page: int | None = None):
        "Get a list of posts, optionally filtered by query and pagination."
        params = {}
        if q:
            params["q"] = q
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page

        return self._request("GET", "/posts", params=params)

    def get_post(self, post_number: int):
        "Get details of a specific post."
        path = f"/posts/{post_number}"
        return self._request("GET", path)

    def create_post(self, payload: dict):
        """Create a new post.

        Args:
            payload (dict): The post data. Expected to be in the format
                            `{"name": "...", "body_md": "...", ...}`.
                            This will be wrapped in `{"post": payload}` before sending.
        """
        # The API expects the payload to be nested under a "post" key.
        return self._request("POST", "/posts", json={"post": payload})

    def update_post(self, post_number: int, payload: dict):
        """Update an existing post.

        Args:
            post_number (int): The number of the post to update.
            payload (dict): The data to update. Expected to be in the format
                            `{"name": "...", "body_md": "...", ...}`.
                            This will be wrapped in `{"post": payload}` before sending.
        """
        path = f"/posts/{post_number}"
        return self._request("PATCH", path, json={"post": payload})

    def delete_post(self, post_number: int):
        """Delete a specific post.

        Args:
            post_number (int): The number of the post to delete.
        """
        path = f"/posts/{post_number}"
        # _request will raise an exception for non-2xx status codes.
        # For 204 No Content, response.json() would fail if called by _request.
        # We need to ensure _request handles 204 gracefully or make a more direct call.
        # For now, assuming _request handles it or we adjust _request later if needed.
        # If _request returns the response object directly for 204 or no content:
        response = self.session.request("DELETE", f"{self.base_url}{path}")
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx/5xx)
        # No specific content to return for a successful DELETE (204 No Content)
        return None


# Example usage (optional, for testing during development)
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()
    logging.basicConfig(level=logging.INFO)
    try:
        client = EsaClient(os.getenv("ESA_TOKEN"), os.getenv("ESA_TEAM_NAME"))
        logger.info(f"EsaClient initialized for team: {client.team_name}")
    except ValueError as e:
        logger.error(f"Initialization failed: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
