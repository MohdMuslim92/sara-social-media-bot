import requests

class FacebookHandler:
    def __init__(self, page_id, access_token):
        self.page_id = page_id
        self.access_token = access_token
        self.base_url = f"https://graph.facebook.com/v18.0/{self.page_id}"

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

        response = requests.post(url, data=data, files=files if files else None)
        if response.status_code == 200:
            print("Facebook post successful!")
        else:
            print(f"Facebook post failed: {response.text}")