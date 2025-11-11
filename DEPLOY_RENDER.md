# Deploying to Render - Model Size Optimization Guide

This guide helps you deploy the AI Art Detector to Render by moving the large model file out of the repository.

## Problem
Render has a slug size limit (~500MB-1GB). The model file (`models/detector.pth`) is ~90MB, which can cause deployment issues when combined with dependencies.

## Solution
Host the model on Hugging Face Hub and download it at runtime. The model will be cached on Render's disk, so it only downloads once per deployment.

---

## Step-by-Step Instructions

### Step 1: Create Hugging Face Account & Repository

1. Go to https://huggingface.co/ and create an account (free)
2. Create a new model repository:
   - Go to https://huggingface.co/new
   - Select "Model"
   - Choose a name (e.g., `ai-art-detector`)
   - Set visibility (Public or Private)
   - Click "Create repository"

### Step 2: Install Hugging Face CLI and Login

```bash
pip install huggingface_hub
huggingface-cli login
```

Enter your Hugging Face token when prompted (get it from https://huggingface.co/settings/tokens)

### Step 3: Upload Your Model

```bash
python upload_model_to_hf.py --repo-id your-username/ai-art-detector --model-path models/detector.pth
```

Replace `your-username` with your Hugging Face username.

**Note:** If you want to use a private repo, you'll need to set up authentication (see Step 6).

### Step 4: Update Environment Variables

In your Render dashboard:

1. Go to your service → Environment
2. Add environment variable:
   - **Key:** `HF_MODEL_REPO`
   - **Value:** `your-username/ai-art-detector` (your actual repo ID)

### Step 5: Verify .gitignore

Make sure `models/` and `*.pth` are in `.gitignore` (they already are):

```gitignore
models/
*.pth
```

### Step 6: (Optional) Private Repository Setup

If using a private repository, add a Hugging Face token:

1. Get your token from https://huggingface.co/settings/tokens
2. In Render dashboard → Environment:
   - **Key:** `HF_TOKEN`
   - **Value:** `hf_your_token_here`

The code will automatically use this token if set.

### Step 7: Deploy to Render

1. Push your code to GitHub (make sure `models/` is not committed)
2. Connect your repo to Render
3. Render will:
   - Build your app
   - On first startup, download the model from Hugging Face
   - Cache it on disk for subsequent requests

---

## How It Works

1. **Local Development:** The app checks for `models/detector.pth` first. If found, uses it.
2. **Render Deployment:** 
   - Model not in repo (excluded by .gitignore)
   - On startup, `model_loader.py` downloads from Hugging Face
   - Model cached to `~/.cache/huggingface/hub/`
   - Subsequent deploys reuse the cache (faster)

---

## Model Size Reduction (Optional)

To further reduce model size, you can quantize it:

### Option 1: PyTorch Dynamic Quantization (2-4x smaller)

```python
import torch
import torch.nn as nn

# Load model
model = torch.load('models/detector.pth', map_location='cpu')

# Quantize
quantized_model = torch.quantization.quantize_dynamic(
    model, 
    {nn.Linear, nn.Conv2d}, 
    dtype=torch.qint8
)

# Save
torch.save(quantized_model.state_dict(), 'models/detector-int8.pth')
```

### Option 2: Float16 Quantization

```python
import torch

model = torch.load('models/detector.pth', map_location='cpu')
model = model.half()  # Convert to float16
torch.save(model.state_dict(), 'models/detector-fp16.pth')
```

**Note:** Test accuracy after quantization. Some models may have slight accuracy loss.

---

## Troubleshooting

### Model not downloading
- Check `HF_MODEL_REPO` environment variable is set correctly
- Verify the repository exists and is accessible
- Check Render logs for download errors

### Slow first request
- First request downloads the model (~90MB)
- Subsequent requests use cached model (fast)
- Consider using a "warmup" endpoint that loads the model on deploy

### Authentication errors (private repos)
- Ensure `HF_TOKEN` is set in Render environment variables
- Token must have read access to the repository

### Cache not persisting
- Render's disk cache should persist between deploys
- If cache is lost, model will re-download (one-time cost)

---

## Alternative: Use Object Storage

If you prefer not to use Hugging Face, you can use:

- **Firebase Storage** (free tier: 5GB)
- **Google Cloud Storage** (free tier: 5GB)
- **AWS S3** (free tier: 5GB)

Modify `src/model_loader.py` to download from your chosen storage instead.

---

## Summary

✅ Model excluded from git (already in .gitignore)  
✅ Model uploaded to Hugging Face Hub  
✅ Code updated to download from HF if not found locally  
✅ Environment variable set in Render  
✅ Deploy and enjoy! 🚀

