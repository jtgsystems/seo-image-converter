#!/usr/bin/env python3
"""
AI-Powered Photo Sorter using Qwen2.5-VL
Analyzes and categorizes photos into intelligent folders
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_analyzer import AIImageAnalyzer
from src.logger import logger


class PhotoCategory:
    """Photo category definitions."""

    PEOPLE = "people"
    NATURE = "nature"
    OBJECTS = "objects"
    DOCUMENTS = "documents"
    ARCHITECTURE = "architecture"
    VEHICLES = "vehicles"
    FOOD = "food"
    TECHNOLOGY = "technology"
    ART = "art"
    EVENTS = "events"
    SPORTS = "sports"
    ANIMALS = "animals"
    UNCLEAR = "unclear"

    DESCRIPTIONS = {
        PEOPLE: "Photos with people, faces, portraits, groups",
        NATURE: "Landscapes, scenery, plants, natural environments",
        OBJECTS: "Items, products, tools, everyday objects",
        DOCUMENTS: "Text, papers, documents, screenshots, receipts",
        ARCHITECTURE: "Buildings, houses, structures, interiors",
        VEHICLES: "Cars, trucks, motorcycles, boats, planes",
        FOOD: "Meals, cooking, restaurants, food items, drinks",
        TECHNOLOGY: "Computers, phones, electronics, gadgets, screens",
        ART: "Artwork, drawings, paintings, sculptures, creative content",
        EVENTS: "Parties, celebrations, weddings, concerts, gatherings",
        SPORTS: "Athletic activities, games, competitions, outdoor activities",
        ANIMALS: "Pets, wildlife, birds, insects, animals",
        UNCLEAR: "Unclear, corrupted, or unidentifiable images",
    }

    @classmethod
    def all_categories(cls) -> List[str]:
        """Get list of all categories."""
        return list(cls.DESCRIPTIONS.keys())

    @classmethod
    def get_description(cls, category: str) -> str:
        """Get description for a category."""
        return cls.DESCRIPTIONS.get(category, "Unknown category")


class AIPhotoSorter:
    """AI-powered photo sorter using Qwen2.5-VL vision model."""

    def __init__(self, source_dir: Path, output_dir: Path, move_files: bool = False):
        """
        Initialize photo sorter.

        Args:
            source_dir: Source directory containing photos
            output_dir: Output directory for sorted photos
            move_files: If True, move files instead of copying
        """
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.move_files = move_files
        self.analyzer = AIImageAnalyzer()

        # Create category directories
        for category in PhotoCategory.all_categories():
            (self.output_dir / category).mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized photo sorter: {self.source_dir} → {self.output_dir}")
        logger.info(f"Mode: {'MOVE' if move_files else 'COPY'} files")

    def _create_categorization_prompt(self) -> str:
        """Create prompt for photo categorization."""
        categories_text = "\n".join(
            [
                f"- {cat}: {PhotoCategory.get_description(cat)}"
                for cat in PhotoCategory.all_categories()
            ]
        )

        return f"""Analyze this image and categorize it into ONE of these categories:

{categories_text}

IMPORTANT:
- Respond with ONLY the category name (one word, lowercase)
- Choose the MOST SPECIFIC category that fits
- If multiple categories apply, choose the primary subject
- If unclear or corrupted, choose "unclear"

