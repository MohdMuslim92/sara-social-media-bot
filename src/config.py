"""
This module handles loading and accessing environment variables for social media platforms,
such as Facebook, and sets up directory paths for content storage.

Main Features:
- Loads environment variables from github action secrets.
- Configures platform-specific API credentials (Facebook).
- Sets up directory paths for content storage, including images and posts.

Usage:
    Ensure github action secrets are set with the required API credentials for each platform.
    The directories for content, images, and posts are set relative to this script's location.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Dictionary to store platform credentials (Facebook)
PLATFORMS = {
    "facebook": {
        "page_id": os.getenv("FB_PAGE_ID"),
        "access_token": os.getenv("FB_ACCESS_TOKEN")
    }
}

# Directory paths for content, images, and posts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "content")
IMAGE_DIR = os.path.join(CONTENT_DIR, "images")
POSTS_DIR = os.path.join(CONTENT_DIR, "posts")
