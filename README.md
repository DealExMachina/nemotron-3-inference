# Nemotron 3 Nano Inference

[![Model](https://img.shields.io/badge/HuggingFace-Nemotron--3--Nano-yellow.svg)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
[![vLLM](https://img.shields.io/badge/Inference-vLLM_v0.12-blue.svg)](https://docs.vllm.ai/)
[![Deploy](https://img.shields.io/badge/Deploy-Koyeb-purple.svg)](https://www.koyeb.com/)
[![CI](https://github.com/DealExMachina/nemotron-3-inference/actions/workflows/deploy.yml/badge.svg)](https://github.com/DealExMachina/nemotron-3-inference/actions)

Deploy [NVIDIA Nemotron-3-Nano-30B-A3B-FP8](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8) with an OpenAI-compatible API.

## Model Highlights

| Property | Value |
|----------|-------|
| Total Parameters | 31.6B |
| Active Parameters | 3.6B per token |
| Context Length | Up to 1M tokens |
| Precision | FP8 |
| Languages | EN, ES, FR, DE, JA, IT |

**Key capabilities:**
- Reasoning with thinking traces
- Tool/function calling
- Long context (262K tokens on vLLM)
- Multilingual support

**Performance:** Run `comprehensive_test.py` to measure real-world performance metrics including response times, token throughput, and latency across different workloads.

## Quick Start

### Deploy to Koyeb

1. Create a [Koyeb secret](https://app.koyeb.com/secrets) for your Hugging Face token:
   ```bash
   koyeb secret create hf-token --value "hf_your_token_here"
   ```

2. Push to main to trigger deployment:
   ```bash
   git push origin main
   ```

### API Usage

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-app.koyeb.app/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "Explain quantum computing briefly."}],
    max_tokens=512
)

print(response.choices[0].message.content)
```

### Tool Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather in a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"]
        }
    }
}]

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto"
)
```

## Performance Metrics

The comprehensive test suite (`comprehensive_test.py`) measures real-world performance metrics on the deployed endpoint. Run it to benchmark your deployment:

```bash
pip install openai
python comprehensive_test.py
```

### Measured Performance

The test suite tracks and reports:

| Metric | Description | Example Output |
|--------|-------------|----------------|
| **Response Time** | End-to-end latency for each request | `⏱️ Time: 1.234s` |
| **Token Throughput** | Tokens processed per second | `🚀 Speed: 4,155 tokens/s` |
| **Token Usage** | Prompt, completion, and total tokens | `📊 Tokens: 5,127 (prompt: 5,012, completion: 115)` |
| **Context Handling** | Performance across different input sizes (100 to 10K+ tokens) | Tested with small, medium, large, and very large inputs |
| **Reasoning Performance** | Time and quality of multi-step reasoning tasks | Includes thinking traces via `deepseek_r1` parser |
| **Tool Calling Speed** | Latency for function calling operations | Measured for single and multi-tool requests |

### Performance Test Coverage

| Test Category | What's Measured |
|---------------|-----------------|
| **Context Length** | Response time and throughput for inputs from 100 to 10,000+ tokens |
| **Reasoning** | Step-by-step reasoning performance with thinking traces |
| **Tool Calling** | Function calling latency for time, weather, calculation, and multi-tool queries |
| **Prompt Types** | Performance across coding, creative writing, technical explanations, and analysis |
| **Conversation** | Multi-turn dialogue performance with context retention |

### Example Test Output

```
📏 Large (~5K tokens):
📝 Estimated input tokens: ~5,000
⏱️  Time: 1.234s
💬 Response: Machine learning is...
🧠 Reasoning: [thinking traces if enabled]
📊 Tokens: 5,127 (prompt: 5,012, completion: 115)
🚀 Speed: 4,155 tokens/s
🏁 Finish Reason: stop
```

**Note:** Actual performance depends on:
- GPU instance type (H100 recommended for best performance)
- Current load and scale-to-zero wake time
- Input/output token counts
- Model warm-up state

## Hardware Requirements

FP8 quantization requires GPU compute capability 89+:

| GPU | VRAM | Koyeb Instance | FP8 Support |
|-----|------|----------------|-------------|
| H100 | 80 GB | `gpu-nvidia-h100` | ✅ |
| L40S | 48 GB | `gpu-nvidia-l40s` | ✅ |
| A100 | 80 GB | `gpu-nvidia-a100` | ❌ |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /v1/models` | List models |
| `POST /v1/chat/completions` | Chat completions |

## Configuration

Environment variables:

| Variable | Description |
|----------|-------------|
| `HF_TOKEN` | Hugging Face token (required) |
| `VLLM_ATTENTION_BACKEND` | Default: `FLASHINFER` |

## Cost Optimization

Scale-to-zero is enabled by default:
- Scales down after 15 minutes idle
- First request after sleep takes 2-5 minutes to load model

## References

- [Model Card](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
- [vLLM Nemotron Guide](https://docs.vllm.ai/projects/recipes/en/latest/NVIDIA/Nemotron-3-Nano-30B-A3B.html)
- [Koyeb GPU Docs](https://www.koyeb.com/docs/reference/instances#gpu-instances)

## License

[NVIDIA Open Model License](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8/blob/main/LICENSE)
