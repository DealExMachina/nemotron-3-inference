# Nemotron 3 Nano Inference on Koyeb

[![License](https://img.shields.io/badge/License-NVIDIA_Open_Model-green.svg)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8/blob/main/LICENSE)
[![Model](https://img.shields.io/badge/HuggingFace-Nemotron--3--Nano-yellow.svg)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
[![vLLM](https://img.shields.io/badge/Inference-vLLM_v0.12-blue.svg)](https://docs.vllm.ai/)
[![Deploy](https://img.shields.io/badge/Deploy-Koyeb-purple.svg)](https://www.koyeb.com/)
[![Docker](https://img.shields.io/badge/Docker-AMD64-2496ED.svg)](https://hub.docker.com/)
[![CI](https://github.com/DealExMachina/nemotron-3-inference/actions/workflows/deploy.yml/badge.svg)](https://github.com/DealExMachina/nemotron-3-inference/actions)

Deploy [NVIDIA Nemotron-3-Nano-30B-A3B-FP8](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8) on Koyeb using vLLM with an OpenAI-compatible API.

## Model Overview

Nemotron 3 Nano represents a significant advancement in efficient large language model design. It combines a hybrid Mamba-2 and Transformer architecture with Mixture-of-Experts (MoE) routing to achieve strong reasoning performance while activating only a fraction of its parameters per token.

| Property | Value |
|----------|-------|
| Total Parameters | 31.6B |
| Active Parameters | 3.6B per token (MoE) |
| Architecture | Hybrid Mamba-2 + Transformer + MoE |
| Context Length | 1M tokens (vLLM configured for 262K) |
| Precision | FP8 |
| Languages | EN, ES, FR, DE, JA, IT |

### Architecture

The hybrid architecture leverages:

- **Mamba-2 layers** for efficient long-context processing with linear complexity
- **Transformer attention layers** for high-accuracy fine-grained reasoning
- **Mixture-of-Experts** with 6 of 128 experts active per token, reducing compute while maintaining capacity

This design enables the model to handle contexts up to 1 million tokens while maintaining competitive inference speed.

### Capabilities

- **Reasoning**: Supports ON/OFF reasoning modes and configurable thinking budgets for predictable inference costs
- **Tool Calling**: Built for multi-step agentic workflows with function calling support
- **Long Context**: Tested up to 262K tokens on vLLM; model supports 1M tokens natively
- **Multilingual**: Trained on English, Spanish, French, German, Japanese, and Italian

## Performance Benchmarks

Measured on Koyeb H100 (80GB) instance:

| Metric | Result |
|--------|--------|
| Prefill throughput (100 tokens) | 315 tokens/s |
| Prefill throughput (1K tokens) | 807 tokens/s |
| Prefill throughput (5K tokens) | 4,677 tokens/s |
| Prefill throughput (10K tokens) | 8,188 tokens/s |
| Generation speed | 190-215 tokens/s |
| Context window | 262,144 tokens |

Reasoning traces are extracted via the `deepseek_r1` parser, exposing the model's internal deliberation before generating a response.

## Hardware Requirements

The FP8 quantized model requires GPU compute capability 89 or higher.

| GPU | VRAM | Koyeb Instance | Hourly Cost | FP8 Support |
|-----|------|----------------|-------------|-------------|
| H100 | 80 GB | `gpu-nvidia-h100` | $3.30 | Yes (capability 90) |
| L40S | 48 GB | `gpu-nvidia-l40s` | $1.55 | Yes (capability 89) |
| A100 | 80 GB | `gpu-nvidia-a100` | $2.00 | No (capability 80) |

The A100 does not support the ModelOpt FP8 quantization format used by this model.

## Quick Start

### Prerequisites

1. [Koyeb account](https://app.koyeb.com/) with GPU access
2. [Hugging Face token](https://huggingface.co/settings/tokens) for model download
3. GitHub repository with Actions enabled

### Setup Secrets

#### Koyeb Secrets

Create these secrets in the [Koyeb Control Panel](https://app.koyeb.com/secrets):

```bash
koyeb secret create hf-token --value "hf_your_token_here"

koyeb secret create dockerhub-secret \
  --type registry \
  --registry-url docker.io \
  --registry-username YOUR_DOCKERHUB_USERNAME \
  --registry-password YOUR_DOCKERHUB_TOKEN
```

#### GitHub Secrets

Add these secrets in your repository settings under Secrets and variables > Actions:

- `KOYEB_TOKEN`: Koyeb API token from [Account Settings](https://app.koyeb.com/settings/api)
- `DOCKERHUB_USERNAME`: Docker Hub username
- `DOCKERHUB_TOKEN`: Docker Hub access token from [Security Settings](https://hub.docker.com/settings/security)

### Deploy

Push to the main branch to trigger automatic deployment:

```bash
git add .
git commit -m "Deploy Nemotron 3 Nano"
git push origin main
```

## API Usage

The deployment exposes an OpenAI-compatible API at `https://your-app.koyeb.app/v1`.

### Python

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-app.koyeb.app/v1",
    api_key="not-needed"
)

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

# Access reasoning trace if available
if hasattr(response.choices[0].message, 'reasoning_content'):
    print("Reasoning:", response.choices[0].message.reasoning_content)
```

### cURL

```bash
curl https://your-app.koyeb.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nemotron",
    "messages": [
      {"role": "user", "content": "What is the capital of France?"}
    ],
    "temperature": 0.7
  }'
```

### Tool Calling

The server is configured with `--enable-auto-tool-choice` for function calling:

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
    messages=[{"role": "user", "content": "What is the weather in Paris?"}],
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

The Dockerfile configures the server with:

```
--model nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8
--dtype auto
--trust-remote-code
--served-model-name nemotron
--enable-auto-tool-choice
--tool-call-parser qwen3_coder
--reasoning-parser deepseek_r1
```

For multi-GPU deployments:

```
--tensor-parallel-size 2
```

## Cost Optimization

The `koyeb.yaml` configuration enables scale-to-zero:

- `min: 0` scales down when idle
- `sleep_idle_delay: 900` sleeps after 15 minutes of no requests

First request after sleep incurs 2-5 minutes latency while the model loads.

## Testing

Run the test suite to validate the deployment:

```bash
pip install openai
python comprehensive_test.py
```

The test suite covers:

- Context length handling (100 to 10K tokens)
- Reasoning with trace extraction
- Tool calling via OpenAI function format
- Multi-turn conversations

## Troubleshooting

### Model fails to load

1. Verify `HF_TOKEN` is set correctly
2. Confirm the GPU instance has 80GB VRAM
3. Check logs: `koyeb service logs nemotron-3-inference/nemotron`

### Out of Memory

Reduce context window if needed:

```
--max-model-len 32768
```

### Slow startup

Model loading takes 2-5 minutes. The health check has a 5-minute grace period.

## References

### Model Documentation

| Resource | Description |
|----------|-------------|
| [Nemotron 3 Nano Blog Post](https://huggingface.co/blog/nvidia/nemotron-3-nano-efficient-open-intelligent-models) | Official NVIDIA announcement with architecture details |
| [Model Card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8) | Hugging Face model page with weights and documentation |
| [Technical Report](https://arxiv.org/abs/2506.11572) | Full technical details on training and architecture |

### Deployment Guides

| Resource | Description |
|----------|-------------|
| [vLLM Nemotron Cookbook](https://docs.vllm.ai/projects/recipes/en/latest/NVIDIA/Nemotron-3-Nano-30B-A3B.html) | Official vLLM deployment guide |
| [vLLM Blog Post](https://blog.vllm.ai/2025/12/15/run-nvidia-nemotron-3-nano.html) | vLLM team guide for running Nemotron |
| [Koyeb GPU Documentation](https://www.koyeb.com/docs/reference/instances#gpu-instances) | Koyeb GPU instance specifications |

### Related Projects

| Project | Description |
|---------|-------------|
| [vLLM](https://github.com/vllm-project/vllm) | High-throughput LLM serving engine |
| [SGLang](https://github.com/sgl-project/sglang) | Alternative serving framework with Nemotron support |
| [OpenRouter](https://openrouter.ai/) | Hosted API access to Nemotron models |

## License

The Nemotron model is released under the [NVIDIA Open Model License](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8/blob/main/LICENSE), which permits commercial use, modification, and redistribution.
