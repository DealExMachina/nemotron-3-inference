# Dockerfile for NVIDIA Nemotron-3-Nano-30B-A3B-FP8 with vLLM
# Based on official vLLM OpenAI-compatible server image
# Target: AMD64 architecture with NVIDIA GPU support

FROM vllm/vllm-openai:v0.12.0

# Model configuration
ENV MODEL_NAME="nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8"
ENV VLLM_ATTENTION_BACKEND=FLASHINFER

# Server configuration
ENV HOST="0.0.0.0"
ENV PORT="8000"
ENV SERVED_MODEL_NAME="nemotron"

# Optional: Set HF_TOKEN at runtime for gated models
# ENV HF_TOKEN=""

# Expose the API port
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command to start vLLM server with Nemotron configuration
# Note: The base image entrypoint is `python -m vllm.entrypoints.openai.api_server`
CMD ["--model", "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8", \
     "--dtype", "auto", \
     "--trust-remote-code", \
     "--served-model-name", "nemotron", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--enable-auto-tool-choice", \
     "--tool-call-parser", "qwen3_coder", \
     "--reasoning-parser", "deepseek_r1"]

