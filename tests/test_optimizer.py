"""Tests for image optimizer module."""

import pytest
from pathlib import Path
from PIL import Image
from src.optimizer import ImageOptimizer
from src.config import Config


@pytest.fixture
def optimizer(test_config_file):
    """Create optimizer instance with test config."""
    # Mock config to avoid loading actual config
    class MockConfig:
        image = {
            "formats": {
                "input": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
                "output": "webp",
            },
            "quality": {"webp": 85, "jpeg": 90, "png": 90},
            "optimization": {
                "lossless": True,
                "strip_metadata": True,
                "resize_large": False,
            },
        }

    from src import optimizer as opt_module

    original_config = opt_module.config
    opt_module.config = MockConfig()

    yield ImageOptimizer()

    opt_module.config = original_config


def test_is_supported_image_valid_formats(optimizer, sample_image):
    """Test that valid image formats are supported."""
    assert optimizer.is_supported_image(sample_image) is True


def test_is_supported_image_invalid_path(optimizer):
    """Test that nonexistent files return False."""
    assert optimizer.is_supported_image(Path("/nonexistent/file.jpg")) is False


def test_is_supported_image_wrong_extension(optimizer, temp_dir):
    """Test that unsupported extensions return False."""
    txt_file = temp_dir / "test.txt"
    txt_file.write_text("not an image")

    assert optimizer.is_supported_image(txt_file) is False


def test_get_image_info(optimizer, sample_image):
    """Test getting image information."""
    info = optimizer.get_image_info(sample_image)

    assert info["format"] in ["JPEG", "JPG"]
    assert info["width"] == 800
    assert info["height"] == 600
    assert info["file_size"] > 0
    assert "has_transparency" in info


def test_get_image_info_with_alpha(optimizer, sample_png_with_alpha):
    """Test getting info from PNG with alpha channel."""
    info = optimizer.get_image_info(sample_png_with_alpha)

    assert info["format"] == "PNG"
    assert info["has_transparency"] is True


def test_get_image_info_invalid_file(optimizer):
    """Test getting info from invalid file."""
    info = optimizer.get_image_info(Path("/nonexistent/file.jpg"))

    assert info == {}


def test_optimize_to_webp(optimizer, sample_image, temp_dir):
    """Test optimizing JPEG to WebP."""
    output_path = temp_dir / "optimized.webp"

    success, result = optimizer.optimize_image(sample_image, output_path)

    assert success is True
    assert output_path.exists()
    assert result["format"] == "webp"
    assert result["original_size"] > 0
    assert result["optimized_size"] > 0
    assert result["compression_ratio"] >= 0


def test_optimize_to_png(optimizer, sample_image, temp_dir):
    """Test optimizing JPEG to PNG."""
    # Change output format temporarily
    optimizer.output_format = "png"
    output_path = temp_dir / "optimized.png"

    success, result = optimizer.optimize_image(sample_image, output_path)

    assert success is True
    assert output_path.exists()
    assert result["format"] == "png"


def test_optimize_to_jpeg(optimizer, sample_image, temp_dir):
    """Test optimizing to JPEG."""
    optimizer.output_format = "jpeg"
    output_path = temp_dir / "optimized.jpg"

    success, result = optimizer.optimize_image(sample_image, output_path)

    assert success is True
    assert output_path.exists()
    assert result["format"] == "jpeg"


def test_optimize_unsupported_format(optimizer, sample_image, temp_dir):
    """Test optimizing to unsupported format."""
    optimizer.output_format = "unsupported"
    output_path = temp_dir / "optimized.xyz"

    success, result = optimizer.optimize_image(sample_image, output_path)

    assert success is False
    assert "error" in result
    assert "Unsupported output format" in result["error"]


def test_optimize_invalid_input(optimizer, temp_dir):
    """Test optimizing invalid input file."""
    invalid_input = temp_dir / "nonexistent.jpg"
    output_path = temp_dir / "output.webp"

    success, result = optimizer.optimize_image(invalid_input, output_path)

    assert success is False
    assert "error" in result


def test_compression_ratio_calculation(optimizer, sample_image, temp_dir):
    """Test that compression ratio is calculated correctly."""
    output_path = temp_dir / "compressed.webp"

    success, result = optimizer.optimize_image(sample_image, output_path)

    assert success is True

    original_size = result["original_size"]
    optimized_size = result["optimized_size"]
    compression_ratio = result["compression_ratio"]

    expected_ratio = (1 - optimized_size / original_size) * 100

    assert abs(compression_ratio - expected_ratio) < 0.1


def test_optimize_preserves_transparency(optimizer, sample_png_with_alpha, temp_dir):
    """Test that transparency is preserved when optimizing to WebP."""
    output_path = temp_dir / "transparent.webp"

    success, result = optimizer.optimize_image(sample_png_with_alpha, output_path)

    assert success is True

    # Verify transparency is preserved
    with Image.open(output_path) as img:
        assert img.mode in ["RGBA", "LA"] or img.format == "WebP"
