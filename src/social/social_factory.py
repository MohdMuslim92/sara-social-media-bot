from .facebook import FacebookHandler
from ..config import PLATFORMS

class SocialFactory:
    @staticmethod
    def get_handler(platform):
        if platform == "facebook":
            return FacebookHandler(
                PLATFORMS["facebook"]["page_id"],
                PLATFORMS["facebook"]["access_token"]
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")