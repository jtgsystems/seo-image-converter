"""Advanced image optimization with latest compression techniques."""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple
from PIL import Image, ImageOps
# import magic  # Optional - fallback to extension checking

from .config import config
from .logger import logger

class ImageOptimizer:
    """Advanced image optimizer with lossless compression support."""
    
    def __init__(self):
        """Initialize optimizer with configuration."""
        self.image_config = config.image
        self.supported_formats = self.image_config.get('formats', {}).get('input', [])
        self.output_format = self.image_config.get('formats', {}).get('output', 'webp')
        self.quality_settings = self.image_config.get('quality', {})
        self.optimization_settings = self.image_config.get('optimization', {})
    
    def is_supported_image(self, file_path: Path) -> bool:
        """Check if file is a supported image format."""
        if not file_path.exists():
            return False
        
        # Check file extension
        ext = file_path.suffix.lower()
        if ext not in self.supported_formats:
            return False
        
        # Verify by attempting to open with PIL
        try:
            with Image.open(file_path) as img:
                return True
        except Exception:
            return False
    
    def get_image_info(self, file_path: Path) -> Dict:
        """Get detailed image information."""
        try:
            with Image.open(file_path) as img:
                return {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'width': img.width,
                    'height': img.height,
                    'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
                    'file_size': file_path.stat().st_size
                }
        except Exception as e:
            logger.error(f"Failed to get image info for {file_path}: {e}")
            return {}
    
    def optimize_image(self, input_path: Path, output_path: Path) -> Tuple[bool, Dict]:
        """Optimize image with the best available method."""
        try:
            image_info = self.get_image_info(input_path)
            if not image_info:
                return False, {'error': 'Could not read image'}
            
            original_size = image_info['file_size']
            
            # Choose optimization method based on format and settings
            if self.output_format.lower() == 'webp':
                success = self._optimize_to_webp(input_path, output_path, image_info)
            elif self.output_format.lower() == 'png':
                success = self._optimize_to_png(input_path, output_path, image_info)
            elif self.output_format.lower() == 'jpeg':
                success = self._optimize_to_jpeg(input_path, output_path, image_info)
            else:
                return False, {'error': f'Unsupported output format: {self.output_format}'}
            
            if not success:
                return False, {'error': 'Optimization failed'}
            
            # Get optimized size
            optimized_size = output_path.stat().st_size if output_path.exists() else 0
            compression_ratio = (1 - optimized_size / original_size) * 100 if original_size > 0 else 0
            
            return True, {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': compression_ratio,
                'format': self.output_format
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize {input_path}: {e}")
            return False, {'error': str(e)}
    
    def _optimize_to_webp(self, input_path: Path, output_path: Path, image_info: Dict) -> bool:
        """Optimize image to WebP format."""
        try:
            with Image.open(input_path) as img:
                # Handle transparency
                if image_info.get('has_transparency'):
                    # Keep alpha channel for transparent images
                    save_kwargs = {
                        'format': 'WebP',
                        'quality': self.quality_settings.get('webp', 85),
                        'method': 6,  # Best compression
                        'lossless': self.optimization_settings.get('lossless', True),
                    }
                else:
                    # Convert to RGB for non-transparent images
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    save_kwargs = {
                        'format': 'WebP',
                        'quality': self.quality_settings.get('webp', 85),
                        'method': 6,
                        'optimize': True,
                    }
                
                # Resize if needed
                if self.optimization_settings.get('resize_large', False):
                    img = self._resize_if_needed(img)
                
                # Strip metadata if configured
                if self.optimization_settings.get('strip_metadata', True):
                    img = ImageOps.exif_transpose(img)
                
                # Save optimized image
                img.save(output_path, **save_kwargs)
                return True
                
        except Exception as e:
            logger.error(f"WebP optimization failed for {input_path}: {e}")
            return False
    
    def _optimize_to_png(self, input_path: Path, output_path: Path, image_info: Dict) -> bool:
        """Optimize image to PNG with Zopfli compression."""
        try:
            # First optimize with Pillow
            with Image.open(input_path) as img:
                # Resize if needed
                if self.optimization_settings.get('resize_large', False):
                    img = self._resize_if_needed(img)
                
                # Strip metadata if configured
                if self.optimization_settings.get('strip_metadata', True):
                    img = ImageOps.exif_transpose(img)
                
                # Save with high PNG compression
                img.save(output_path, 'PNG', 
                        optimize=True, 
                        compress_level=self.quality_settings.get('png_compression', 6))
            
            # Try Zopfli optimization if available
            try:
                import zopflipng
                with open(output_path, 'rb') as f:
                    original_data = f.read()
                
                optimized_data = zopflipng.optimize_png_data(original_data)
                
                if len(optimized_data) < len(original_data):
                    with open(output_path, 'wb') as f:
                        f.write(optimized_data)
                    logger.debug(f"Zopfli optimization saved {len(original_data) - len(optimized_data)} bytes")
                
            except ImportError:
                logger.debug("Zopfli not available, using standard PNG optimization")
            except Exception as e:
                logger.warning(f"Zopfli optimization failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"PNG optimization failed for {input_path}: {e}")
            return False
    
    def _optimize_to_jpeg(self, input_path: Path, output_path: Path, image_info: Dict) -> bool:
        """Optimize image to JPEG with MozJPEG if available."""
        try:
            with Image.open(input_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                
                # Resize if needed
                if self.optimization_settings.get('resize_large', False):
                    img = self._resize_if_needed(img)
                
                # Strip metadata if configured
                if self.optimization_settings.get('strip_metadata', True):
                    img = ImageOps.exif_transpose(img)
                
                # Save with high quality
                save_kwargs = {
                    'format': 'JPEG',
                    'quality': self.quality_settings.get('jpeg', 90),
                    'optimize': True,
                }
                
                if self.optimization_settings.get('progressive', True):
                    save_kwargs['progressive'] = True
                
                img.save(output_path, **save_kwargs)
            
            # Try MozJPEG optimization if available
            try:
                import mozjpeg_lossless_optimization as mozjpeg
                
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                # Use mozjpeg for lossless optimization
                if mozjpeg.optimize_jpeg(str(output_path), str(temp_path)):
                    # Replace original with optimized version if smaller
                    temp_size = Path(temp_path).stat().st_size
                    original_size = output_path.stat().st_size
                    
                    if temp_size < original_size:
                        os.replace(temp_path, output_path)
                        logger.debug(f"MozJPEG saved {original_size - temp_size} bytes")
                    else:
                        os.unlink(temp_path)
                else:
                    os.unlink(temp_path)
                    
            except ImportError:
                logger.debug("MozJPEG not available, using standard JPEG optimization")
            except Exception as e:
                logger.warning(f"MozJPEG optimization failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"JPEG optimization failed for {input_path}: {e}")
            return False
    
    def _resize_if_needed(self, img: Image.Image) -> Image.Image:
        """Resize image if it exceeds maximum dimensions."""
        max_dim = self.optimization_settings.get('max_dimension', 1920)
        
        if max(img.size) > max_dim:
            # Calculate new size maintaining aspect ratio
            ratio = max_dim / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            
            # Use high-quality resampling
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.debug(f"Resized image from {img.size} to {new_size}")
        
        return img