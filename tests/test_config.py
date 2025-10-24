"""Tests for configuration management module."""

import pytest
from pathlib import Path
from src.config import Config


def test_config_loads_yaml(test_config_file):
    """Test that configuration loads from YAML file."""
    config = Config(test_config_file)

    assert config.ollama["model"] == "qwen2.5vl:7b"
    assert config.seo["keyword_count"] == 10
    assert config.image["formats"]["output"] == "webp"


def test_config_ollama_properties(test_config_file):
    """Test ollama configuration properties."""
    config = Config(test_config_file)

    assert "endpoint" in config.ollama
    assert "model" in config.ollama
    assert config.ollama["timeout"] == 45


def test_config_seo_properties(test_config_file):
    """Test SEO configuration properties."""
    config = Config(test_config_file)

    assert config.seo["keyword_count"] == 10
    assert config.seo["max_filename_length"] == 120
    assert config.seo["fallback_prefix"] == "image"


def test_config_image_properties(test_config_file):
    """Test image configuration properties."""
    config = Config(test_config_file)

    assert config.image["formats"]["output"] == "webp"
    assert config.image["quality"]["webp"] == 85
    assert ".jpg" in config.image["formats"]["input"]


def test_config_processing_properties(test_config_file):
    """Test processing configuration properties."""
    config = Config(test_config_file)

    assert config.processing["parallel_jobs"] == 2
    assert config.processing["batch_size"] == 10
    assert config.processing["backup_originals"] is False


def test_config_get_with_dot_notation(test_config_file):
    """Test get method with dot notation."""
    config = Config(test_config_file)

    assert config.get("ollama.model") == "qwen2.5vl:7b"
    assert config.get("image.formats.output") == "webp"
    assert config.get("nonexistent.key", "default") == "default"


def test_config_update_with_dot_notation(test_config_file):
    """Test update method with dot notation."""
    config = Config(test_config_file)

    config.update("ollama.timeout", 60)
    assert config.get("ollama.timeout") == 60

    config.update("new.nested.value", 42)
    assert config.get("new.nested.value") == 42


def test_config_save(test_config_file, temp_dir):
    """Test saving configuration to file."""
    config = Config(test_config_file)
    config.update("test.value", "modified")

    new_path = temp_dir / "saved_config.yaml"
    config.save(str(new_path))

    # Load saved config and verify
    loaded_config = Config(new_path)
    assert loaded_config.get("test.value") == "modified"


def test_config_missing_file():
    """Test that missing config file raises error."""
    with pytest.raises(FileNotFoundError):
        Config("/nonexistent/config.yaml")


def test_config_invalid_yaml(temp_dir):
    """Test that invalid YAML raises error."""
    invalid_config = temp_dir / "invalid.yaml"
    invalid_config.write_text("invalid: yaml: content:")

    with pytest.raises(ValueError):
        Config(invalid_config)
