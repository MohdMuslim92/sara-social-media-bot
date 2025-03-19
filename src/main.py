import argparse
import os
import yaml
import logging
from datetime import datetime
from .social.social_factory import SocialFactory
from .utils.content_loader import ContentLoader
from .utils.image_handler import ImageHandler

# Path to store the last posted index for each platform
STATE_FILE = "post_state.yaml"
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

def load_state():
    """Load the last posted index for each platform."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                return yaml.safe_load(file) or {"facebook": 0, "twitter": 0}
        return {"facebook": 0, "twitter": 0}
    except Exception as e:
        logging.error(f"Error loading state: {e}")
        return {"facebook": 0, "twitter": 0}

def save_state(state):
    """Save the current state to the file."""
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            yaml.safe_dump(state, file)
    except Exception as e:
        logging.error(f"Error saving state: {e}")

def format_post(post, platform):
    """Format the post text with the Facebook footer and hashtags if applicable."""
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
    except Exception as e:
        logging.error(f"Error formatting post: {e}")
        return None

def get_next_post(posts, platform, last_index):
    """Get the next post for the specified platform, starting from the last index."""
    try:
        for i in range(last_index, len(posts)):
            if platform in posts[i]["platforms"]:
                return posts[i], i + 1  # Return the post and the next index
        # If no more posts are found, start from the beginning
        for i in range(0, last_index):
            if platform in posts[i]["platforms"]:
                return posts[i], i + 1
        return None, 0  # No posts found for the platform
    except Exception as e:
        logging.error(f"Error getting next post: {e}")
        return None, 0

def main(post_type):
    try:
        # Log the start of the process
        logging.info(f"Starting {post_type} posts at {datetime.now()}")

        # Load posts
        posts = ContentLoader.load_posts(post_type)

        # Load the last posted index for each platform
        state = load_state()

        # Process posts for each platform
        for platform in ["facebook", "twitter"]:
            try:
                # Get the next post for the platform
                post, next_index = get_next_post(posts, platform, state[platform])
                if not post:
                    logging.warning(f"No posts found for {platform}. Skipping.")
                    continue

                # Format the post text
                formatted_text = format_post(post, platform)
                if not formatted_text:
                    logging.error(f"Failed to format post for {platform}. Skipping.")
                    continue

                # Get the image path if available
                image_path = None
                if "image" in post:
                    try:
                        image_path = ImageHandler.get_image_path(post_type, post["image"])
                    except Exception as e:
                        logging.error(f"Error loading image for {platform}: {e}")

                # Post to the platform
                handler = SocialFactory.get_handler(platform)
                handler.post(formatted_text, image_path)

                # Update the state
                state[platform] = next_index
            except Exception as e:
                logging.error(f"Error processing {platform}: {e}")

        # Save the updated state
        save_state(state)
    except Exception as e:
        logging.error(f"Unexpected error in main: {e}")
    finally:
        # Log the end of the process
        logging.info(f"Finished {post_type} posts at {datetime.now()}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="Type of posts (e.g., friday, ramadan)")
    args = parser.parse_args()

    main(args.type)