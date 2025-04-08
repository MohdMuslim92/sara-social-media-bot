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
    try:
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {"facebook": 0, "twitter": 0}
        return {"facebook": 0, "twitter": 0}
    except (OSError, yaml.YAMLError) as e:
        logging.error("Error loading state: %s", e)
        return {"facebook": 0, "twitter": 0}

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

    Args:
        post_type (str): The type of posts to process (e.g., 'friday', 'ramadan', 'daily').
    """
    try:
        # Log the start of the process
        logging.info("Starting %s posts at %s", post_type, datetime.now())

        # Load posts
        posts = ContentLoader.load_posts(post_type)

        # Select the correct state file based on post type
        if post_type == "friday":
            state_file = FRIDAY_STATE_FILE
        elif post_type == "daily":
            state_file = DAILY_STATE_FILE
        else:
            state_file = STATE_FILE  # Default (e.g., Ramadan)

        state = load_state(state_file)

        # Process posts for each platform
        for platform in ["facebook", "twitter"]:
            try:
                # Get the next post for the platform
                post, next_index = get_next_post(posts, platform, state[platform])
                if not post:
                    logging.warning("No posts found for %s. Skipping.", platform)
                    continue

                # Format the post text
                formatted_text = format_post(post, platform)
                if not formatted_text:
                    logging.error("Failed to format post for %s. Skipping.", platform)
                    continue

                # Get the image path if available
                image_path = None
                if "image" in post:
                    try:
                        image_path = ImageHandler.get_image_path(post_type, post["image"])
                    except (OSError, IOError) as e:
                        logging.error(f"Error loading image for {platform}: %s", e)

                # Post to the platform
                handler = SocialFactory.get_handler(platform)
                handler.post(formatted_text, image_path)

                # Update the state
                state[platform] = next_index
            except (KeyError, ValueError, OSError, TypeError) as e:
                logging.error(f"Error processing {platform}: %s", e)

        # Save the updated state
        save_state(state, state_file)
    except (OSError, KeyError, ValueError) as e:
        logging.error("Unexpected error in main: %s", e)
    finally:
        # Log the end of the process
        logging.info("Finished %s posts at %s", post_type, datetime.now())

if __name__ == "__main__":
    # Entry point for the script. Parses command-line arguments and runs main().

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type", required=True, help="Type of posts (e.g., friday, ramadan, daily)")
    args = parser.parse_args()

    main(args.type)
