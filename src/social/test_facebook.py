from unittest.mock import MagicMock, patch

from .facebook import FacebookHandler


def _mock_response(status_code, json_body):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = str(json_body)
    resp.json.return_value = json_body
    return resp


def test_post_returns_true_on_success_without_image():
    handler = FacebookHandler(page_id="123", access_token="token")

    with patch("src.social.facebook.requests.post") as mock_post:
        mock_post.return_value = _mock_response(200, {"id": "post1"})
        result = handler.post("hello world")

    assert result is True
    mock_post.assert_called_once()
    assert mock_post.call_args.kwargs["data"]["message"] == "hello world"
    assert "files" not in mock_post.call_args.kwargs or mock_post.call_args.kwargs.get("files") is None


def test_post_returns_true_on_success_with_image_and_closes_file(tmp_path):
    handler = FacebookHandler(page_id="123", access_token="token")
    image = tmp_path / "pic.jpg"
    image.write_bytes(b"fake-image-bytes")

    captured_file = {}

    def fake_post(url, data=None, files=None):
        captured_file["handle"] = files["source"]
        return _mock_response(200, {"id": "post1", "post_id": "123_456"})

    with patch("src.social.facebook.requests.post", side_effect=fake_post):
        result = handler.post("hello with image", image_path=str(image))

    assert result is True
    # The file handle passed to requests.post must be closed afterwards,
    # proving the handler no longer leaks it.
    assert captured_file["handle"].closed is True


def test_post_returns_false_on_http_error_status():
    handler = FacebookHandler(page_id="123", access_token="token")

    with patch("src.social.facebook.requests.post") as mock_post:
        mock_post.return_value = _mock_response(
            403,
            {"error": {"message": "permission denied", "code": 200}},
        )
        result = handler.post("hello world")

    assert result is False


def test_post_returns_false_when_200_body_contains_error():
    """Facebook's Graph API sometimes returns HTTP 200 with an error payload."""
    handler = FacebookHandler(page_id="123", access_token="token")

    with patch("src.social.facebook.requests.post") as mock_post:
        mock_post.return_value = _mock_response(
            200,
            {"error": {"message": "credits depleted", "code": 402}},
        )
        result = handler.post("hello world")

    assert result is False
