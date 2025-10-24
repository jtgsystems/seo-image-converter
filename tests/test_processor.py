"""Tests for main processor module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.processor import SEOImageProcessor, ProcessingResult


@pytest.fixture
def processor():
    """Create processor instance."""
    return SEOImageProcessor()


def test_processor_initialization(processor):
    """Test processor initializes correctly."""
    assert processor.optimizer is not None
    assert processor.ai_analyzer is not None
    assert processor.max_workers > 0


def test_find_images_single_dir(processor, sample_images):
    """Test finding images in directory."""
    directory = sample_images[0].parent

    images = processor.find_images(directory, recursive=False)

    assert len(images) == 3
    assert all(img.exists() for img in images)


def test_find_images_nonexistent_dir(processor):
    """Test finding images in nonexistent directory raises error."""
    with pytest.raises(ValueError, match="does not exist"):
        processor.find_images(Path("/nonexistent/directory"))


def test_find_images_file_not_dir(processor, sample_image):
    """Test finding images with file path raises error."""
    with pytest.raises(ValueError, match="not a directory"):
        processor.find_images(sample_image)


def test_create_backup_directory(processor, temp_dir):
    """Test creating backup directory."""
    backup_dir = processor.create_backup_directory(temp_dir)

    assert backup_dir is not None
    assert backup_dir.exists()
    assert backup_dir.is_dir()
    assert "originals_backup" in backup_dir.name


def test_create_backup_directory_disabled(processor, temp_dir):
    """Test that backup directory not created when disabled."""
    processor.backup_originals = False

    backup_dir = processor.create_backup_directory(temp_dir)

    assert backup_dir is None


def test_should_skip_file_when_skip_existing_enabled(processor, sample_image, temp_dir):
    """Test skip logic when file exists."""
    processor.skip_existing = True

    output_path = temp_dir / "existing.webp"
    output_path.write_text("existing file")

    assert processor.should_skip_file(sample_image, output_path) is True


def test_should_skip_file_when_skip_existing_disabled(
    processor, sample_image, temp_dir
):
    """Test skip logic when skip_existing is False."""
    processor.skip_existing = False

    output_path = temp_dir / "existing.webp"
    output_path.write_text("existing file")

    assert processor.should_skip_file(sample_image, output_path) is False


@patch.object(SEOImageProcessor, "_process_images_parallel")
def test_process_directory_calls_parallel(mock_parallel, processor, sample_images):
    """Test that process_directory calls parallel processing."""
    directory = sample_images[0].parent
    mock_parallel.return_value = []

    processor.process_directory(directory)

    mock_parallel.assert_called_once()


def test_process_directory_creates_report(processor, sample_images):
    """Test that process_directory returns report."""
    directory = sample_images[0].parent

    # Mock the processing to avoid actual image operations
    with patch.object(processor, "find_images", return_value=sample_images):
        with patch.object(
            processor, "_process_images_parallel", return_value=[]
        ) as mock_process:
            report = processor.process_directory(directory)

    assert "summary" in report
    assert "size_analysis" in report
    assert "detailed_results" in report


def test_process_single_image_dry_run(processor, sample_image, temp_dir):
    """Test processing image in dry run mode."""
    processor.dry_run = True

    result = processor.process_single_image(sample_image, temp_dir)

    assert result.success is True
    assert result.error == "dry_run"
    assert result.output_path is not None


def test_process_single_image_success(processor, sample_image, temp_dir):
    """Test successful single image processing."""
    # Mock AI analyzer on the instance
    with patch.object(
        processor.ai_analyzer,
        "generate_seo_description",
        return_value="happy-family-beach-vacation",
    ):
        # Mock optimizer on the instance
        with patch.object(
            processor.optimizer,
            "optimize_image",
            return_value=(
                True,
                {
                    "original_size": 1000,
                    "optimized_size": 500,
                    "compression_ratio": 50.0,
                    "format": "webp",
                },
            ),
        ):
            result = processor.process_single_image(sample_image, temp_dir)

    assert result.success is True
    assert result.output_path is not None
    assert result.seo_keywords == "happy-family-beach-vacation"


def test_process_single_image_fallback_naming(processor, sample_image, temp_dir):
    """Test fallback naming when AI fails."""
    # Mock AI analyzer to fail on the instance
    with patch.object(
        processor.ai_analyzer, "generate_seo_description", return_value=None
    ):
        with patch.object(
            processor.ai_analyzer,
            "generate_fallback_name",
            return_value="fallback-image-12345",
        ):
            with patch.object(
                processor.optimizer,
                "optimize_image",
                return_value=(
                    True,
                    {
                        "original_size": 1000,
                        "optimized_size": 500,
                        "compression_ratio": 50.0,
                    },
                ),
            ):
                result = processor.process_single_image(sample_image, temp_dir)

    assert result.success is True
    assert result.seo_keywords == "fallback-image-12345"


def test_process_single_image_filename_conflict(processor, sample_images, temp_dir):
    """Test handling of filename conflicts."""

    # Custom side effect to create actual file
    def create_output_file(input_path, output_path):
        output_path.write_text("test")
        return (
            True,
            {"original_size": 1000, "optimized_size": 500, "compression_ratio": 50.0},
        )

    # Mock AI to return same name on the instance
    with patch.object(
        processor.ai_analyzer, "generate_seo_description", return_value="test-keyword"
    ):
        with patch.object(
            processor.optimizer, "optimize_image", side_effect=create_output_file
        ):
            # Process first image
            result1 = processor.process_single_image(sample_images[0], temp_dir)

            # Process second image with same keywords
            result2 = processor.process_single_image(sample_images[1], temp_dir)

    # Second image should have -1 suffix
    assert result1.output_path != result2.output_path
    assert "-1" in str(result2.output_path)


def test_create_final_report_calculates_stats(processor):
    """Test that final report calculates statistics correctly."""
    results = [
        ProcessingResult(
            input_path=Path("test1.jpg"),
            output_path=Path("out1.webp"),
            success=True,
            error=None,
            original_size=1000,
            optimized_size=500,
            compression_ratio=50.0,
            processing_time=2.5,
            seo_keywords="test-keywords",
        ),
        ProcessingResult(
            input_path=Path("test2.jpg"),
            output_path=Path("out2.webp"),
            success=True,
            error=None,
            original_size=2000,
            optimized_size=1000,
            compression_ratio=50.0,
            processing_time=3.0,
            seo_keywords="test-keywords-2",
        ),
    ]

    processor.stats = {
        "total_files": 2,
        "processed": 2,
        "failed": 0,
        "skipped": 0,
        "total_original_size": 3000,
        "total_optimized_size": 1500,
        "start_time": 1000.0,
        "end_time": 1005.5,
    }

    report = processor._create_final_report(results)

    assert report["summary"]["total_files"] == 2
    assert report["summary"]["processed"] == 2
    assert report["summary"]["processing_time"] == 5.5
    assert report["size_analysis"]["overall_compression_ratio"] == 50.0
