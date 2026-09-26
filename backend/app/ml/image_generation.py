"""Image Generation Module - Stable Diffusion wrapper for campaign posters.

This module provides OOP-based image generation using Stable Diffusion XL
for Indian e-commerce campaign posters.

Classes:
    ImageConfig: Configuration for image generation
    PosterGenerator: Main image generation class
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ImageConfig:
    """Configuration for image generation."""
    
    device: str = "cuda"
    height: int = 768
    width: int = 768
    num_inference_steps: int = 50
    guidance_scale: float = 7.5
    model_name: str = "stabilityai/stable-diffusion-xl-base-1.0"


class PosterGenerator:
    """Generate campaign posters using Stable Diffusion XL.
    
    Provides OOP interface for generating Indian e-commerce
    campaign posters with regional customization.
    
    Attributes:
        config: ImageConfig instance
        pipeline: Loaded diffusion model (optional)
        output_dir: Directory for saving generated images
    """
    
    CATEGORIES = {
        'apparel': 'vibrant colorful fabric clothing store display',
        'electronics': 'modern sleek electronics showroom',
        'home_textiles': 'cozy home interior with beautiful fabrics',
        'kitchenware': 'modern kitchen with shiny utensils',
        'footwear': 'stylish shoe store display',
        'beauty': 'luxurious beauty and cosmetics store',
        'books': 'cozy library with neatly arranged books',
        'toys': 'colorful toy store display',
        'sports': 'modern sports equipment store',
        'mobile_accessories': 'high-tech mobile accessories store'
    }
    
    REGIONS = {
        'Tamil Nadu': 'South Indian traditional elements, vibrant colors',
        'Kerala': 'tropical elements, coconut palms, backwater scenes',
        'Bihar': 'festival colors, traditional Indian patterns',
        'Uttar Pradesh': 'North Indian architecture, traditional marketplace',
        'Maharashtra': 'cosmopolitan urban style, modern marketplace',
        'West Bengal': 'Bengali cultural elements, artistic design',
        'Rajasthan': 'desert landscape, traditional textile patterns',
        'Gujarat': 'colorful ethnic patterns, trade marketplace',
        'Punjab': 'harvest festival themes, golden wheat fields',
        'Karnataka': 'tech city modern style, coffee plantation elements'
    }
    
    def __init__(
        self,
        config: Optional[ImageConfig] = None,
        output_dir: Optional[Path | str] = None
    ):
        """Initialize PosterGenerator.
        
        Args:
            config: Optional ImageConfig (uses defaults if None)
            output_dir: Directory for saving images
        """
        self.config = config or ImageConfig()
        self.output_dir = (
            Path(output_dir) if output_dir
            else Path.home() / ".cache" / "twinai_posters"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.pipeline = None
        self._check_diffusers_availability()
        
        logger.info(
            f"PosterGenerator initialized | Device: {self.config.device} | "
            f"Output: {self.output_dir}"
        )
    
    def _check_diffusers_availability(self) -> None:
        """Check if diffusers library is available."""
        try:
            import torch
            from PIL import Image
            from diffusers import StableDiffusionXLPipeline
            self.DIFFUSERS_AVAILABLE = True
            logger.debug("Diffusers available")
        except ImportError:
            self.DIFFUSERS_AVAILABLE = False
            logger.warning(
                "Diffusers not installed. Install with: pip install -r requirements_ml.txt"
            )
    
    def load_model(self) -> None:
        """Load Stable Diffusion XL model.
        
        Raises:
            RuntimeError: If diffusers not available
        """
        if not self.DIFFUSERS_AVAILABLE:
            raise RuntimeError(
                "Diffusers not installed. Install with: pip install -r requirements_ml.txt"
            )
        
        logger.info("Loading Stable Diffusion XL model...")
        try:
            import torch
            from diffusers import StableDiffusionXLPipeline
            
            dtype = torch.float16 if self.config.device == "cuda" else torch.float32
            
            self.pipeline = StableDiffusionXLPipeline.from_pretrained(
                self.config.model_name,
                torch_dtype=dtype,
                use_safetensors=True,
                variant="fp16" if self.config.device == "cuda" else None
            )
            self.pipeline = self.pipeline.to(self.config.device)
            
            if self.config.device == "cuda":
                self.pipeline.enable_attention_slicing()
                self.pipeline.enable_vae_tiling()
            
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise RuntimeError(f"Model loading failed: {e}")
    
    def _build_prompt(
        self,
        campaign_name: str,
        category: str,
        region: str
    ) -> Tuple[str, str]:
        """Build prompt and negative prompt for image generation.
        
        Args:
            campaign_name: Campaign name
            category: Product category
            region: Target region
            
        Returns:
            Tuple of (prompt, negative_prompt)
        """
        category_desc = self.CATEGORIES.get(
            category, 'retail product display'
        )
        region_style = self.REGIONS.get(
            region, 'Indian marketplace style'
        )
        
        prompt = (
            f"Professional product photo for {campaign_name} campaign, "
            f"{category_desc}, {region_style}, "
            f"vibrant colors, high quality photography, 8k resolution"
        )
        
        negative_prompt = (
            "text, watermark, low quality, blurry, distorted, "
            "unrealistic, cartoon, anime, ugly"
        )
        
        return prompt, negative_prompt
    
    def generate_poster(
        self,
        campaign_name: str,
        category: str,
        region: str,
        discount_pct: int = 20
    ) -> 'PIL.Image':
        """Generate campaign poster.
        
        Args:
            campaign_name: Campaign name
            category: Product category
            region: Target region
            discount_pct: Discount percentage for overlay
            
        Returns:
            PIL Image object
            
        Raises:
            ValueError: If category/region invalid
            RuntimeError: If model not loaded
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category: {category}")
        
        if region not in self.REGIONS:
            logger.warning(f"Unknown region: {region}. Using default.")
        
        if self.pipeline is None:
            self.load_model()
        
        logger.info(
            f"Generating poster: {campaign_name} | {category} | {region}"
        )
        
        prompt, negative_prompt = self._build_prompt(
            campaign_name, category, region
        )
        
        try:
            import torch
            
            with torch.no_grad():
                image = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    height=self.config.height,
                    width=self.config.width,
                    num_inference_steps=self.config.num_inference_steps,
                    guidance_scale=self.config.guidance_scale
                ).images[0]
            
            # Add overlay text
            image = self._add_text_overlay(image, campaign_name, discount_pct)
            
            logger.info("Poster generation complete")
            return image
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise RuntimeError(f"Image generation failed: {e}")
    
    def _add_text_overlay(
        self,
        image: 'PIL.Image',
        campaign_name: str,
        discount_pct: int
    ) -> 'PIL.Image':
        """Add text overlay to generated image.
        
        Args:
            image: PIL Image
            campaign_name: Campaign text
            discount_pct: Discount text
            
        Returns:
            Image with text overlay
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            logger.warning("PIL not available. Skipping text overlay.")
            return image
        
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        try:
            title_font = ImageFont.truetype("arial.ttf", 60)
            discount_font = ImageFont.truetype("arial.ttf", 80)
        except (OSError, IOError):
            logger.debug("Using default font for overlay")
            title_font = ImageFont.load_default()
            discount_font = title_font
        
        width, height = img_copy.size
        
        # Add semi-transparent background
        try:
            overlay = Image.new("RGBA", img_copy.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(
                [(0, height - 250), (width, height)],
                fill=(0, 0, 0, 180)
            )
            img_copy = Image.alpha_composite(
                img_copy.convert("RGBA"), overlay
            ).convert("RGB")
        except Exception as e:
            logger.debug(f"Overlay creation failed: {e}")
        
        draw = ImageDraw.Draw(img_copy)
        
        # Add discount text
        discount_text = f"{discount_pct}% OFF"
        draw.text(
            (width // 2, height - 200),
            discount_text,
            fill=(255, 0, 0),
            font=discount_font,
            anchor="mm"
        )
        
        # Add campaign text
        draw.text(
            (width // 2, height - 80),
            campaign_name,
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm"
        )
        
        return img_copy
    
    def save_image(
        self,
        image: 'PIL.Image',
        filename: str,
        quality: int = 95
    ) -> Path:
        """Save generated image.
        
        Args:
            image: PIL Image object
            filename: Output filename
            quality: JPEG quality (1-100)
            
        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename
        image.save(output_path, "JPEG", quality=quality)
        logger.info(f"Image saved: {output_path}")
        return output_path
    
    def cleanup_memory(self) -> None:
        """Clean up model from memory."""
        if self.pipeline is not None:
            del self.pipeline
            self.pipeline = None
            
            try:
                import torch
                if self.config.device == "cuda":
                    torch.cuda.empty_cache()
            except Exception:
                pass
            
            logger.info("Memory cleaned")


# Type hints for IDE support
try:
    from PIL import Image
    Tuple = tuple
except ImportError:
    pass
