"""AI-powered image analysis using Ollama/Qwen2.5-VL for SEO optimization."""

import base64
import json
import time
from pathlib import Path
from typing import Optional, Dict, List
import requests

from .config import config
from .logger import logger


class AIImageAnalyzer:
    """AI-powered image analyzer using Ollama/Qwen2.5-VL."""

    def __init__(self):
        """Initialize AI analyzer with Ollama configuration."""
        self.ollama_config = config.ollama
        self.endpoint = self.ollama_config.get(
            "endpoint", "http://localhost:11434/api/generate"
        )
        self.model = self.ollama_config.get(
            "model", "qwen2.5vl:7b"
        )  # UPGRADED from llava:latest - much better accuracy!
        self.timeout = self.ollama_config.get(
            "timeout", 45
        )  # Increased for better results
        self.max_retries = self.ollama_config.get("max_retries", 3)
        self.retry_delay = self.ollama_config.get("retry_delay", 2)

        # SEO configuration
        self.seo_config = config.seo
        self.keyword_count = self.seo_config.get("keyword_count", 8)

    def is_ollama_available(self) -> bool:
        """Check if Ollama service is running and model is available."""
        try:
            # Check if Ollama is running
            health_response = requests.get(
                self.endpoint.replace("/api/generate", "/api/tags"), timeout=5
            )

            if health_response.status_code != 200:
                return False

            # Check if our model is available
            models = health_response.json().get("models", [])
            model_names = [model.get("name", "") for model in models]

            # Check if exact model or base model exists
            target_model = self.model.split(":")[0]  # Remove tag if present
            available = any(target_model in name for name in model_names)

            if not available:
                logger.warning(
                    f"Model '{self.model}' not found. Available models: {model_names}"
                )
                return False

            logger.debug(f"Ollama service available with model '{self.model}'")
            return True

        except requests.exceptions.RequestException as e:
            logger.warning(f"Ollama service not available: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking Ollama availability: {e}")
            return False

    def encode_image_base64(self, image_path: Path) -> Optional[str]:
        """Encode image file to base64 string."""
        try:
            with open(image_path, "rb") as image_file:
                encoded = base64.b64encode(image_file.read()).decode("utf-8")
                logger.debug(
                    f"Encoded image {image_path} to base64 ({len(encoded)} chars)"
                )
                return encoded
        except Exception as e:
            logger.error(f"Failed to encode image {image_path}: {e}")
            return None

    def generate_seo_description(self, image_path: Path) -> Optional[str]:
        """Generate SEO-optimized description for image using Qwen2.5-VL."""
        if not self.is_ollama_available():
            logger.error("Ollama service not available")
            return None

        # Encode image
        image_b64 = self.encode_image_base64(image_path)
        if not image_b64:
            return None

        # Create prompt for SEO keywords
        prompt = self._create_seo_prompt()

        # Build request payload
        payload = {
            "model": self.model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {
                "temperature": 0.2,  # Qwen2.5-VL works better with slightly higher temp for creative keywords
                "top_p": 0.95,  # Increased for more diverse, specific keywords
                "top_k": 50,  # Increased diversity for better SEO terms
            },
        }

        # Make API call with retries
        response_text = self._call_ollama_api(payload, image_path)

        if response_text:
            # Clean and validate response
            keywords = self._process_seo_response(response_text)
            logger.info(f"Generated SEO keywords for {image_path.name}: {keywords}")
            return keywords

        return None

    def _create_seo_prompt(self) -> str:
        """Create optimized prompt for SEO keyword generation."""
        return f"""Analyze this image and generate exactly {self.keyword_count} SEO-optimized keywords that describe what you see.

REQUIREMENTS:
- Use only descriptive, searchable terms
- Include objects, people, actions, setting, mood, colors
- Make keywords specific and relevant
- Use lowercase letters only
- Separate keywords with hyphens
- No articles (a, an, the), prepositions (in, on, at), or stop words
- Focus on nouns, adjectives, and action verbs

EXAMPLES:
- For a family photo: "happy-family-walking-beach-sunset-vacation-children-parents"
- For a business meeting: "professional-meeting-office-team-discussion-laptop-conference-business"
- For food: "delicious-chocolate-cake-dessert-birthday-celebration-sweet-homemade"

Your response must ONLY contain the {self.keyword_count} keywords separated by hyphens, nothing else."""

    def _call_ollama_api(self, payload: Dict, image_path: Path) -> Optional[str]:
        """Make API call to Ollama with retry logic."""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    f"Calling Ollama API (attempt {attempt}/{self.max_retries}) for {image_path.name}"
                )

                response = requests.post(
                    self.endpoint,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"},
                )

                if response.status_code == 200:
                    response_data = response.json()
                    response_text = response_data.get("response", "").strip()

                    if response_text:
                        logger.debug(f"Ollama response: {response_text}")
                        return response_text
                    else:
                        logger.warning(
                            f"Empty response from Ollama for {image_path.name}"
                        )

                else:
                    logger.warning(
                        f"Ollama API returned status {response.status_code}: {response.text}"
                    )

            except requests.exceptions.Timeout:
                logger.warning(
                    f"Timeout calling Ollama API for {image_path.name} (attempt {attempt})"
                )

            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed for {image_path.name} (attempt {attempt}): {e}"
                )

            except json.JSONDecodeError as e:
                logger.warning(
                    f"Invalid JSON response for {image_path.name} (attempt {attempt}): {e}"
                )

            except Exception as e:
                logger.error(
                    f"Unexpected error calling Ollama API for {image_path.name} (attempt {attempt}): {e}"
                )

            # Wait before retry (except on last attempt)
            if attempt < self.max_retries:
                time.sleep(self.retry_delay * attempt)  # Exponential backoff

        logger.error(
            f"Failed to get response from Ollama after {self.max_retries} attempts for {image_path.name}"
        )
        return None

    def _process_seo_response(self, response_text: str) -> str:
        """Process and clean the SEO response from Qwen2.5-VL."""
        # Clean the response
        keywords = response_text.lower().strip()

        # Remove any quotes or extra formatting
        keywords = keywords.strip("\"'`")

        # Remove any explanatory text (keep only the keywords)
        lines = keywords.split("\n")
        for line in lines:
            if "-" in line and len(line.split("-")) >= 3:  # Looks like keywords
                keywords = line.strip()
                break

        # Basic sanitization
        keywords = "".join(c if c.isalnum() or c == "-" else "-" for c in keywords)

        # Remove multiple consecutive hyphens
        while "--" in keywords:
            keywords = keywords.replace("--", "-")

        # Remove leading/trailing hyphens
        keywords = keywords.strip("-")

        # Ensure we don't exceed maximum filename length
        max_length = (
            self.seo_config.get("max_filename_length", 100) - 5
        )  # Reserve space for .webp
        if len(keywords) > max_length:
            # Truncate at word boundary
            parts = keywords.split("-")
            truncated = []
            current_length = 0

            for part in parts:
                if current_length + len(part) + 1 <= max_length:  # +1 for hyphen
                    truncated.append(part)
                    current_length += len(part) + 1
                else:
                    break

            keywords = "-".join(truncated)

        return keywords if keywords else f"image-{int(time.time())}"

    def generate_fallback_name(self, image_path: Path) -> str:
        """Generate fallback filename when AI analysis fails."""
        fallback_prefix = self.seo_config.get("fallback_prefix", "image")
        timestamp = int(time.time())

        # Try to use some characteristics of the original filename
        original_stem = image_path.stem.lower()

        # Clean original stem
        clean_stem = "".join(
            c if c.isalnum() or c == "-" else "-" for c in original_stem
        )
        clean_stem = clean_stem[:30]  # Limit length

        if clean_stem and len(clean_stem) > 2:
            return f"{fallback_prefix}-{clean_stem}-{timestamp}"
        else:
            return f"{fallback_prefix}-{timestamp}"

    def batch_analyze_images(
        self, image_paths: List[Path], progress_callback=None
    ) -> Dict[Path, Optional[str]]:
        """Analyze multiple images and return SEO descriptions."""
        results = {}
        total = len(image_paths)

        for i, image_path in enumerate(image_paths, 1):
            if progress_callback:
                progress_callback(i, total, f"Analyzing {image_path.name}")

            try:
                description = self.generate_seo_description(image_path)
                if not description:
                    description = self.generate_fallback_name(image_path)

                results[image_path] = description

            except Exception as e:
                logger.error(f"Failed to analyze {image_path}: {e}")
                results[image_path] = self.generate_fallback_name(image_path)

        return results
