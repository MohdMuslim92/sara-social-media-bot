"""
Automated Social Media Poster

This module handles posting pre-written content to social media platforms
such as Facebook and Twitter. It supports various post types like Friday,
daily, and Ramadan posts, keeps track of the last posted content, and ensures
content is formatted and published correctly.

Main Features:
- Loads posts from content files
- Formats posts with optional footers and hashtags
- Handles platform-specific posting via SocialFactory
- Maintains state to avoid reposting the same content
- Logs all operations and errors for transparency

Usage:
    python script_name.py --type friday
"""

import argparse
import os
import logging
from datetime import datetime
import yaml
from .social.social_factory import SocialFactory
from .utils.content_loader import ContentLoader
from .utils.image_handler import ImageHandler

# Path to store the last posted index for each platform
STATE_FILE = "post_state.yaml"  # For Ramadan posts
FRIDAY_STATE_FILE = "friday_state.yaml"  # For Friday posts
DAILY_STATE_FILE = "daily_state.yaml"  # For Monday and Thursday posts
LOG_FILE = "logs.txt"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def load_state(state_file):
    """
    Load the last posted index for each platform from a YAML file.

    Args:
        state_file (str): Path to the YAML state file.

    Returns:
        dict: Dictionary with last posted indices per platform.
    """
    default_state = {
        "facebook": {"post_index": 0, "image_index": 0},
        "twitter": {"post_index": 0, "image_index": 0}
    }
    try:
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as file:
                loaded_state = yaml.safe_load(file) or {}
                # Migrate old state format to new structure
                for platform in ["facebook", "twitter"]:
                    if platform in loaded_state:
                        if isinstance(loaded_state[platform], int):
                            loaded_state[platform] = {
                                "post_index": loaded_state[platform],
                                "image_index": 0
                            }
                    loaded_state.setdefault(platform, default_state[platform].copy())
                    loaded_state[platform].setdefault("post_index", 0)
                    loaded_state[platform].setdefault("image_index", 0)
                return loaded_state
        return default_state.copy()
    except (OSError, yaml.YAMLError) as e:
        logging.error("Error loading state: %s", e)
        return default_state.copy()

def save_state(state, state_file):
    """
    Save the current state (last posted index per platform) to a YAML file.

    Args:
        state (dict): Dictionary containing post indices per platform.
        state_file (str): Path to the YAML state file.
    """
    try:
        with open(state_file, "w", encoding="utf-8") as file:
            yaml.safe_dump(state, file)
    except (OSError, yaml.YAMLError) as e:
        logging.error("Error saving state: %s", e)

def format_post(post, platform):
    """
    Format a post's text for a specific platform, appending footers and hashtags.

    Args:
        post (dict): The post content.
        platform (str): Target platform (e.g., 'facebook', 'twitter').

    Returns:
        str or None: Formatted post text or None if formatting fails.
    """
    try:
        text = post["text"]

        # Add Facebook footer if exists
        if platform == "facebook" and "facebook_footer" in post:
            text += "\n\n" + post["facebook_footer"]

        # Add hashtags
        if "hashtags" in post:
            hashtags = " ".join(f"#{tag}" for tag in post["hashtags"])
            text += "\n\n" + hashtags

        return text
    except (KeyError, TypeError) as e:
        logging.error("Error formatting post: %s", e)
        return None

def get_next_post(posts, platform, last_index):
    """
    Retrieve the next post for a given platform, starting from the last index.

    Args:
        posts (list): List of post dictionaries.
        platform (str): Target platform name.
        last_index (int): Index to start searching from.

    Returns:
        tuple: (next post dict or None, next index to use)
    """
    try:
        for i in range(last_index, len(posts)):
            if platform in posts[i]["platforms"]:
                return posts[i], i + 1  # Return the post and the next index
        # If no more posts are found, start from the beginning
        for i in range(0, last_index):
            if platform in posts[i]["platforms"]:
                return posts[i], i + 1
        return None, 0  # No posts found for the platform
    except (KeyError, TypeError) as e:
        logging.error("Error getting next post: %s", e)
        return None, 0

