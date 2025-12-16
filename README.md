# Nemotron 3 Inference on Koyeb

Deploy [NVIDIA Nemotron-3-Nano-30B-A3B-FP8](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8) on Koyeb using vLLM with an OpenAI-compatible API.

## Model Overview

| Property | Value |
|----------|-------|
| Total Parameters | 30B |
| Active Parameters | 3.5B (MoE) |
| Architecture | Hybrid Mamba-2 + Transformer + MoE |
| Context Length | 1M tokens |
| Precision | FP8 |
| Languages | EN, ES, FR, DE, JA, IT |

## Hardware Requirements

| GPU | VRAM | Koyeb Instance | Cost |
|-----|------|----------------|------|
| A100 | 80 GB | `gpu-nvidia-a100` | ~$2/hr |
| H100 | 80 GB | `gpu-nvidia-h100` | ~$3.30/hr |

The FP8 model requires approximately 40-48 GB VRAM minimum. A100 80GB is recommended.

## Quick Start

### Prerequisites

1. [Koyeb account](https://app.koyeb.com/) with GPU access
2. [Hugging Face token](https://huggingface.co/settings/tokens) (for model download)
3. GitHub repository with Actions enabled

### Setup Secrets

#### Koyeb Secrets

Create these secrets in [Koyeb Control Panel](https://app.koyeb.com/secrets):

```bash
# Hugging Face token for model download
koyeb secret create hf-token --value "hf_your_token_here"

# Docker Hub registry access
koyeb secret create dockerhub-secret \
  --type registry \
  --registry-url docker.io \
  --registry-username YOUR_DOCKERHUB_USERNAME \
  --registry-password YOUR_DOCKERHUB_TOKEN
```

#### GitHub Secrets

Add these secrets in your repository settings → Secrets and variables → Actions:

- `KOYEB_TOKEN`: Your Koyeb API token from [Account Settings](https://app.koyeb.com/settings/api)
- `DOCKERHUB_USERNAME`: Your Docker Hub username
- `DOCKERHUB_TOKEN`: Your Docker Hub access token from [Security Settings](https://hub.docker.com/settings/security)

### Deploy

Push to main branch to trigger automatic deployment:

```bash
git add .
git commit -m "Deploy Nemotron 3 Nano"
git push origin main
```

Or deploy manually:

```bash
# Install Koyeb CLI
curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | bash

# Create app and service
koyeb app create nemotron-3-inference

koyeb service create nemotron \
  --app nemotron-3-inference \
  --docker docker.io/YOUR_DOCKERHUB_USERNAME/nemotron-3-inference:latest \
  --docker-private-registry-secret dockerhub-secret \
  --instance-type gpu-nvidia-a100 \
  --regions fra \
  --ports 8000:http \
  --routes /:8000 \
  --checks 8000:http:/health \
  --env "HF_TOKEN=@hf-token" \
  --env "VLLM_ATTENTION_BACKEND=FLASHINFER" \
  --min-scale 0 \
  --max-scale 1
```

## API Usage

The deployment exposes an OpenAI-compatible API at `https://your-app.koyeb.app/v1`.

### Python (OpenAI SDK)

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://nemotron-nano-YOUR_ORG.koyeb.app/v1",
    api_key="not-needed"  # No auth by default
)

# Basic chat completion
response = client.chat.completions.create(
    model="nemotron",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in simple terms."}
    ],
    temperature=0.7,
    max_tokens=512
)

print(response.choices[0].message.content)

# Access reasoning trace (if available)
if hasattr(response.choices[0].message, 'reasoning_content'):
    print("Reasoning:", response.choices[0].message.reasoning_content)
```

### cURL

```bash
curl https://nemotron-nano-YOUR_ORG.koyeb.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nemotron",
    "messages": [
      {"role": "user", "content": "Write a haiku about AI."}
    ],
    "temperature": 0.7
  }'
```

### Tool Calling / Function Calling

The server is configured with `--enable-auto-tool-choice` for function calling support:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    }
]

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto"
)
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /v1/models` | List available models |
| `POST /v1/chat/completions` | Chat completions (OpenAI-compatible) |
| `POST /v1/completions` | Text completions (OpenAI-compatible) |

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HF_TOKEN` | Hugging Face token for model download | Required |
| `VLLM_ATTENTION_BACKEND` | Attention backend for vLLM | `FLASHINFER` |

### vLLM Server Options

The default configuration in the Dockerfile uses these flags:

```bash
--model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8
--dtype auto
--trust-remote-code
--served-model-name nemotron
--enable-auto-tool-choice
--tool-call-parser qwen3_coder
--reasoning-parser deepseek_r1
```

For multi-GPU setups, add:
```bash
--tensor-parallel-size 2  # For 2 GPUs
```

## Cost Optimization

The `koyeb.yaml` is configured with scale-to-zero:

- `min: 0` - Scales down when idle
- `sleep_idle_delay: 900` - Sleeps after 15 minutes of no requests

First request after sleep will have higher latency (~2-5 minutes) while the model loads.

## Troubleshooting

### Model fails to load

1. Check HF_TOKEN is set correctly
2. Verify GPU instance has sufficient VRAM (80GB recommended)
3. Check logs: `koyeb service logs nemotron-3-inference/nemotron`

### Out of Memory

Use FP8 model (already configured) or reduce `--max-model-len`:
```bash
--max-model-len 32768  # Reduce context window
```

### Slow startup

Model loading takes 2-5 minutes. The health check has a 5-minute grace period.

## References

- [vLLM Nemotron Cookbook](https://docs.vllm.ai/projects/recipes/en/latest/NVIDIA/Nemotron-3-Nano-30B-A3B.html)
- [vLLM Blog Post](https://blog.vllm.ai/2025/12/15/run-nvidia-nemotron-3-nano.html)
- [Model Card on Hugging Face](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
- [Koyeb GPU Documentation](https://www.koyeb.com/docs/reference/instances#gpu-instances)

## License

The Nemotron model is licensed under [NVIDIA Open Model License](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8/blob/main/LICENSE).

