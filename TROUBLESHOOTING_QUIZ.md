# Troubleshooting Quiz Image Errors

## Common Issues and Solutions

### Error: "Failed to fetch image" or 404/500 errors

#### 1. Check Environment Variable
Make sure `HF_QUIZ_IMAGES_REPO` is set correctly in Render:

```bash
# In Render Dashboard → Environment
HF_QUIZ_IMAGES_REPO=your-username/ai-art-quiz-images
```

**Verify:**
- No typos in the repo name
- Repository exists: https://huggingface.co/your-username/ai-art-quiz-images
- Repository is public (or `HF_TOKEN` is set for private repos)

#### 2. Check Repository Structure
Your HF repository should have:
```
your-repo/
├── AI/
│   ├── image1.jpg
│   └── ...
├── Human/
│   ├── image1.jpg
│   └── ...
└── manifest.json
```

**Verify manifest.json exists:**
- Go to: https://huggingface.co/your-username/ai-art-quiz-images/tree/main
- Check that `manifest.json` is there

#### 3. Check Render Logs
Look for these messages in Render logs:

**Success:**
```
✓ Quiz dataset loaded: 100 images from Hugging Face Hub: your-username/ai-art-quiz-images
```

**Failure:**
```
Warning: Could not load from Hugging Face Hub: ...
```

**Common errors:**
- `401 Unauthorized` → Set `HF_TOKEN` for private repos
- `404 Not Found` → Repository doesn't exist or wrong name
- `Connection timeout` → Network issue, will retry

#### 4. Test Locally First
```bash
# Set environment variable
export HF_QUIZ_IMAGES_REPO=your-username/ai-art-quiz-images

# Run app
python run_web.py

# Check logs for:
# ✓ Quiz dataset loaded: X images from Hugging Face Hub
```

#### 5. Verify Images Were Uploaded
Check your Hugging Face repository:
1. Go to https://huggingface.co/your-username/ai-art-quiz-images
2. Click "Files" tab
3. Verify `AI/` and `Human/` folders exist
4. Verify `manifest.json` exists

#### 6. Re-upload if Needed
If images are missing, re-upload:

```bash
python upload_quiz_images_to_hf.py --repo-id your-username/ai-art-quiz-images
```

---

## Debug Steps

### Step 1: Check Environment Variables
In Render logs, look for:
```
HF_QUIZ_IMAGES_REPO=your-username/ai-art-quiz-images
```

If not set, add it in Render Dashboard → Environment

### Step 2: Check Quiz Loader Initialization
Look for these log messages:
- `Found manifest with X images` ✅
- `Loaded X quiz images from Hugging Face Hub` ✅
- `Warning: Could not load from Hugging Face Hub` ❌

### Step 3: Test Image Download
The app now downloads images lazily (on-demand). Check if:
- First image request works (downloads from HF)
- Subsequent requests work (uses cache)

### Step 4: Check Image Paths
If you see errors like "Image file not found", check:
- Image paths in logs
- Whether files exist at those paths
- Cache directory permissions

---

## Quick Fixes

### Fix 1: Re-upload Images
```bash
# Make sure you're logged in
huggingface-cli login

# Re-upload
python upload_quiz_images_to_hf.py --repo-id your-username/ai-art-quiz-images --num-samples 50
```

### Fix 2: Check Repository Type
Make sure you created a **Dataset** repository, not a Model repository:
- ✅ https://huggingface.co/datasets/your-username/ai-art-quiz-images
- ❌ https://huggingface.co/your-username/ai-art-quiz-images (Model)

### Fix 3: Verify Manifest
Check `manifest.json` structure:
```json
{
  "images": [
    {"path": "AI/image1.jpg", "label": "AI"},
    {"path": "Human/image1.jpg", "label": "Human"}
  ],
  "total": 100,
  "ai_count": 50,
  "human_count": 50
}
```

### Fix 4: Private Repository
If using private repo:
1. Set `HF_TOKEN` in Render environment
2. Token needs **read** access
3. Get token from: https://huggingface.co/settings/tokens

---

## Still Not Working?

1. **Check Render logs** for detailed error messages
2. **Test locally** with the same environment variable
3. **Verify repository** exists and is accessible
4. **Re-upload images** if needed
5. **Check network** - Render might have firewall issues

---

## Alternative: Use Local Samples

If Hugging Face continues to have issues, use local samples:

```bash
# Create quiz_samples directory
mkdir -p quiz_samples/AI quiz_samples/Human

# Copy some images
cp data/val/AI/*.jpg quiz_samples/AI/ | head -20
cp data/val/Human/*.jpg quiz_samples/Human/ | head -20

# Commit to git
git add quiz_samples/
git commit -m "Add quiz sample images"
git push
```

Then remove `HF_QUIZ_IMAGES_REPO` from environment variables.

---

## Need More Help?

Check the logs for:
- Exact error messages
- Stack traces
- Which step failed (manifest download, image download, etc.)

Share the error message and I can help debug further!

