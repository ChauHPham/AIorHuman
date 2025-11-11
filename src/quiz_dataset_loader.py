"""
Quiz dataset loader - handles loading quiz images for production
Supports loading from Hugging Face Hub or local directories
"""
import os
import random
import json
import tempfile
from pathlib import Path
import logging
from huggingface_hub import hf_hub_download, list_repo_files

logger = logging.getLogger(__name__)

# Hugging Face token for private repos
HF_TOKEN = os.environ.get('HF_TOKEN', None)

class QuizDatasetLoader:
    """
    Loads quiz images from Hugging Face Hub or local directories
    Priority: HF Hub > local sample directory > full dataset
    """
    def __init__(self, sample_data_dir='quiz_samples', full_data_dir='data', hf_repo_id=None):
        self.sample_data_dir = sample_data_dir
        self.full_data_dir = full_data_dir
        self.hf_repo_id = hf_repo_id or os.environ.get('HF_QUIZ_IMAGES_REPO', None)
        self.samples = []
        self.class_names = ['AI', 'Human']
        self.cache_dir = None
        self.load_samples()
    
    def load_samples(self):
        """Load samples with priority: HF Hub > local sample > full dataset"""
        # Try Hugging Face Hub first (for production)
        if self.hf_repo_id:
            samples = self._load_from_hf()
            if samples:
                self.samples = samples
                logger.info(f"Loaded {len(self.samples)} quiz images from Hugging Face Hub: {self.hf_repo_id}")
                return
        
        # Try local sample directory (small, can be committed to git)
        samples = self._load_from_dir(self.sample_data_dir)
        if samples:
            self.samples = samples
            logger.info(f"Loaded {len(self.samples)} quiz images from sample directory")
            return
        
        # Fallback to full dataset if available (for local development)
        samples = self._load_from_dir(os.path.join(self.full_data_dir, 'val'))
        if samples:
            self.samples = samples
            logger.info(f"Loaded {len(self.samples)} quiz images from full dataset")
            return
        
        # No images available
        logger.warning("No quiz images available. Quiz will not work.")
        logger.warning("Options to fix:")
        logger.warning("  1. Upload images to Hugging Face Hub and set HF_QUIZ_IMAGES_REPO")
        logger.warning("  2. Create quiz_samples/ directory with AI/ and Human/ subdirectories")
        self.samples = []
    
    def _load_from_hf(self):
        """Load images from Hugging Face Hub"""
        try:
            # Download manifest first
            manifest_path = hf_hub_download(
                repo_id=self.hf_repo_id,
                filename='manifest.json',
                repo_type='dataset',
                token=HF_TOKEN
            )
            
            # Read manifest
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            
            logger.info(f"Found manifest with {manifest.get('total', 0)} images")
            
            # Download images and create samples
            samples = []
            cache_base = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'hub', 'datasets')
            
            for img_info in manifest.get('images', []):
                hf_path = img_info['path']
                label = img_info['label']
                
                try:
                    # Download image
                    img_path = hf_hub_download(
                        repo_id=self.hf_repo_id,
                        filename=hf_path,
                        repo_type='dataset',
                        token=HF_TOKEN
                    )
                    
                    class_idx = self.class_names.index(label)
                    samples.append((img_path, class_idx))
                except Exception as e:
                    logger.warning(f"Could not download {hf_path}: {e}")
                    continue
            
            if samples:
                return samples
        except Exception as e:
            logger.warning(f"Could not load from Hugging Face Hub: {e}")
            logger.warning(f"  Repo: {self.hf_repo_id}")
            logger.warning(f"  Falling back to local directories...")
        
        return None
    
    def _load_from_dir(self, base_dir):
        """Load images from directory structure"""
        if not os.path.exists(base_dir):
            return None
        
        samples = []
        
        for class_name in self.class_names:
            class_dir = os.path.join(base_dir, class_name)
            if not os.path.isdir(class_dir):
                continue
            
            # Get all image files
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
            for filename in os.listdir(class_dir):
                file_path = os.path.join(class_dir, filename)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(filename)[1].lower()
                    if ext in image_extensions:
                        class_idx = self.class_names.index(class_name)
                        samples.append((file_path, class_idx))
        
        return samples if samples else None
    
    def get_random_sample(self):
        """Get a random sample"""
        if not self.samples:
            return None, None
        idx = random.randint(0, len(self.samples) - 1)
        return idx, self.samples[idx]
    
    def get_sample(self, idx):
        """Get sample by index"""
        if idx < 0 or idx >= len(self.samples):
            return None
        return self.samples[idx]
    
    def __len__(self):
        return len(self.samples)

