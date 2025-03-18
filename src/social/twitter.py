import tweepy

class TwitterHandler:
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret):
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_secret
        )
        self.api = tweepy.API(auth)

    def post(self, message, image_path=None):
        try:
            if image_path:
                media = self.api.media_upload(image_path)
                self.api.update_status(status=message, media_ids=[media.media_id])
            else:
                self.api.update_status(status=message)
            print("Twitter post successful!")
        except tweepy.TweepyException as e:
            print(f"Twitter post failed: {e}")