"""Tests for AI analyzer module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.ai_analyzer import AIImageAnalyzer


@pytest.fixture
def mock_ollama_available():
    """Mock Ollama availability check."""
    with patch.object(AIImageAnalyzer, "is_ollama_available", return_value=True):
        yield


@pytest.fixture
def mock_ollama_unavailable():
    """Mock Ollama unavailability."""
    with patch.object(AIImageAnalyzer, "is_ollama_available", return_value=False):
        yield


@pytest.fixture
def analyzer():
    """Create analyzer instance."""
    return AIImageAnalyzer()


def test_analyzer_initialization(analyzer):
    """Test analyzer initializes with correct defaults."""
    assert analyzer.model == "qwen2.5vl:7b"
    assert analyzer.timeout == 45
    assert analyzer.keyword_count == 10


def test_encode_image_base64(analyzer, sample_image):
    """Test encoding image to base64."""
    encoded = analyzer.encode_image_base64(sample_image)

    assert encoded is not None
    assert isinstance(encoded, str)
    assert len(encoded) > 0


def test_encode_image_base64_invalid_file(analyzer):
    """Test encoding nonexistent file returns None."""
    result = analyzer.encode_image_base64(Path("/nonexistent/file.jpg"))

    assert result is None


def test_generate_fallback_name(analyzer, sample_image):
    """Test fallback name generation."""
    fallback = analyzer.generate_fallback_name(sample_image)

    assert fallback.startswith("image-")
    assert len(fallback) > 6


def test_generate_fallback_name_with_original_stem(analyzer, temp_dir):
    """Test fallback name includes original filename."""
    image_path = temp_dir / "my-test-photo.jpg"
    from PIL import Image

    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    img.save(image_path)

    fallback = analyzer.generate_fallback_name(image_path)

    assert "my-test-photo" in fallback


def test_process_seo_response_basic(analyzer):
    """Test processing SEO response with basic keywords."""
    response = "happy-family-beach-vacation-sunset-children-parents-summer"

    result = analyzer._process_seo_response(response)

    assert result == "happy-family-beach-vacation-sunset-children-parents-summer"


def test_process_seo_response_uppercase(analyzer):
    """Test that uppercase is converted to lowercase."""
    response = "Happy-Family-BEACH-Vacation"

    result = analyzer._process_seo_response(response)

    assert result == "happy-family-beach-vacation"


def test_process_seo_response_strips_quotes(analyzer):
    """Test that quotes are stripped."""
    response = '"happy-family-beach-vacation"'

    result = analyzer._process_seo_response(response)

    assert result == "happy-family-beach-vacation"


def test_process_seo_response_removes_multiple_hyphens(analyzer):
    """Test that multiple hyphens are collapsed."""
    response = "happy--family---beach"

    result = analyzer._process_seo_response(response)

    assert result == "happy-family-beach"


def test_process_seo_response_multiline(analyzer):
    """Test processing response with multiple lines."""
    response = """Here are the keywords:
happy-family-beach-vacation-sunset
This is a description."""

    result = analyzer._process_seo_response(response)

    # Should extract the line with keywords
    assert "happy" in result
    assert "family" in result


def test_process_seo_response_length_limit(analyzer):
    """Test that response is truncated to max length."""
    # Create a very long response
    keywords = "-".join([f"keyword{i}" for i in range(50)])

    result = analyzer._process_seo_response(keywords)

    # Should be truncated (max_filename_length - 5 for extension)
    assert len(result) <= 115


def test_create_seo_prompt(analyzer):
    """Test SEO prompt creation."""
    prompt = analyzer._create_seo_prompt()

    assert "keywords" in prompt.lower()
    assert str(analyzer.keyword_count) in prompt
    assert "hyphens" in prompt.lower()


@patch("requests.post")
def test_generate_seo_description_success(
    mock_post, analyzer, sample_image, mock_ollama_available
):
    """Test successful SEO description generation."""
    # Mock successful API response
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": "happy-family-beach-vacation-sunset-children"
    }
    mock_post.return_value = mock_response

    result = analyzer.generate_seo_description(sample_image)

    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0


@patch("requests.post")
def test_generate_seo_description_retry_logic(
    mock_post, analyzer, sample_image, mock_ollama_available
):
    """Test retry logic on API failure."""
    # First call fails, second succeeds
    mock_response_fail = Mock()
    mock_response_fail.status_code = 500

    mock_response_success = Mock()
    mock_response_success.status_code = 200
    mock_response_success.json.return_value = {"response": "happy-family-beach"}

    mock_post.side_effect = [mock_response_fail, mock_response_success]

    with patch("time.sleep"):  # Skip actual sleep
        result = analyzer.generate_seo_description(sample_image)

    assert result is not None


def test_generate_seo_description_ollama_unavailable(
    analyzer, sample_image, mock_ollama_unavailable
):
    """Test that None is returned when Ollama unavailable."""
    result = analyzer.generate_seo_description(sample_image)

    assert result is None


@patch("requests.get")
def test_is_ollama_available_success(mock_get, analyzer):
    """Test Ollama availability check success."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "models": [{"name": "qwen2.5vl:7b"}, {"name": "llama2"}]
    }
    mock_get.return_value = mock_response

    result = analyzer.is_ollama_available()

    assert result is True


@patch("requests.get")
def test_is_ollama_available_connection_error(mock_get, analyzer):
    """Test Ollama availability check on connection error."""
    mock_get.side_effect = Exception("Connection refused")

    result = analyzer.is_ollama_available()

    assert result is False


@patch("requests.get")
def test_is_ollama_available_model_not_found(mock_get, analyzer):
    """Test Ollama availability when model not found."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"models": [{"name": "other_model"}]}
    mock_get.return_value = mock_response

    result = analyzer.is_ollama_available()

    assert result is False
