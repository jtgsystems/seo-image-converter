"""Pytest configuration and fixtures for SEO Image Converter tests."""

import tempfile
from pathlib import Path
import pytest
from PIL import Image


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_image(temp_dir):
    """Create a sample test image."""
    image_path = temp_dir / "test_image.jpg"
    img = Image.new("RGB", (800, 600), color=(73, 109, 137))
    img.save(image_path, "JPEG", quality=90)
    return image_path


@pytest.fixture
def sample_images(temp_dir):
    """Create multiple sample test images."""
    images = []
    for i in range(3):
        image_path = temp_dir / f"test_image_{i}.jpg"
        img = Image.new("RGB", (800, 600), color=(73 + i * 20, 109, 137))
        img.save(image_path, "JPEG", quality=90)
        images.append(image_path)
    return images


@pytest.fixture
def sample_png_with_alpha(temp_dir):
    """Create a PNG image with alpha channel."""
    image_path = temp_dir / "test_alpha.png"
    img = Image.new("RGBA", (800, 600), color=(255, 0, 0, 128))
    img.save(image_path, "PNG")
    return image_path


@pytest.fixture
def test_config_file(temp_dir):
    """Create a test configuration file."""
    config_path = temp_dir / "test_config.yaml"
    config_content = """# Test configuration
ollama:
  endpoint: "http://localhost:11434/api/generate"
  model: "qwen2.5vl:7b"
  timeout: 45
  max_retries: 3
  retry_delay: 2

seo:
  keyword_count: 10
  max_filename_length: 120
  fallback_prefix: "image"

image:
  formats:
    input: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]
    output: "webp"
  quality:
    webp: 85
    jpeg: 90
    png: 90
  optimization:
    lossless: true
    strip_metadata: true

processing:
  parallel_jobs: 2
  batch_size: 10
  backup_originals: false
  skip_existing: false
  dry_run: false

logging:
  level: "INFO"
  file: "test_converter.log"
  console: true
"""
    config_path.write_text(config_content)
    return config_path
