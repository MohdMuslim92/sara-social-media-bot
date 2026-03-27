import logging
import requests

logger = logging.getLogger(__name__)

class FacebookHandler:
    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v22.0/{self.page_id}"

    def post(self, message, image_path=None):
        url = f"{self.base_url}/photos" if image_path else f"{self.base_url}/feed"
        files = {}
        data = {
            "access_token": self.access_token,
            "message": message
        }

        if image_path:
            files["source"] = open(image_path, "rb")
            data["published"] = "true"

        logger.info("Posting to Facebook. URL: %s | Has image: %s", url, bool(image_path))
        response = requests.post(url, data=data, files=files if files else None)
        logger.info("Facebook response status: %s", response.status_code)
        logger.info("Facebook response body: %s", response.text)

        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                logger.error("Facebook post returned 200 but contains error: %s", result["error"])
            else:
                logger.info("Facebook post successful! Post ID: %s", result.get("id") or result.get("post_id"))
        else:
            logger.error("Facebook post failed with status %s: %s", response.status_code, response.text)