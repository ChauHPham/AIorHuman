#!/usr/bin/env python3
"""
Script to upload quiz images to Hugging Face Hub

Usage:
    python upload_quiz_images_to_hf.py --repo-id your-username/ai-art-quiz-images --data-dir data/val

This will:
1. Sample images from data/val/AI/ and data/val/Human/
2. Upload them to Hugging Face Hub
3. Create a manifest file for easy loading
"""
import argparse
import os
import json
import random
from pathlib import Path
from huggingface_hub import HfApi, upload_file, create_repo
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_quiz_images(repo_id, data_dir='data/val', num_samples_per_class=50, repo_type='dataset'):
    """
    Upload quiz images to Hugging Face Hub
    
    Args:
        repo_id: Hugging Face repository ID (e.g., 'username/ai-art-quiz-images')
        data_dir: Directory containing AI/ and Human/ subdirectories
        num_samples_per_class: Number of images to upload per class
        repo_type: 'dataset' or 'model' (dataset is better for this)
    """
    ai_dir = os.path.join(data_dir, 'AI')
    human_dir = os.path.join(data_dir, 'Human')
    
    # Check directories exist
    if not os.path.exists(ai_dir):
        raise FileNotFoundError(f"AI directory not found: {ai_dir}")
    if not os.path.exists(human_dir):
        raise FileNotFoundError(f"Human directory not found: {human_dir}")
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    ai_images = [
        f for f in os.listdir(ai_dir)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    human_images = [
        f for f in os.listdir(human_dir)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    if not ai_images:
        raise ValueError(f"No AI images found in {ai_dir}")
    if not human_images:
        raise ValueError(f"No Human images found in {human_dir}")
    
    # Sample images
    num_ai = min(num_samples_per_class, len(ai_images))
    num_human = min(num_samples_per_class, len(human_images))
    
    sampled_ai = random.sample(ai_images, num_ai)
    sampled_human = random.sample(human_images, num_human)
    
    logger.info(f"Uploading {num_ai} AI images and {num_human} Human images to {repo_id}")
    
    # Initialize API
    api = HfApi()
    
    # Create repo if it doesn't exist
    try:
        create_repo(repo_id=repo_id, repo_type=repo_type, exist_ok=True)
        logger.info(f"Repository {repo_id} ready")
    except Exception as e:
        logger.warning(f"Could not create repo (might already exist): {e}")
    
    # Upload AI images
    ai_manifest = []
    for i, filename in enumerate(sampled_ai):
        src_path = os.path.join(ai_dir, filename)
        hf_path = f"AI/{filename}"
        
        try:
            upload_file(
                path_or_fileobj=src_path,
                path_in_repo=hf_path,
                repo_id=repo_id,
                repo_type=repo_type,
            )
            ai_manifest.append({
                'filename': filename,
                'path': hf_path,
                'label': 'AI'
            })
            logger.info(f"  [{i+1}/{num_ai}] Uploaded AI/{filename}")
        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
    
    # Upload Human images
    human_manifest = []
    for i, filename in enumerate(sampled_human):
        src_path = os.path.join(human_dir, filename)
        hf_path = f"Human/{filename}"
        
        try:
            upload_file(
                path_or_fileobj=src_path,
                path_in_repo=hf_path,
                repo_id=repo_id,
                repo_type=repo_type,
            )
            human_manifest.append({
                'filename': filename,
                'path': hf_path,
                'label': 'Human'
            })
            logger.info(f"  [{i+1}/{num_human}] Uploaded Human/{filename}")
        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
    
    # Create and upload manifest
    manifest = {
        'images': ai_manifest + human_manifest,
        'total': len(ai_manifest) + len(human_manifest),
        'ai_count': len(ai_manifest),
        'human_count': len(human_manifest)
    }
    
    manifest_json = json.dumps(manifest, indent=2)
    manifest_path = 'manifest.json'
    
    # Save manifest locally first
    with open(manifest_path, 'w') as f:
        f.write(manifest_json)
    
    # Upload manifest
    try:
        upload_file(
            path_or_fileobj=manifest_path,
            path_in_repo='manifest.json',
            repo_id=repo_id,
            repo_type=repo_type,
        )
        logger.info("✓ Uploaded manifest.json")
    except Exception as e:
        logger.error(f"Failed to upload manifest: {e}")
    
    # Clean up local manifest
    if os.path.exists(manifest_path):
        os.remove(manifest_path)
    
    logger.info(f"\n✅ Successfully uploaded quiz images to {repo_id}")
    logger.info(f"   Total images: {manifest['total']}")
    logger.info(f"   AI images: {manifest['ai_count']}")
    logger.info(f"   Human images: {manifest['human_count']}")
    logger.info(f"\n📝 Next steps:")
    logger.info(f"   1. Set environment variable: HF_QUIZ_IMAGES_REPO={repo_id}")
    logger.info(f"   2. Redeploy your app")
    logger.info(f"   3. Images will download automatically on first request")

def main():
    parser = argparse.ArgumentParser(description='Upload quiz images to Hugging Face Hub')
    parser.add_argument(
        '--repo-id',
        type=str,
        required=True,
        help='Hugging Face repository ID (e.g., your-username/ai-art-quiz-images)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/val',
        help='Directory containing AI/ and Human/ subdirectories (default: data/val)'
    )
    parser.add_argument(
        '--num-samples',
        type=int,
        default=50,
        help='Number of images per class to upload (default: 50)'
    )
    parser.add_argument(
        '--repo-type',
        type=str,
        default='dataset',
        choices=['dataset', 'model'],
        help='Repository type (default: dataset)'
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
    
    upload_quiz_images(
        repo_id=args.repo_id,
        data_dir=args.data_dir,
        num_samples_per_class=args.num_samples,
        repo_type=args.repo_type
    )

if __name__ == '__main__':
    main()

