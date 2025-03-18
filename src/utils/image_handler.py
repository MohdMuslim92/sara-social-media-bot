from PIL import Image
from pathlib import Path
from ..config import IMAGE_DIR

class ImageHandler:
    @staticmethod
    def get_image_path(post_type, image_name):
        return Path(IMAGE_DIR) / post_type / image_name

    @staticmethod
    def resize_image(image_path, max_size=(1200, 1200)):
        img = Image.open(image_path)
        img.thumbnail(max_size)
        return img