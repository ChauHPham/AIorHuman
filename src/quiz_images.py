"""
Quiz images loader - downloads sample images from Hugging Face Hub for quiz
Since the full dataset is too large, we use a small sample of images for the quiz
"""
import os
import random
from pathlib import Path
from huggingface_hub import hf_hub_download
import logging
from PIL import Image
import io

logger = logging.getLogger(__name__)

# Default Hugging Face repository for quiz images
DEFAULT_QUIZ_IMAGES_REPO = os.environ.get('HF_QUIZ_IMAGES_REPO', None)
HF_TOKEN = os.environ.get('HF_TOKEN', None)

class QuizImageLoader:
    """
    Loads quiz images from Hugging Face Hub or local directory
    Falls back to a small set of sample images if dataset not available
    """
    def __init__(self, hf_repo_id=None, local_data_dir='data'):
        self.hf_repo_id = hf_repo_id or DEFAULT_QUIZ_IMAGES_REPO
        self.local_data_dir = local_data_dir
        self.images = []
        self.image_labels = []
        self.load_images()
    
    def load_images(self):
        """Load images from local directory or Hugging Face"""
        # Try local first
        local_images = self._load_local_images()
        if local_images:
            self.images = local_images['images']
            self.image_labels = local_images['labels']
            logger.info(f"Loaded {len(self.images)} quiz images from local directory")
            return
        
        # Try Hugging Face if repo is configured
        if self.hf_repo_id:
            hf_images = self._load_hf_images()
            if hf_images:
                self.images = hf_images['images']
                self.image_labels = hf_images['labels']
                logger.info(f"Loaded {len(self.images)} quiz images from Hugging Face")
                return
        
        # Fallback: create placeholder images
        logger.warning("No quiz images available. Quiz will not work properly.")
        logger.warning("Please either:")
        logger.warning("  1. Upload quiz images to Hugging Face Hub")
        logger.warning("  2. Or ensure data/val/ directory exists locally")
        self.images = []
        self.image_labels = []
    
    def _load_local_images(self):
        """Load images from local data/val directory"""
        val_dir = os.path.join(self.local_data_dir, 'val')
        if not os.path.exists(val_dir):
            return None
        
        images = []
        labels = []
        
        for class_name in ['AI', 'Human']:
            class_dir = os.path.join(val_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
            
            # Get up to 50 random images per class (to keep memory reasonable)
            image_files = [
                f for f in os.listdir(class_dir)
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
            ]
            
            # Sample up to 50 images per class
            sample_size = min(50, len(image_files))
            sampled_files = random.sample(image_files, sample_size) if image_files else []
            
            for filename in sampled_files:
                image_path = os.path.join(class_dir, filename)
                images.append(image_path)
                labels.append(class_name)
        
        if images:
            return {'images': images, 'labels': labels}
        return None
    
    def _load_hf_images(self):
        """Load images from Hugging Face Hub"""
        # This would require a specific structure on HF
        # For now, return None - you'd need to upload images in a specific format
        # TODO: Implement HF image loading if needed
        return None
    
    def get_random_image(self):
        """Get a random image and its label"""
        if not self.images:
            return None, None
        
        idx = random.randint(0, len(self.images) - 1)
        return self.images[idx], self.image_labels[idx]
    
    def get_image_by_id(self, image_id):
        """Get image by ID"""
        if image_id < 0 or image_id >= len(self.images):
            return None, None
        return self.images[image_id], self.image_labels[image_id]
    
    def __len__(self):
        return len(self.images)

