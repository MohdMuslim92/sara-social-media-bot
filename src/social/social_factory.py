from .facebook import FacebookHandler
from .twitter import TwitterHandler
from ..config import PLATFORMS

class SocialFactory:
    @staticmethod
    def get_handler(platform):
        if platform == "facebook":
            return FacebookHandler(
                PLATFORMS["facebook"]["page_id"],
                PLATFORMS["facebook"]["access_token"]
            )
        elif platform == "twitter":
            return TwitterHandler(
                PLATFORMS["twitter"]["consumer_key"],
                PLATFORMS["twitter"]["consumer_secret"],
                PLATFORMS["twitter"]["access_token"],
                PLATFORMS["twitter"]["access_secret"]
            )
        else:
            raise ValueError(f"Unsupported platform: {platform}")