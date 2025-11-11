"""
Model loading utilities with Hugging Face Hub support
Downloads and caches models from Hugging Face Hub if not found locally
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download
import logging

logger = logging.getLogger(__name__)

# Default Hugging Face repository (update this with your repo)
DEFAULT_HF_REPO = os.environ.get('HF_MODEL_REPO', 'your-username/ai-art-detector')
DEFAULT_MODEL_FILENAME = 'detector.pth'

# Hugging Face token for private repos (optional)
HF_TOKEN = os.environ.get('HF_TOKEN', None)

def get_model_path(
    local_path='models/detector.pth',
    hf_repo_id=None,
    hf_filename=None,
    cache_dir=None
):
    """
    Get model path, downloading from Hugging Face Hub if not found locally.
    
    Args:
        local_path (str): Local path to check first
        hf_repo_id (str): Hugging Face repository ID (e.g., 'username/repo-name')
        hf_filename (str): Filename in the Hugging Face repo
        cache_dir (str): Directory to cache downloaded models (default: ~/.cache/huggingface)
    
    Returns:
        str: Path to the model file
    """
    # Use environment variable or default
    hf_repo_id = hf_repo_id or DEFAULT_HF_REPO
    hf_filename = hf_filename or DEFAULT_MODEL_FILENAME
    
    # Check if local file exists
    if os.path.exists(local_path):
        logger.info(f"Using local model: {local_path}")
        return local_path
    
    # If local file doesn't exist, try to download from Hugging Face
    logger.info(f"Local model not found at {local_path}")
    logger.info(f"Attempting to download from Hugging Face: {hf_repo_id}/{hf_filename}")
    
    try:
        # Download from Hugging Face Hub
        # This will cache to ~/.cache/huggingface/hub by default
        # On Render, this cache persists between deploys
        download_kwargs = {
            'repo_id': hf_repo_id,
            'filename': hf_filename,
            'cache_dir': cache_dir,
            'force_download': False,  # Use cache if available
            'resume_download': True
        }
        
        # Add token if provided (for private repos)
        if HF_TOKEN:
            download_kwargs['token'] = HF_TOKEN
        
        downloaded_path = hf_hub_download(**download_kwargs)
        
        logger.info(f"Model downloaded from Hugging Face: {downloaded_path}")
        
        # Optionally copy to local path for consistency
        # This is useful if the app expects the model at a specific location
        local_dir = os.path.dirname(local_path)
        if local_dir and not os.path.exists(local_dir):
            os.makedirs(local_dir, exist_ok=True)
        
        # Return the cached path (or copy to local_path if needed)
        return downloaded_path
        
    except Exception as e:
        logger.error(f"Failed to download model from Hugging Face: {e}")
        logger.warning(f"Falling back to local path: {local_path}")
        # Return local path even if it doesn't exist
        # The model loader will handle the error
        return local_path

def ensure_model_downloaded(
    local_path='models/detector.pth',
    hf_repo_id=None,
    hf_filename=None
):
    """
    Ensure model is downloaded. Raises error if download fails and file doesn't exist.
    
    Args:
        local_path (str): Local path to check
        hf_repo_id (str): Hugging Face repository ID
        hf_filename (str): Filename in the Hugging Face repo
    
    Returns:
        str: Path to the model file
    
    Raises:
        FileNotFoundError: If model cannot be found locally or downloaded
    """
    model_path = get_model_path(local_path, hf_repo_id, hf_filename)
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path} and could not be downloaded from Hugging Face. "
            f"Please ensure the model is uploaded to {hf_repo_id or DEFAULT_HF_REPO} "
            f"or place it at {local_path}"
        )
    
    return model_path

