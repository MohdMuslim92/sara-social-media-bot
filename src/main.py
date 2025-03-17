import argparse
import os
import yaml
from src.social.social_factory import SocialFactory
from src.utils.content_loader import ContentLoader
from src.utils.image_handler import ImageHandler

# Path to store the last posted index for each platform
STATE_FILE = "post_state.yaml"

def load_state():
    """Load the last posted index for each platform."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {"facebook": 0, "twitter": 0}
    return {"facebook": 0, "twitter": 0}

def save_state(state):
    """Save the current state to the file."""
    with open(STATE_FILE, "w", encoding="utf-8") as file:
        yaml.safe_dump(state, file)

def format_post(post, platform):
    """Format the post text with the Facebook footer if applicable."""
    text = post["text"]
    if platform == "facebook" and "facebook_footer" in post:
        text += "\n\n" + post["facebook_footer"]
    return text

def get_next_post(posts, platform, last_index):
    """Get the next post for the specified platform, starting from the last index."""
    for i in range(last_index, len(posts)):
        if platform in posts[i]["platforms"]:
            return posts[i], i + 1  # Return the post and the next index
    # If no more posts are found, start from the beginning
    for i in range(0, last_index):
        if platform in posts[i]["platforms"]:
            return posts[i], i + 1
    return None, 0  # No posts found for the platform

def main(post_type):
    # Load posts
    posts = ContentLoader.load_posts(post_type)

    # Load the last posted index for each platform
    state = load_state()

    # Process posts for each platform
    for platform in ["facebook", "twitter"]:
        # Get the next post for the platform
        post, next_index = get_next_post(posts, platform, state[platform])
        if not post:
            print(f"No posts found for {platform}. Skipping.")
            continue

        # Format the post text
        formatted_text = format_post(post, platform)

        # Get the image path if available
        image_path = None
        if "image" in post:
            image_path = ImageHandler.get_image_path(post_type, post["image"])

        # Post to the platform
        handler = SocialFactory.get_handler(platform)
        handler.post(formatted_text, image_path)

        # Update the state
        state[platform] = next_index

    # Save the updated state
    save_state(state)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, help="Type of posts (e.g., friday, ramadan)")
    args = parser.parse_args()

    main(args.type)