def main(post_type):
    """
    Main function to load, format, and publish posts to different platforms.
    """
    try:
        logging.info("Starting %s posts at %s", post_type, datetime.now())
        posts = ContentLoader.load_posts(post_type)
        state_file = get_state_file(post_type)
        state = load_state(state_file)

        # Process each platform in separate function
        for platform in ["facebook", "twitter"]:
            process_platform_posts(platform, posts, state, post_type)

        save_state(state, state_file)
    except (OSError, KeyError, ValueError) as e:
        logging.error("Unexpected error in main: %s", e)
    finally:
        logging.info("Finished %s posts at %s", post_type, datetime.now())

def get_state_file(post_type):
    """Helper to get appropriate state file"""
    return {
        "friday": FRIDAY_STATE_FILE,
        "daily": DAILY_STATE_FILE
    }.get(post_type, STATE_FILE)

def process_platform_posts(platform, posts, state, post_type):
    """Handle all processing for a single platform"""
    try:
        platform_state = state[platform]
        post_data = get_next_post_data(posts, platform, platform_state["post_index"])

        if not post_data:
            return

        # Changed: Get both formatted content AND next image index
        formatted_text, image_path, next_image_index = prepare_post_content(
            post_data.post,  # Changed: Pass post directly instead of PostData object
            platform,
            platform_state["image_index"],
            post_type
        )

        if formatted_text:
            post_content(platform, formatted_text, image_path)
            # Changed: Use the returned next_image_index directly
            update_platform_state(platform_state, post_data.next_index, next_image_index)

    except (KeyError, ValueError, OSError, TypeError) as e:
        logging.error("Error processing %s: %s", platform, e)

def get_next_post_data(posts, platform, current_index):
    """Retrieve and validate next post"""
    post, next_index = get_next_post(posts, platform, current_index)
    if not post:
        logging.warning("No posts found for %s. Skipping.", platform)
        return None
    return type('PostData', (), {'post': post, 'next_index': next_index})

def prepare_post_content(post, platform, current_image_index, post_type):
    """Format text and prepare image (returns text, path, next_image_index)"""
    formatted_text = format_post(post, platform)
    if not formatted_text:
        return None, None, None

    sorted_paths = _get_sorted_image_paths(post_type)
    if not sorted_paths:
        logging.warning("No images found for %s posts", post_type)
        return formatted_text, None, 0

    # Use modulo to cycle through available images
    total = len(sorted_paths)
    current_idx = current_image_index % total
    next_idx = (current_image_index + 1) % total

    selected_image = sorted_paths[current_idx]
    return formatted_text, selected_image, next_idx


def _get_sorted_image_paths(post_type):
    """
    Retrieve and sort image paths based on the post_type prefix.
    Returns a list of sorted image Path objects.
    """
    image_dir = ImageHandler.get_image_path(post_type, "")
    image_paths = []

    # Gather all image paths with valid extensions and the right prefix
    for ext in ['png', 'jpg']:
        pattern = f"{post_type}_*.{ext}"
        image_paths.extend(image_dir.glob(pattern))

    valid_images = []
    for path in image_paths:
        try:
            # Extract image number from filename (e.g., "daily_001.jpg" -> 1)
            num = int(path.stem.split('_')[-1])
            valid_images.append((num, path))
        except (ValueError, IndexError):
            continue  # Skip files with incorrect naming

    # Sort by extracted number
    valid_images.sort(key=lambda x: x[0])
    return [img[1] for img in valid_images]

def post_content(platform, text, image_path):
    """Execute the actual platform post"""
    handler = SocialFactory.get_handler(platform)
    handler.post(text, image_path)

def update_platform_state(state, post_index, image_index):
    """Update state after successful posting"""
    state["post_index"] = post_index
    state["image_index"] = image_index

if __name__ == "__main__":
    # Entry point for the script. Parses command-line arguments and runs main().

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", required=True, help="Type of posts (e.g., friday, ramadan, daily)")
    args = parser.parse_args()

    main(args.type)
