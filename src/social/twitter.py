import tweepy
import logging

class TwitterHandler:
    def __init__(self, consumer_key, consumer_secret, access_token, access_secret, bearer_token):
        try:
            # For media upload (v1.1)
            self.auth_v1 = tweepy.OAuth1UserHandler(
                consumer_key,
                consumer_secret,
                access_token,
                access_secret
            )
            self.api_v1 = tweepy.API(self.auth_v1)

            # For tweet posting (v2)
            self.client_v2 = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )

            self.api_v1.verify_credentials()
            logging.info("Twitter authentication successful")
        except tweepy.TweepyException as e:
            logging.error(f"Twitter auth failed: {e}")
            raise

    def post(self, message, image_path=None):
        try:
            media_ids = []
            if image_path:
                # Upload media using v1.1
                media = self.api_v1.media_upload(image_path)
                media_ids.append(media.media_id)
                logging.info(f"Uploaded media: {media.media_id}")

            # Post tweet using v2
            self.client_v2.create_tweet(text=message, media_ids=media_ids)
            logging.info("Twitter post successful")
        except tweepy.TweepyException as e:
            logging.error(f"Twitter post failed: {e}")