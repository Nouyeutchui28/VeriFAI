#!/usr/bin/env python3
"""Download a model repository snapshot from Hugging Face Hub for offline use.

Usage:
  python scripts/download_model.py --model distilgpt2 --dest models/distilgpt2
"""
import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="distilgpt2", help="Hugging Face model repo id (e.g., distilgpt2)")
    parser.add_argument("--dest", default=None, help="Destination directory to place the snapshot")
    args = parser.parse_args()

    try:
        from huggingface_hub import snapshot_download
    except Exception as e:
        print("Please install huggingface_hub: pip install huggingface_hub")
        sys.exit(2)

    model = args.model
    dest = args.dest or os.path.join("models", model.replace("/", "__"))
    os.makedirs(dest, exist_ok=True)

    print(f"Downloading model snapshot for '{model}' into {dest} (this may take a while)...")
    try:
        repo_path = snapshot_download(repo_id=model, cache_dir=dest, repo_type="model")
        print("Download complete. Files available at:", repo_path)
    except Exception as e:
        print("Download failed:", str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
