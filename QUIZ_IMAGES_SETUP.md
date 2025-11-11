# Quiz Images Setup Guide

## Problem
The quiz needs images to work, but the full `data/` folder is too large to commit to git (excluded in `.gitignore`). On Render, the quiz fails because images don't exist.

## Solution
Create a small sample dataset (`quiz_samples/`) with 10-20 images per class that can be committed to git.

---

## Quick Setup

### Step 1: Create Directory Structure
```bash
mkdir -p quiz_samples/AI
mkdir -p quiz_samples/Human
```

### Step 2: Copy Sample Images
Copy 10-20 images from your validation set to the sample directories:

```bash
# Copy some AI images
cp data/val/AI/*.jpg quiz_samples/AI/ | head -15

# Copy some Human images  
cp data/val/Human/*.jpg quiz_samples/Human/ | head -15
```

Or manually select diverse images and copy them.

### Step 3: Verify Structure
```
quiz_samples/
├── AI/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── Human/
    ├── image1.jpg
    ├── image2.jpg
    └── ...
```

### Step 4: Commit to Git
```bash
git add quiz_samples/
git commit -m "Add quiz sample images"
git push
```

---

## How It Works

1. **Local Development**: 
   - Uses `quiz_samples/` if available
   - Falls back to `data/val/` if sample doesn't exist

2. **Production (Render)**:
   - Uses `quiz_samples/` (committed to git)
   - Quiz works with the sample images

---

## Image Selection Tips

- **Diversity**: Choose images that represent different styles
- **Quality**: Use clear, representative images
- **Balance**: Equal number of AI and Human images
- **Size**: 10-20 images per class is enough for a good quiz

---

## Alternative: Host on Hugging Face

If you prefer not to commit images, you can host them on Hugging Face Hub:

1. Upload images to a Hugging Face dataset repository
2. Set `HF_QUIZ_IMAGES_REPO` environment variable
3. Images will be downloaded at runtime

(Note: This requires additional code changes - see `src/quiz_images.py` for reference)

---

## Troubleshooting

**Quiz still not working?**
- Check `quiz_samples/` directory exists
- Verify it has `AI/` and `Human/` subdirectories
- Ensure images are in supported formats (jpg, png, gif)
- Check Render logs for errors

**Not enough images?**
- Add more images to `quiz_samples/` directories
- Commit and redeploy

---

## File Size

- 20 images × ~100KB each = ~2MB total
- This is small enough to commit to git
- Much better than the full dataset (~GB)

---

That's it! Once you create `quiz_samples/` and commit it, the quiz will work on Render! 🎉

