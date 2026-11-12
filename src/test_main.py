from unittest.mock import MagicMock, patch

from . import main as main_module


def _state():
    return {
        "facebook": {"post_index": 0, "image_index": 0},
    }


def _posts():
    return [{"text": "hello", "platforms": ["facebook"]}]


def _raise(*_args, **_kwargs):
    raise RuntimeError("boom")


def test_process_platform_posts_advances_state_on_success():
    state = _state()
    with patch.object(main_module, "prepare_post_content", return_value=("hello", None, 7)), \
         patch.object(main_module, "post_content", return_value=True) as mock_post_content:
        result = main_module.process_platform_posts("facebook", _posts(), state, "daily")

    assert result is True
    mock_post_content.assert_called_once()
    assert state["facebook"] == {"post_index": 1, "image_index": 7}


def test_process_platform_posts_does_not_advance_state_on_failure():
    """
    Regression test: a failed post must not advance post_index/image_index.
    Before this fix, every Twitter post between 2026-10-26 and 2026-11-12
    failed with 402 Payment Required but still advanced the index, so 8
    different scheduled posts were silently burned and never actually
    published. (Twitter has since been dropped entirely, but the same
    index-corruption bug applies equally to Facebook.)
    """
    state = _state()
    with patch.object(main_module, "prepare_post_content", return_value=("hello", None, 7)), \
         patch.object(main_module, "post_content", return_value=False):
        result = main_module.process_platform_posts("facebook", _posts(), state, "daily")

    assert result is False
    assert state["facebook"] == {"post_index": 0, "image_index": 0}


def test_process_platform_posts_returns_true_when_nothing_to_post():
    state = _state()
    with patch.object(main_module, "post_content") as mock_post_content:
        result = main_module.process_platform_posts("facebook", [], state, "daily")

    assert result is True
    mock_post_content.assert_not_called()
    assert state["facebook"] == {"post_index": 0, "image_index": 0}


def test_process_platform_posts_returns_false_when_formatting_fails():
    state = _state()
    with patch.object(main_module, "prepare_post_content", return_value=(None, None, None)), \
         patch.object(main_module, "post_content") as mock_post_content:
        result = main_module.process_platform_posts("facebook", _posts(), state, "daily")

    assert result is False
    mock_post_content.assert_not_called()
    assert state["facebook"] == {"post_index": 0, "image_index": 0}


def test_post_content_returns_bool_from_handler():
    handler = MagicMock()

    handler.post.return_value = {"id": "123"}
    with patch.object(main_module.SocialFactory, "get_handler", return_value=handler):
        assert main_module.post_content("facebook", "text", None) is True

    handler.post.return_value = None
    with patch.object(main_module.SocialFactory, "get_handler", return_value=handler):
        assert main_module.post_content("facebook", "text", None) is False

    handler.post.return_value = False
    with patch.object(main_module.SocialFactory, "get_handler", return_value=handler):
        assert main_module.post_content("facebook", "text", None) is False


def test_main_returns_false_when_platform_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "DAILY_STATE_FILE", str(tmp_path / "daily_state.yaml"))
    monkeypatch.setattr(main_module.ContentLoader, "load_posts", staticmethod(lambda post_type: _posts()))

    with patch.object(main_module, "process_platform_posts", return_value=False):
        success = main_module.main("daily")

    assert success is False


def test_main_returns_true_when_platform_succeeds(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "DAILY_STATE_FILE", str(tmp_path / "daily_state.yaml"))
    monkeypatch.setattr(main_module.ContentLoader, "load_posts", staticmethod(lambda post_type: _posts()))

    with patch.object(main_module, "process_platform_posts", return_value=True):
        success = main_module.main("daily")

    assert success is True


def test_main_returns_false_on_unexpected_exception(monkeypatch):
    monkeypatch.setattr(main_module.ContentLoader, "load_posts", staticmethod(_raise))

    assert main_module.main("daily") is False


def test_cli_exit_code_reflects_main_result():
    with patch.object(main_module, "main", return_value=True):
        assert main_module._cli(["--type", "daily"]) == 0

    with patch.object(main_module, "main", return_value=False):
        assert main_module._cli(["--type", "daily"]) == 1
