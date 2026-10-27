#!/bin/bash
mkdir -p model
echo "Downloading Phi-3-mini-4k-instruct-q4.gguf (2.3GB)..."
wget -qcO model/Phi-3-mini-4k-instruct-q4.gguf https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf
echo "Download complete."
