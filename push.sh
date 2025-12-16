#!/bin/bash
set -e

cd /Users/jeanbapt/nemotron-nano

echo "=== Initializing Git ==="
rm -rf .git
git init

echo "=== Setting remote ==="
git remote add origin https://github.com/DealExMachina/nemotron-3-inference.git

echo "=== Adding files ==="
git add -A
git status

echo "=== Committing ==="
git commit -m "Initial commit: Nemotron 3 Nano vLLM deployment on Koyeb

- Dockerfile with vLLM v0.12.0 and Nemotron FP8 model
- GitHub Actions workflow for Docker Hub build and Koyeb deployment
- Koyeb service configuration for A100 GPU
- Complete documentation and setup instructions"

echo "=== Pushing to main ==="
git branch -M main
git push -u origin main --force

echo "=== Done! ==="

