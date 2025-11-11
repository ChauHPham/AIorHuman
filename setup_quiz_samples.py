#!/usr/bin/env python3
"""
Script to set up quiz sample images from validation set
Creates quiz_samples/ directory with a small sample of images for the quiz
"""
import os
import shutil
import random
from pathlib import Path

def setup_quiz_samples(num_samples_per_class=15, source_dir='data/val', target_dir='quiz_samples'):
    """
    Copy sample images from validation set to quiz_samples directory
    
    Args:
        num_samples_per_class: Number of images to copy per class
        source_dir: Source directory (data/val)
        target_dir: Target directory (quiz_samples)
    """
    # Create target directories
    target_ai = os.path.join(target_dir, 'AI')
    target_human = os.path.join(target_dir, 'Human')
    
    os.makedirs(target_ai, exist_ok=True)
    os.makedirs(target_human, exist_ok=True)
    
    # Check if source exists
    source_ai = os.path.join(source_dir, 'AI')
    source_human = os.path.join(source_dir, 'Human')
    
    if not os.path.exists(source_ai) or not os.path.exists(source_human):
        print(f"❌ Source directory not found: {source_dir}")
        print("   Please ensure data/val/AI/ and data/val/Human/ exist")
        return False
    
    # Get image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    ai_images = [
        f for f in os.listdir(source_ai)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    human_images = [
        f for f in os.listdir(source_human)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    
    if not ai_images:
        print(f"❌ No AI images found in {source_ai}")
        return False
    
    if not human_images:
        print(f"❌ No Human images found in {source_human}")
        return False
    
    # Sample images
    num_ai = min(num_samples_per_class, len(ai_images))
    num_human = min(num_samples_per_class, len(human_images))
    
    sampled_ai = random.sample(ai_images, num_ai)
    sampled_human = random.sample(human_images, num_human)
    
    # Copy images
    copied_ai = 0
    copied_human = 0
    
    for img in sampled_ai:
        src = os.path.join(source_ai, img)
        dst = os.path.join(target_ai, img)
        try:
            shutil.copy2(src, dst)
            copied_ai += 1
        except Exception as e:
            print(f"Warning: Could not copy {img}: {e}")
    
    for img in sampled_human:
        src = os.path.join(source_human, img)
        dst = os.path.join(target_human, img)
        try:
            shutil.copy2(src, dst)
            copied_human += 1
        except Exception as e:
            print(f"Warning: Could not copy {img}: {e}")
    
    print(f"✅ Quiz samples created!")
    print(f"   Copied {copied_ai} AI images to {target_ai}/")
    print(f"   Copied {copied_human} Human images to {target_human}/")
    print(f"   Total: {copied_ai + copied_human} images")
    print(f"\n📝 Next steps:")
    print(f"   1. Review the images in {target_dir}/")
    print(f"   2. git add {target_dir}/")
    print(f"   3. git commit -m 'Add quiz sample images'")
    print(f"   4. git push")
    
    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Set up quiz sample images')
    parser.add_argument('--num-samples', type=int, default=15,
                       help='Number of images per class (default: 15)')
    parser.add_argument('--source', type=str, default='data/val',
                       help='Source directory (default: data/val)')
    parser.add_argument('--target', type=str, default='quiz_samples',
                       help='Target directory (default: quiz_samples)')
    
    args = parser.parse_args()
    
    setup_quiz_samples(
        num_samples_per_class=args.num_samples,
        source_dir=args.source,
        target_dir=args.target
    )