Category:"""

    def categorize_image(self, image_path: Path) -> str:
        """
        Categorize a single image using AI.

        Args:
            image_path: Path to image file

        Returns:
            Category name
        """
        prompt = self._create_categorization_prompt()

        # Encode image
        image_b64 = self.analyzer.encode_image_base64(image_path)
        if not image_b64:
            logger.warning(f"Could not encode image: {image_path.name}")
            return PhotoCategory.UNCLEAR

        # Build request payload
        payload = {
            "model": self.analyzer.model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Low temperature for more consistent categorization
                "top_p": 0.9,
            },
        }

        # Get AI response
        response_text = self.analyzer._call_ollama_api(payload, image_path)

        if response_text:
            # Clean response
            category = response_text.strip().lower()

            # Validate category
            if category in PhotoCategory.all_categories():
                return category

            # Try to extract valid category from response
            for valid_cat in PhotoCategory.all_categories():
                if valid_cat in category:
                    return valid_cat

        logger.warning(f"Could not categorize {image_path.name}, marking as unclear")
        return PhotoCategory.UNCLEAR

    def process_image(self, image_path: Path) -> tuple[Path, str, bool]:
        """
        Process a single image: categorize and move/copy.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (image_path, category, success)
        """
        try:
            # Categorize
            category = self.categorize_image(image_path)

            # Determine destination
            dest_path = self.output_dir / category / image_path.name

            # Handle duplicate names
            counter = 1
            while dest_path.exists():
                stem = image_path.stem
                suffix = image_path.suffix
                dest_path = self.output_dir / category / f"{stem}_{counter}{suffix}"
                counter += 1

            # Move or copy
            if self.move_files:
                shutil.move(str(image_path), str(dest_path))
                action = "Moved"
            else:
                shutil.copy2(str(image_path), str(dest_path))
                action = "Copied"

            logger.info(f"{action} {image_path.name} → {category}/")
            return (image_path, category, True)

        except Exception as e:
            logger.error(f"Failed to process {image_path.name}: {e}")
            return (image_path, PhotoCategory.UNCLEAR, False)

    def find_images(self) -> List[Path]:
        """Find all image files in source directory."""
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
            ".heic",
        }
        image_files = []

        for ext in image_extensions:
            image_files.extend(self.source_dir.rglob(f"*{ext}"))
            image_files.extend(self.source_dir.rglob(f"*{ext.upper()}"))

        return sorted(set(image_files))

    def sort_photos(
        self, limit: Optional[int] = None, parallel: bool = True
    ) -> Dict[str, int]:
        """
        Sort all photos in source directory.

        Args:
            limit: Maximum number of images to process (None for all)
            parallel: Use parallel processing

        Returns:
            Dictionary of category counts
        """
        # Check if Ollama is available
        if not self.analyzer.is_ollama_available():
            logger.error("Ollama service not available!")
            logger.error("Please start Ollama: ollama serve")
            logger.error("And pull the model: ollama pull qwen2.5vl:7b")
            return {}

        # Find images
        image_files = self.find_images()

        if not image_files:
            logger.warning(f"No images found in {self.source_dir}")
            return {}

        total_images = len(image_files)
        if limit:
            image_files = image_files[:limit]

        logger.info(f"Found {total_images} images, processing {len(image_files)}...")

        # Process images
        results: Dict[str, int] = {}
        processed = 0
        failed = 0

        if parallel:
            # Parallel processing
            max_workers = min(4, len(image_files))  # Limit concurrent AI requests
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.process_image, img): img for img in image_files
                }

                for future in as_completed(futures):
                    img_path, category, success = future.result()
                    processed += 1

                    if success:
                        results[category] = results.get(category, 0) + 1
                    else:
                        failed += 1

                    # Progress
                    logger.info(
                        f"Progress: {processed}/{len(image_files)} ({processed * 100 // len(image_files)}%)"
                    )
        else:
            # Sequential processing
            for i, image_path in enumerate(image_files, 1):
                img_path, category, success = self.process_image(image_path)

                if success:
                    results[category] = results.get(category, 0) + 1
                else:
                    failed += 1

                logger.info(
                    f"Progress: {i}/{len(image_files)} ({i * 100 // len(image_files)}%)"
                )

        # Summary
        logger.info("=" * 60)
        logger.info("PHOTO SORTING COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total processed: {processed} images")
        logger.info(f"Successfully sorted: {processed - failed}")
        logger.info(f"Failed: {failed}")
        logger.info("")
        logger.info("Category breakdown:")
        for category in sorted(results.keys()):
            count = results[category]
            desc = PhotoCategory.get_description(category)
            logger.info(f"  {category.capitalize():15} {count:4} images - {desc}")

        return results


def main():
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-Powered Photo Sorter using Qwen2.5-VL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sort photos (copy mode)
  python photo_sorter.py /path/to/photos /path/to/sorted

  # Sort photos (move mode)
  python photo_sorter.py /path/to/photos /path/to/sorted --move

  # Sort only first 50 photos
  python photo_sorter.py /path/to/photos /path/to/sorted --limit 50

  # Sequential processing (no parallel)
  python photo_sorter.py /path/to/photos /path/to/sorted --no-parallel
        """,
    )

    parser.add_argument("source", type=Path, help="Source directory with photos")
    parser.add_argument("output", type=Path, help="Output directory for sorted photos")
    parser.add_argument(
        "--move", action="store_true", help="Move files instead of copying"
    )
    parser.add_argument("--limit", type=int, help="Maximum number of images to process")
    parser.add_argument(
        "--no-parallel", action="store_true", help="Disable parallel processing"
    )

    args = parser.parse_args()

    # Validate paths
    if not args.source.exists():
        logger.error(f"Source directory does not exist: {args.source}")
        sys.exit(1)

    if not args.source.is_dir():
        logger.error(f"Source path is not a directory: {args.source}")
        sys.exit(1)

    # Create sorter
    sorter = AIPhotoSorter(
        source_dir=args.source, output_dir=args.output, move_files=args.move
    )

    # Sort photos
    sorter.sort_photos(limit=args.limit, parallel=not args.no_parallel)


if __name__ == "__main__":
    main()
