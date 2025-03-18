import yaml
from pathlib import Path
from config import POSTS_DIR

class ContentLoader:
    @staticmethod
    def load_posts(post_type):
        file_path = Path(POSTS_DIR) / post_type / "posts.yaml"
        with open(file_path, "r", encoding="utf-8") as file:
            return yaml.safe_load(file)