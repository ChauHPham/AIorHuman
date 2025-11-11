#!/usr/bin/env python3
"""
Script to upload the model to Hugging Face Hub

Usage:
    python upload_model_to_hf.py --repo-id your-username/ai-art-detector --model-path models/detector.pth

You'll need to:
1. Install: pip install huggingface_hub
2. Login: huggingface-cli login
3. Create a repository on https://huggingface.co/new
4. Run this script
"""
import argparse
import os
from pathlib import Path
from huggingface_hub import HfApi, upload_file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_model(repo_id, model_path, filename=None):
    """
    Upload model to Hugging Face Hub
    
    Args:
        repo_id (str): Repository ID (e.g., 'username/repo-name')
        model_path (str): Path to the model file
        filename (str): Filename in the repo (defaults to basename of model_path)
    """
    if filename is None:
        filename = os.path.basename(model_path)
    
    # Check if file exists
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    file_size = os.path.getsize(model_path) / (1024 * 1024)  # Size in MB
    logger.info(f"Uploading {model_path} ({file_size:.2f} MB) to {repo_id}/{filename}")
    
    # Initialize API
    api = HfApi()
    
    # Upload file
    try:
        upload_file(
            path_or_fileobj=model_path,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="model",
        )
        logger.info(f"✓ Successfully uploaded {filename} to {repo_id}")
        logger.info(f"  Model is now available at: https://huggingface.co/{repo_id}")
    except Exception as e:
        logger.error(f"✗ Failed to upload model: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Upload model to Hugging Face Hub')
    parser.add_argument(
        '--repo-id',
        type=str,
        required=True,
        help='Hugging Face repository ID (e.g., your-username/ai-art-detector)'
    )
    parser.add_argument(
        '--model-path',
        type=str,
        default='models/detector.pth',
        help='Path to the model file (default: models/detector.pth)'
    )
    parser.add_argument(
        '--filename',
        type=str,
        default=None,
        help='Filename in the repo (defaults to basename of model_path)'
    )
    
    args = parser.parse_args()
    
    # Check if logged in
    try:
        from huggingface_hub import whoami
        user = whoami()
        logger.info(f"Logged in as: {user.get('name', 'unknown')}")
    except Exception:
        logger.error("Not logged in to Hugging Face. Run: huggingface-cli login")
        return
    
    upload_model(args.repo_id, args.model_path, args.filename)

if __name__ == '__main__':
    main()

