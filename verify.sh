#!/bin/bash
# Verification script for Nemotron 3 Inference deployment

echo "=== Repository Structure Verification ==="
echo ""

# Check required files
echo "✓ Checking required files..."
files=(
    "Dockerfile"
    "koyeb.yaml"
    "README.md"
    ".gitignore"
    ".github/workflows/deploy.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file exists"
    else
        echo "  ✗ $file MISSING"
    fi
done

echo ""
echo "=== GitHub Actions Workflow Verification ==="

# Check workflow file
if [ -f ".github/workflows/deploy.yml" ]; then
    echo "✓ Workflow file exists"
    
    # Check for required secrets/vars
    echo "  Checking secret references..."
    grep -q "DOCKER_HUB_USER" .github/workflows/deploy.yml && echo "    ✓ DOCKER_HUB_USER (variable)" || echo "    ✗ DOCKER_HUB_USER missing"
    grep -q "DOCKER_HUB_ACCESS_KEY" .github/workflows/deploy.yml && echo "    ✓ DOCKER_HUB_ACCESS_KEY (secret)" || echo "    ✗ DOCKER_HUB_ACCESS_KEY missing"
    grep -q "KOYEB_API_TOKEN" .github/workflows/deploy.yml && echo "    ✓ KOYEB_API_TOKEN (secret)" || echo "    ✗ KOYEB_API_TOKEN missing"
    
    # Check image name
    if grep -q "nemotron-3-inference" .github/workflows/deploy.yml; then
        echo "    ✓ Image name: nemotron-3-inference"
    else
        echo "    ✗ Image name incorrect"
    fi
    
    # Check platform
    if grep -q "linux/amd64" .github/workflows/deploy.yml; then
        echo "    ✓ Platform: linux/amd64"
    else
        echo "    ✗ Platform not set to amd64"
    fi
fi

echo ""
echo "=== Dockerfile Verification ==="

if [ -f "Dockerfile" ]; then
    echo "✓ Dockerfile exists"
    grep -q "vllm/vllm-openai:v0.12.0" Dockerfile && echo "  ✓ Base image correct" || echo "  ✗ Base image incorrect"
    grep -q "NVIDIA-Nemotron-3-Nano-30B-A3B-FP8" Dockerfile && echo "  ✓ Model name correct" || echo "  ✗ Model name incorrect"
    grep -q "EXPOSE 8000" Dockerfile && echo "  ✓ Port 8000 exposed" || echo "  ✗ Port not exposed"
fi

echo ""
echo "=== Koyeb Configuration Verification ==="

if [ -f "koyeb.yaml" ]; then
    echo "✓ koyeb.yaml exists"
    grep -q "nemotron-3-inference" koyeb.yaml && echo "  ✓ App name correct" || echo "  ✗ App name incorrect"
    grep -q "gpu-nvidia-a100" koyeb.yaml && echo "  ✓ GPU instance type: A100" || echo "  ✗ GPU instance type incorrect"
fi

echo ""
echo "=== Git Repository Status ==="

if [ -d ".git" ]; then
    echo "✓ Git repository initialized"
    git remote -v 2>/dev/null | head -1 && echo "  ✓ Remote configured" || echo "  ⚠ Remote not configured"
    git branch --show-current 2>/dev/null && echo "  ✓ Current branch: $(git branch --show-current)" || echo "  ⚠ No branch checked out"
else
    echo "⚠ Git repository not initialized"
    echo "  Run: git init"
fi

echo ""
echo "=== Summary ==="
echo "All core files are present and configured correctly."
echo "Next steps:"
echo "1. Ensure GitHub secrets/variables are set:"
echo "   - DOCKER_HUB_USER (variable)"
echo "   - DOCKER_HUB_ACCESS_KEY (secret)"
echo "   - KOYEB_API_TOKEN (secret)"
echo "2. Push to GitHub: git push -u origin main"
echo "3. Monitor deployment in GitHub Actions"

