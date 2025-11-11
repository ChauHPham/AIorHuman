# Quiz Images on Hugging Face Hub - Setup Guide

## Why Hugging Face Hub?

✅ **No git size limits** - Can upload many images  
✅ **Cleaner repository** - Images not in your code repo  
✅ **Easy to update** - Just upload new images  
✅ **Automatic caching** - Images cached after first download  
✅ **Free hosting** - Hugging Face Hub is free  

---

## Quick Setup (3 Steps)

### Step 1: Create Hugging Face Dataset Repository

1. Go to https://huggingface.co/new
2. Select **"Dataset"** (not Model)
3. Repository name: `ai-art-quiz-images` (or your choice)
4. Visibility: **Public** (or Private if you prefer)
5. Click **"Create repository"**

### Step 2: Upload Images

```bash
# Install and login
pip install huggingface_hub
huggingface-cli login

# Upload images (samples 50 images per class by default)
python upload_quiz_images_to_hf.py --repo-id YOUR_USERNAME/ai-art-quiz-images
```

**Options:**
- `--num-samples 100` - Upload more images (default: 50 per class)
- `--data-dir data/val` - Source directory (default: data/val)

**Example:**
```bash
python upload_quiz_images_to_hf.py \
  --repo-id johndoe/ai-art-quiz-images \
  --num-samples 75
```

### Step 3: Configure Render

In Render dashboard → Your Service → Environment:

| Key | Value |
|-----|-------|
| `HF_QUIZ_IMAGES_REPO` | `YOUR_USERNAME/ai-art-quiz-images` |

If using a **private repository**, also add:
| Key | Value |
|-----|-------|
| `HF_TOKEN` | `hf_your_token_here` |

---

## How It Works

1. **Upload**: Images uploaded to Hugging Face Hub with manifest
2. **Download**: On first request, images download automatically
3. **Cache**: Images cached to `~/.cache/huggingface/hub/datasets/`
4. **Fast**: Subsequent requests use cached images

---

## What Gets Uploaded

The script uploads:
- `AI/` folder with AI-generated images
- `Human/` folder with human-made images  
- `manifest.json` - Index of all images

**Structure on Hugging Face:**
```
your-repo/
├── AI/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── Human/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── manifest.json
```

---

## Image Count

- **Default**: 50 images per class = 100 total
- **Recommended**: 50-100 images per class
- **Maximum**: As many as you want! (no hard limit)

More images = better quiz variety, but longer first download.

---

## Testing Locally

Test the Hugging Face download:

```bash
# Set environment variable
export HF_QUIZ_IMAGES_REPO=YOUR_USERNAME/ai-art-quiz-images

# Run app - it will download images from HF
python run_web.py
```

Check logs for:
```
✓ Quiz dataset loaded: 100 images from Hugging Face Hub: YOUR_USERNAME/ai-art-quiz-images
```

---

## Updating Images

To add more images:

1. Upload again with more samples:
   ```bash
   python upload_quiz_images_to_hf.py \
     --repo-id YOUR_USERNAME/ai-art-quiz-images \
     --num-samples 100
   ```

2. Or manually upload to Hugging Face Hub web interface

3. Images will be available immediately (no redeploy needed)

---

## Troubleshooting

**Images not downloading?**
- ✅ Check `HF_QUIZ_IMAGES_REPO` is set correctly
- ✅ Verify repository exists: https://huggingface.co/YOUR_USERNAME/ai-art-quiz-images
- ✅ Check repository is public (or `HF_TOKEN` is set for private repos)
- ✅ Check Render logs for download errors

**Slow first request?**
- ✅ Normal! Images download on first request
- ✅ Subsequent requests use cache (fast)
- ✅ Consider reducing number of images if too slow

**Private repository?**
- ✅ Set `HF_TOKEN` environment variable
- ✅ Token needs read access to repository

---

## Comparison: HF Hub vs Local Samples

| Feature | Hugging Face Hub | Local quiz_samples/ |
|---------|----------------|---------------------|
| **Size limit** | None | ~10-20MB (git limit) |
| **Number of images** | Unlimited | Limited |
| **Git repo size** | Small | Larger |
| **First download** | Slower | Instant |
| **Updates** | Easy (just upload) | Need to commit |
| **Best for** | Production | Quick testing |

**Recommendation**: Use Hugging Face Hub for production! 🚀

---

## Summary

1. ✅ Create dataset repository on Hugging Face
2. ✅ Upload images using `upload_quiz_images_to_hf.py`
3. ✅ Set `HF_QUIZ_IMAGES_REPO` in Render
4. ✅ Deploy - images download automatically!

That's it! Your quiz will work on Render with images from Hugging Face Hub! 🎉

