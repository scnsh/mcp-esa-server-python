import logging
import os
import sys
from typing import Annotated, Any

from dotenv import load_dotenv
from .esa_client import EsaClient
from mcp.server.fastmcp import FastMCP
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

# Setup logging using standard library
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
esa_token = os.getenv("ESA_TOKEN")
esa_team_name = os.getenv("ESA_TEAM_NAME")

logger.debug("Attempting to initialize EsaClient.")
logger.debug(f"ESA_TOKEN from env (for EsaClient): {esa_token}")
logger.debug(f"ESA_TEAM_NAME from env (for EsaClient): {esa_team_name}")

# Create MCP instance
mcp = FastMCP("esa-mcp-server")

# Initialize EsaClient
if not esa_token or not esa_team_name:
    logger.error("ESA_TOKEN or ESA_TEAM_NAME environment variable not set (or empty).")  # 少し詳細なエラーログに変更
    esa_client = None
else:
    try:
        esa_client = EsaClient(token=esa_token, team_name=esa_team_name)
        logger.info("EsaClient initialized successfully.")
    except ValueError as e:  # Catch potential ValueError from EsaClient init
        logger.error(f"Failed to initialize EsaClient: {e}")
        esa_client = None
    except Exception as e:
        logger.error(f"An unexpected error occurred during EsaClient initialization: {e}")
        esa_client = None


# --- MCP Tools Definition ---
@mcp.tool()
def user_get_info() -> dict[str, Any]:
    """Get current esa.io user information"""
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot get user info.")
        # Raise standard exception instead of HTTPException
        raise RuntimeError("EsaClient not initialized")
    try:
        logger.info("Getting user info...")
        user_info = esa_client.get_user()
        logger.info(f"Successfully retrieved user info: {user_info}")
        return user_info
    except Exception as e:
        logger.error(f"Error getting user info: {e}", exc_info=True)
        # Raise standard exception
        raise RuntimeError(f"Error getting user info: {e}") from e


@mcp.tool()
def posts_get_list(q: str | None = None, page: int | None = None, per_page: int | None = None) -> dict[str, Any]:
    """Get a list of posts from esa.io

    Args:
        q: Search query
        page: Page number
        per_page: Number of posts per page (max 100)
    """
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot get posts list.")
        raise RuntimeError("EsaClient not initialized")
    try:
        logger.info(f"Getting posts list with query='{q}', page={page}, per_page={per_page}")
        params = {}
        if q:
            params["q"] = q
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page

        posts_list = esa_client.get_posts(**params)
        logger.info(f"Successfully retrieved {len(posts_list.get('posts', []))} posts.")
        return posts_list
    except Exception as e:
        logger.error(f"Error getting posts list: {e}", exc_info=True)
        raise RuntimeError(f"Error getting posts list: {e}") from e


@mcp.tool()
def posts_get_detail(post_number: int) -> dict[str, Any]:
    """Get details of a specific post from esa.io

    Args:
        post_number: The number of the post to retrieve
    """
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot get post detail.")
        raise RuntimeError("EsaClient not initialized")
    try:
        logger.info(f"Getting detail for post number: {post_number}")
        post_detail = esa_client.get_post(post_number)
        logger.info(f"Successfully retrieved detail for post {post_number}.")
        return post_detail
    except Exception as e:
        logger.error(f"Error getting post detail for {post_number}: {e}", exc_info=True)
        raise RuntimeError(f"Error getting post detail: {e}") from e


@mcp.tool()
def posts_create(
    name: str,
    body_md: str,
    tags: Annotated[list[str], Field(description="List of tags for the post")] = [],
    category: Annotated[str, Field(description="Category path (e.g., 'foo/bar')")] = "",
    wip: Annotated[bool, Field(description="Whether the post is Work In Progress (default: true)")] = True,
    message: Annotated[str, Field(description="Commit message for the post")] = "",
) -> dict[str, Any]:
    """Create a new post on esa.io

    Args:
        name: Post title
        body_md: Post body in Markdown format
        tags: List of tags for the post
        category: Category path (e.g., 'foo/bar')
        wip: Whether the post is Work In Progress (default: true)
        message: Commit message for the post
    """
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot create post.")
        raise RuntimeError("EsaClient not initialized")
    try:
        logger.info(f"Creating post with name: {name}")

        payload = {
            "name": name,
            "body_md": body_md,
            "tags": tags or [],
            "category": category,
            "wip": wip,
            "message": message,
        }
        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}

        new_post = esa_client.create_post(payload=payload)
        logger.info(f"Successfully created post: {new_post.get('url')}")
        return new_post
    except Exception as e:
        logger.error(f"Error creating post: {e}", exc_info=True)
        raise RuntimeError(f"Error creating post: {e}") from e


@mcp.tool()
def posts_update(
    post_number: int,
    name: Annotated[str, Field(default=None, description="New post title")] = None,
    body_md: Annotated[str, Field(default=None, description="New post body in Markdown format")] = None,
    tags: Annotated[list[str], Field(default=None, description="New list of tags")] = None,
    category: Annotated[str, Field(default=None, description="New category path")] = None,
    wip: Annotated[bool, Field(default=None, description="New WIP status")] = None,
    message: Annotated[str, Field(default=None, description="Commit message for the update")] = None,
) -> dict[str, Any]:
    """Update an existing post on esa.io

    Args:
        post_number: The number of the post to update
        name: New post title
        body_md: New post body in Markdown format
        tags: New list of tags
        category: New category path
        wip: New WIP status
        message: Commit message for the update
    """
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot update post.")
        raise RuntimeError("EsaClient not initialized")
    try:
        logger.info(f"Updating post number: {post_number}")
        payload = {
            "name": name,
            "body_md": body_md,
            "tags": tags,
            "category": category,
            "wip": wip,
            "message": message,
        }
        # Remove None values from payload to avoid overwriting existing values with None
        payload = {k: v for k, v in payload.items() if v is not None}

        if not payload:
            logger.warning(f"No update parameters provided for post {post_number}.")
            # Consider returning current post details or raising a more specific error
            return {"message": f"No update parameters provided for post {post_number}. Nothing changed."}

        updated_post = esa_client.update_post(post_number=post_number, payload=payload)
        logger.info(f"Successfully updated post: {updated_post.get('url')}")
        return updated_post
    except Exception as e:
        logger.error(f"Error updating post {post_number}: {e}", exc_info=True)
        raise RuntimeError(f"Error updating post: {e}") from e


@mcp.tool()
def posts_delete(post_number: int) -> dict[str, Any]:
    """Delete a post on esa.io

    Args:
        post_number: The number of the post to delete
    """
    if esa_client is None:
        logger.error("EsaClient is not initialized. Cannot delete post.")
        raise RuntimeError("EsaClient not initialized")
    try:
        esa_client.delete_post(post_number)
        logger.info(f"Successfully deleted post {post_number}.")
        # Return empty dict upon successful deletion as per esa.io API
        return {}
    except Exception as e:
        logger.error(f"Error deleting post {post_number}: {e}", exc_info=True)
        raise RuntimeError(f"Error deleting post: {e}") from e

def main():
    """MCPサーバーを起動するためのメイン関数"""
    logger.info("Starting MCP server via main()...")
    mcp.run()

# Use mcp.run() to start the server when script is executed directly
if __name__ == "__main__":
    main()
