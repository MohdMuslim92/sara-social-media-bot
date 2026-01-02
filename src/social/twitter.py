import logging
import tweepy
from typing import Optional, List

logger = logging.getLogger(__name__)

class TwitterHandler:
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: str,
        access_secret: str,
        bearer_token: str
    ):
        """
        Initialize Twitter handler using Tweepy Client (v2). Create v1.1 API
        object only if consumer/access tokens are provided (used for media upload).
        """
        self.client_v2: Optional[tweepy.Client] = None
        self.api_v1: Optional[tweepy.API] = None

        try:
            # Initialize v2 client (used for posting tweets)
            self.client_v2 = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_secret,
                wait_on_rate_limit=True
            )

            # Verify v2 authentication by fetching the authenticated user
            # This avoids calling v1.1 verify_credentials() which may be blocked.
            me = self.client_v2.get_me()
            if not (hasattr(me, "data") and me.data):
                logger.warning("Twitter v2 client created but get_me() returned no user data.")
            else:
                logger.info("Twitter v2 authentication successful for user id: %s", me.data.get("id"))

        except tweepy.TweepyException as e:
            logger.error("Twitter v2 auth failed: %s", e)
            # Re-raise because without v2 access posting will likely fail.
            raise

        # Create a v1.1 API client only for media upload (if possible).
        # Keep this optional: if v1.1 access is denied, media uploads will fail,
        # but we still can post text using v2.
        try:
            auth_v1 = tweepy.OAuth1UserHandler(
                consumer_key,
                consumer_secret,
                access_token,
                access_secret
            )
            self.api_v1 = tweepy.API(auth_v1, wait_on_rate_limit=True)
            # Do NOT call api_v1.verify_credentials() here to avoid hitting a potentially forbidden endpoint.
            logger.info("Prepared v1.1 API client for media upload (no verify performed).")
        except Exception as e:
            # Keep going — we can still post text-only with v2
            logger.warning("Could not prepare v1.1 API client: %s", e)
            self.api_v1 = None

    def _upload_media_v1(self, image_path: str) -> List[str]:
        """
        Upload media using v1.1 endpoint and return [media_id].
        Raises TweepyException on error.
        """
        if self.api_v1 is None:
            raise RuntimeError("v1.1 API client not available for media upload")

        media = self.api_v1.media_upload(image_path)
        # Tweepy Media object may have 'media_id' or 'media_id_string'
        media_id = getattr(media, "media_id_string", None) or getattr(media, "media_id", None)
        if not media_id:
            raise RuntimeError("Failed to obtain media_id after upload")
        return [str(media_id)]

    def post(self, message: str, image_path: Optional[str] = None) -> Optional[dict]:
        """
        Post a tweet using v2. If image_path is provided, attempt to upload using v1.1.
        If v1.1 media upload is not available or fails with 403, the method will
        attempt to post text-only and log a warning.
        """
        try:
            media_ids: Optional[List[str]] = None

            if image_path:
                try:
                    media_ids = self._upload_media_v1(image_path)
                    logger.info("Uploaded media via v1.1; media_ids=%s", media_ids)
                except Exception as e:
                    # Common reasons: lack of v1.1 access, 403 Forbidden, or file errors.
                    logger.warning("Media upload failed (will attempt text-only tweet): %s", e)
                    media_ids = None

            # Use v2 Client to create the tweet (text + optional media_ids).
            # Tweepy expects media_ids as a list of strings/ids.
            create_kwargs = {"text": message}
            if media_ids:
                create_kwargs["media_ids"] = media_ids

            resp = self.client_v2.create_tweet(**create_kwargs)

            # resp is a Response object; resp.data contains tweet info on success
            if hasattr(resp, "data") and resp.data:
                logger.info("Twitter post successful: tweet id %s", resp.data.get("id"))
                return resp.data
            else:
                logger.warning("Twitter create_tweet returned no data: %s", resp)
                return None

        except tweepy.TweepyException as e:
            logger.error("Twitter post failed: %s", e)
            # Do not raise to allow caller to continue,
            # but return None to signal failure.
            return None
        except Exception as e:
            logger.error("Unexpected error posting to Twitter: %s", e)
            return None
