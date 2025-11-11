# Quick Start: Deploy to Render

## TL;DR - 5 Steps

1. **Upload model to Hugging Face:**
   ```bash
   pip install huggingface_hub
   huggingface-cli login
   python upload_model_to_hf.py --repo-id YOUR_USERNAME/ai-art-detector
   ```

2. **Set environment variable in Render:**
   - Go to your Render service → Environment
   - Add: `HF_MODEL_REPO` = `YOUR_USERNAME/ai-art-detector`

3. **Verify .gitignore excludes models:**
   ```bash
   # Should already be in .gitignore
   models/
   *.pth
   ```

4. **Push to GitHub** (without models folder)

5. **Deploy on Render** - Model will auto-download on first startup

---

## Detailed Steps

### 1. Create Hugging Face Repository

- Visit: https://huggingface.co/new
- Type: Model
- Name: `ai-art-detector` (or your choice)
- Visibility: Public (or Private if you prefer)

### 2. Upload Model

```bash
# Install and login
pip install huggingface_hub
huggingface-cli login
# Enter your token from https://huggingface.co/settings/tokens

# Upload
python upload_model_to_hf.py --repo-id YOUR_USERNAME/ai-art-detector
```

### 3. Configure Render

In Render dashboard → Your Service → Environment:

| Key | Value |
|-----|-------|
| `HF_MODEL_REPO` | `YOUR_USERNAME/ai-art-detector` |

If using a **private repository**, also add:
| Key | Value |
|-----|-------|
| `HF_TOKEN` | `hf_your_token_here` |

### 4. Deploy

- Push code to GitHub
- Render will build and deploy
- On first request, model downloads automatically
- Subsequent requests use cached model

---

## What Changed?

✅ Model file excluded from git (already done)  
✅ Added `huggingface_hub` to requirements.txt  
✅ Created `src/model_loader.py` - downloads model if not found locally  
✅ Updated `src/inference.py` - uses model loader  
✅ Created upload script - `upload_model_to_hf.py`  

The app now:
- Checks for local model first (for development)
- Downloads from Hugging Face if not found (for Render)
- Caches model on disk (fast subsequent loads)

---

## Testing Locally

The app works the same locally - it will use `models/detector.pth` if it exists, or download from Hugging Face if not.

To test the download:
```bash
# Remove local model temporarily
mv models/detector.pth models/detector.pth.backup

# Set environment variable
export HF_MODEL_REPO=YOUR_USERNAME/ai-art-detector

# Run app - it will download model
python run_web.py
```

---

## Troubleshooting

**Model not found?**
- Check `HF_MODEL_REPO` is set correctly
- Verify repo exists: https://huggingface.co/YOUR_USERNAME/ai-art-detector

**Download slow?**
- First download is ~90MB (one-time)
- Subsequent deploys use cache

**Private repo issues?**
- Set `HF_TOKEN` environment variable
- Token needs read access

---

That's it! Your app should now deploy successfully on Render. 🚀

