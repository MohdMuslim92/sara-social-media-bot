"""
This module handles loading and accessing environment variables for social media platforms,
such as Facebook and Twitter, and sets up directory paths for content storage.

Main Features:
- Loads environment variables from github action secrets.
- Configures platform-specific API credentials (Facebook and Twitter).
- Sets up directory paths for content storage, including images and posts.

Usage:
    Ensure github action secrets are set with the required API credentials for each platform.
    The directories for content, images, and posts are set relative to this script's location.
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Dictionary to store platform credentials (Facebook and Twitter)
PLATFORMS = {
    "facebook": {
        "page_id": os.getenv("FB_PAGE_ID"),
        "access_token": os.getenv("FB_ACCESS_TOKEN")
    },
    "twitter": {
        "consumer_key": os.getenv("TW_CONSUMER_KEY"),
        "consumer_secret": os.getenv("TW_CONSUMER_SECRET"),
        "access_token": os.getenv("TW_ACCESS_TOKEN"),
        "access_secret": os.getenv("TW_ACCESS_SECRET"),
        "bearer_token": os.getenv("TW_BEARER_TOKEN")
    }
}

# Directory paths for content, images, and posts
CONTENT_DIR = os.path.join(os.path.dirname(__file__), "../content")
IMAGE_DIR = os.path.join(CONTENT_DIR, "images")
POSTS_DIR = os.path.join(CONTENT_DIR, "posts")
