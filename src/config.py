import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

PLATFORMS = {
    "facebook": {
        "page_id": os.getenv("FB_PAGE_ID"),
        "access_token": os.getenv("FB_ACCESS_TOKEN")
    },
    "twitter": {
        "consumer_key": os.getenv("TW_CONSUMER_KEY"),
        "consumer_secret": os.getenv("TW_CONSUMER_SECRET"),
        "access_token": os.getenv("TW_ACCESS_TOKEN"),
        "access_secret": os.getenv("TW_ACCESS_SECRET")
    }
}

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "../content")
IMAGE_DIR = os.path.join(CONTENT_DIR, "images")
POSTS_DIR = os.path.join(CONTENT_DIR, "posts")