from PIL import Image

from .image_handler import ImageHandler


def test_resize_image_shrinks_to_max_size(tmp_path):
    src = tmp_path / "source.png"
    Image.new("RGB", (3000, 1500), color="red").save(src)

    resized = ImageHandler.resize_image(src, max_size=(1200, 1200))

    assert resized.size[0] <= 1200
    assert resized.size[1] <= 1200
    # aspect ratio preserved
    assert resized.size == (1200, 600)


def test_resize_image_leaves_smaller_image_untouched(tmp_path):
    src = tmp_path / "small.png"
    Image.new("RGB", (400, 300), color="blue").save(src)

    resized = ImageHandler.resize_image(src, max_size=(1200, 1200))

    assert resized.size == (400, 300)


def test_get_image_path_joins_type_and_name():
    path = ImageHandler.get_image_path("daily", "foo.jpg")

    assert path.parts[-3:] == ("images", "daily", "foo.jpg")
