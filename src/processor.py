"""Main processing engine with parallel support and comprehensive workflow."""

import shutil
from pathlib import Path
from typing import List, Dict, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
from dataclasses import dataclass
import time

from .config import config
from .logger import logger
from .optimizer import ImageOptimizer
from .ai_analyzer import AIImageAnalyzer

@dataclass
class ProcessingResult:
    """Result of processing a single image."""
    input_path: Path
    output_path: Optional[Path]
    success: bool
    error: Optional[str]
    original_size: int
    optimized_size: int
    compression_ratio: float
    processing_time: float
    seo_keywords: Optional[str]

class SEOImageProcessor:
    """Main processor orchestrating the entire conversion workflow."""
    
    def __init__(self):
        """Initialize processor with components."""
        self.processing_config = config.processing
        self.optimizer = ImageOptimizer()
        self.ai_analyzer = AIImageAnalyzer()
        
        # Processing configuration
        self.max_workers = self._get_max_workers()
        self.batch_size = self.processing_config.get('batch_size', 50)
        self.backup_originals = self.processing_config.get('backup_originals', True)
        self.skip_existing = self.processing_config.get('skip_existing', False)
        self.dry_run = self.processing_config.get('dry_run', False)
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'failed': 0,
            'skipped': 0,
            'total_original_size': 0,
            'total_optimized_size': 0,
            'start_time': None,
            'end_time': None
        }
    
    def _get_max_workers(self) -> int:
        """Calculate optimal number of parallel workers."""
        configured_jobs = self.processing_config.get('parallel_jobs', 0)
        
        if configured_jobs > 0:
            return min(configured_jobs, mp.cpu_count())
        else:
            # Use 80% of available CPU cores
            return max(1, int(mp.cpu_count() * 0.8))
    
    def find_images(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Find all supported images in directory."""
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        images = []
        pattern = "**/*" if recursive else "*"
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and self.optimizer.is_supported_image(file_path):
                images.append(file_path)
        
        logger.info(f"Found {len(images)} images in {directory}")
        return sorted(images)
    
    def create_backup_directory(self, target_dir: Path) -> Optional[Path]:
        """Create backup directory for original files."""
        if not self.backup_originals:
            return None
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_dir = target_dir / f"originals_backup_{timestamp}"
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created backup directory: {backup_dir}")
            return backup_dir
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            return None
    
    def should_skip_file(self, input_path: Path, output_path: Path) -> bool:
        """Check if file should be skipped."""
        if not self.skip_existing:
            return False
        
        if output_path.exists() and output_path.stat().st_size > 0:
            logger.debug(f"Skipping existing file: {output_path}")
            return True
        
        return False
    
    def process_single_image(self, input_path: Path, output_dir: Path, 
                           backup_dir: Optional[Path] = None) -> ProcessingResult:
        """Process a single image with optimization and SEO naming."""
        start_time = time.time()
        original_size = input_path.stat().st_size
        
        try:
            # Step 1: Generate SEO-optimized filename using AI
            logger.debug(f"Analyzing image for SEO keywords: {input_path}")
            seo_keywords = self.ai_analyzer.generate_seo_description(input_path)
            
            if not seo_keywords:
                logger.warning(f"Failed to generate SEO keywords for {input_path}, using fallback")
                seo_keywords = self.ai_analyzer.generate_fallback_name(input_path)
            
            # Step 2: Determine output path
            output_format = self.optimizer.output_format
            output_filename = f"{seo_keywords}.{output_format}"
            output_path = output_dir / output_filename
            
            # Handle filename conflicts
            counter = 1
            while output_path.exists():
                base_name = f"{seo_keywords}-{counter}"
                output_filename = f"{base_name}.{output_format}"
                output_path = output_dir / output_filename
                counter += 1
            
            # Check if should skip
            if self.should_skip_file(input_path, output_path):
                return ProcessingResult(
                    input_path=input_path,
                    output_path=output_path,
                    success=True,
                    error=None,
                    original_size=original_size,
                    optimized_size=output_path.stat().st_size,
                    compression_ratio=0.0,
                    processing_time=time.time() - start_time,
                    seo_keywords=seo_keywords
                )
            
            # Step 3: Dry run check
            if self.dry_run:
                logger.info(f"[DRY RUN] Would process: {input_path} -> {output_path}")
                return ProcessingResult(
                    input_path=input_path,
                    output_path=output_path,
                    success=True,
                    error="dry_run",
                    original_size=original_size,
                    optimized_size=0,
                    compression_ratio=0.0,
                    processing_time=time.time() - start_time,
                    seo_keywords=seo_keywords
                )
            
            # Step 4: Optimize image
            logger.debug(f"Optimizing image: {input_path} -> {output_path}")
            success, optimization_result = self.optimizer.optimize_image(input_path, output_path)
            
            if not success:
                error_msg = optimization_result.get('error', 'Unknown optimization error')
                logger.error(f"Failed to optimize {input_path}: {error_msg}")
                return ProcessingResult(
                    input_path=input_path,
                    output_path=None,
                    success=False,
                    error=error_msg,
                    original_size=original_size,
                    optimized_size=0,
                    compression_ratio=0.0,
                    processing_time=time.time() - start_time,
                    seo_keywords=seo_keywords
                )
            
            optimized_size = optimization_result.get('optimized_size', 0)
            compression_ratio = optimization_result.get('compression_ratio', 0.0)
            
            # Step 5: Backup original if configured
            if backup_dir and input_path != output_path:  # Don't backup if processing in-place
                try:
                    relative_path = input_path.relative_to(output_dir.parent)
                    backup_path = backup_dir / relative_path
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    shutil.move(str(input_path), str(backup_path))
                    logger.debug(f"Backed up original: {input_path} -> {backup_path}")
                    
                except Exception as e:
                    logger.warning(f"Failed to backup {input_path}: {e}")
            
            logger.info(f"Successfully processed: {input_path.name} -> {output_path.name} "
                       f"({compression_ratio:.1f}% smaller)")
            
            return ProcessingResult(
                input_path=input_path,
                output_path=output_path,
                success=True,
                error=None,
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                processing_time=time.time() - start_time,
                seo_keywords=seo_keywords
            )
            
        except Exception as e:
            logger.error(f"Unexpected error processing {input_path}: {e}")
            return ProcessingResult(
                input_path=input_path,
                output_path=None,
                success=False,
                error=str(e),
                original_size=original_size,
                optimized_size=0,
                compression_ratio=0.0,
                processing_time=time.time() - start_time,
                seo_keywords=None
            )
    
    def process_directory(self, input_directory: Path, output_directory: Path = None,
                         progress_callback: Optional[Callable] = None) -> Dict:
        """Process all images in directory with parallel processing."""
        
        # Validate input
        if not input_directory.exists():
            raise ValueError(f"Input directory does not exist: {input_directory}")
        
        # Setup output directory
        if output_directory is None:
            output_directory = input_directory
        else:
            output_directory.mkdir(parents=True, exist_ok=True)
        
        # Find images
        image_paths = self.find_images(input_directory)
        if not image_paths:
            logger.warning(f"No supported images found in {input_directory}")
            return self._create_final_report([])
        
        # Initialize statistics
        self.stats['total_files'] = len(image_paths)
        self.stats['start_time'] = time.time()
        
        # Create backup directory
        backup_dir = self.create_backup_directory(output_directory)
        
        # Process images in parallel
        results = self._process_images_parallel(
            image_paths, output_directory, backup_dir, progress_callback
        )
        
        # Finalize statistics
        self.stats['end_time'] = time.time()
        
        return self._create_final_report(results)
    
    def _process_images_parallel(self, image_paths: List[Path], output_dir: Path,
                               backup_dir: Optional[Path], 
                               progress_callback: Optional[Callable]) -> List[ProcessingResult]:
        """Process images using parallel execution."""
        
        results = []
        completed_count = 0
        total_count = len(image_paths)
        
        # Use ThreadPoolExecutor for I/O bound operations (AI analysis, file operations)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self.process_single_image, img_path, output_dir, backup_dir): img_path
                for img_path in image_paths
            }
            
            # Process completed tasks
            for future in as_completed(future_to_path):
                img_path = future_to_path[future]
                completed_count += 1
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update statistics
                    if result.success and result.error != "dry_run":
                        self.stats['processed'] += 1
                        self.stats['total_original_size'] += result.original_size
                        self.stats['total_optimized_size'] += result.optimized_size
                    elif result.error == "dry_run":
                        self.stats['skipped'] += 1
                    else:
                        self.stats['failed'] += 1
                    
                    # Progress callback
                    if progress_callback:
                        progress_callback(completed_count, total_count, result)
                    
                    # Log progress
                    if completed_count % 10 == 0 or completed_count == total_count:
                        logger.info(f"Progress: {completed_count}/{total_count} images processed")
                
                except Exception as e:
                    logger.error(f"Task failed for {img_path}: {e}")
                    self.stats['failed'] += 1
                    
                    # Create error result
                    error_result = ProcessingResult(
                        input_path=img_path,
                        output_path=None,
                        success=False,
                        error=str(e),
                        original_size=img_path.stat().st_size if img_path.exists() else 0,
                        optimized_size=0,
                        compression_ratio=0.0,
                        processing_time=0.0,
                        seo_keywords=None
                    )
                    results.append(error_result)
        
        return results
    
    def _create_final_report(self, results: List[ProcessingResult]) -> Dict:
        """Create comprehensive processing report."""
        
        processing_time = 0
        if self.stats['start_time'] and self.stats['end_time']:
            processing_time = self.stats['end_time'] - self.stats['start_time']
        
        total_savings = self.stats['total_original_size'] - self.stats['total_optimized_size']
        overall_compression = 0.0
        if self.stats['total_original_size'] > 0:
            overall_compression = (total_savings / self.stats['total_original_size']) * 100
        
        report = {
            'summary': {
                'total_files': self.stats['total_files'],
                'processed': self.stats['processed'],
                'failed': self.stats['failed'],
                'skipped': self.stats['skipped'],
                'processing_time': processing_time,
                'average_time_per_image': processing_time / max(1, self.stats['total_files'])
            },
            'size_analysis': {
                'total_original_size': self.stats['total_original_size'],
                'total_optimized_size': self.stats['total_optimized_size'],
                'total_savings_bytes': total_savings,
                'overall_compression_ratio': overall_compression,
                'average_compression_per_image': sum(r.compression_ratio for r in results if r.success) / max(1, len([r for r in results if r.success]))
            },
            'detailed_results': [
                {
                    'input_file': str(r.input_path),
                    'output_file': str(r.output_path) if r.output_path else None,
                    'success': r.success,
                    'error': r.error,
                    'original_size': r.original_size,
                    'optimized_size': r.optimized_size,
                    'compression_ratio': r.compression_ratio,
                    'processing_time': r.processing_time,
                    'seo_keywords': r.seo_keywords
                }
                for r in results
            ]
        }
        
        return report