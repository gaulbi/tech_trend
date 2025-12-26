"""
Thumbnail image generation module.
"""
import logging
from pathlib import Path
from typing import Tuple

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from .exceptions import ThumbnailGenerationError


class ThumbnailGenerator:
    """Handles thumbnail image generation from original images."""
    
    TARGET_SIZE = (800, 420)
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize thumbnail generator.
        
        Args:
            logger: Logger instance
            
        Raises:
            ImportError: If PIL/Pillow is not available
        """
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is required for thumbnail generation. "
                "Install it with: pip install Pillow"
            )
        
        self.logger = logger
    
    def generate(
        self,
        source_path: Path,
        output_path: Path
    ) -> None:
        """
        Generate thumbnail image from source image.
        
        Args:
            source_path: Path to source image file
            output_path: Path for thumbnail output
            
        Raises:
            ThumbnailGenerationError: If generation fails
        """
        if not source_path.exists():
            raise ThumbnailGenerationError(
                f"Source image not found: {source_path}"
            )
        
        try:
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Open and process image
            with Image.open(source_path) as img:
                # Verify image is valid
                img.verify()
            
            # Reopen for processing (verify closes the file)
            with Image.open(source_path) as img:
                # Convert to RGB if necessary (handles RGBA, P, etc.)
                if img.mode not in ('RGB', 'L'):
                    if img.mode == 'RGBA':
                        # Handle transparency by creating white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[3])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif img.mode == 'L':
                    img = img.convert('RGB')
                
                # Resize maintaining aspect ratio
                thumbnail = self._resize_maintain_aspect(img)
                
                # Save thumbnail
                thumbnail.save(
                    output_path, 
                    'JPEG', 
                    quality=85, 
                    optimize=True
                )
            
            self.logger.info(
                f"Thumbnail generated: {output_path.name} "
                f"(size: {thumbnail.size[0]}x{thumbnail.size[1]})"
            )
            
        except OSError as e:
            raise ThumbnailGenerationError(
                f"Failed to read/write image file: {e}"
            )
        except Exception as e:
            raise ThumbnailGenerationError(
                f"Failed to generate thumbnail: {e}"
            )
    
    def _resize_maintain_aspect(self, img: Image.Image) -> Image.Image:
        """
        Resize image maintaining aspect ratio to fit target size.
        
        Args:
            img: PIL Image object
            
        Returns:
            Resized PIL Image object
        """
        # Get original dimensions
        orig_width, orig_height = img.size
        target_width, target_height = self.TARGET_SIZE
        
        # Calculate aspect ratios
        source_ratio = orig_width / orig_height
        target_ratio = target_width / target_height
        
        # Determine new dimensions to fit within target
        if source_ratio > target_ratio:
            # Source is wider, fit to width
            new_width = target_width
            new_height = int(new_width / source_ratio)
        else:
            # Source is taller or equal, fit to height
            new_height = target_height
            new_width = int(new_height * source_ratio)
        
        # Ensure dimensions are at least 1 pixel
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # Resize using high-quality resampling
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
