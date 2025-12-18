# Nemotron-3 Inference Server

Deploy NVIDIA's Nemotron-3-Nano (30B params, 3.6B active) with an OpenAI-compatible API. Optimized for structured outputs, tool calling, and long contexts.

[![Deploy](https://img.shields.io/badge/Deploy-Koyeb-purple.svg)](https://www.koyeb.com/)
[![Model](https://img.shields.io/badge/Model-HuggingFace-yellow.svg)](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
[![vLLM](https://img.shields.io/badge/vLLM-0.12.0-blue.svg)](https://docs.vllm.ai/)
[![Tests](https://github.com/DealExMachina/nemotron-3-inference/actions/workflows/deploy.yml/badge.svg)](https://github.com/DealExMachina/nemotron-3-inference/actions)

---

## Quick Start

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://your-service.koyeb.app/v1",
    api_key="not-needed"
)

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "Explain transformers in simple terms."}],
    max_tokens=200
)
```

---

## Why These Examples Matter

While our test examples may seem simple—parsing movie reviews, generating recipes, extracting transaction data—they represent real patterns you'll encounter in production:

- **Transaction parsing** demonstrates financial data extraction at scale
- **Portfolio analysis** shows handling of complex nested structures
- **Needle-in-a-haystack** tests prove the model can find specific information in 200K+ token documents
- **Tool calling examples** illustrate API integration patterns

The difference between a toy example and production is just complexity and volume. These tests establish that the fundamentals work reliably, which is what matters.

---

## Features

### Structured Outputs

Guaranteed JSON Schema compliance using xgrammar:

```python
from pydantic import BaseModel

class Transaction(BaseModel):
    symbol: str
    quantity: float
    price: float
    
response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "Extract: Bought 100 AAPL @ $150"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "Transaction",
            "schema": Transaction.model_json_schema(),
            "strict": True
        }
    },
    temperature=0
)
# Returns valid JSON every time
```

### Tool Calling

```python
tools = [{
    "type": "function",
    "function": {
        "name": "calculate",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"]
        }
    }
}]

response = client.chat.completions.create(
    model="nemotron",
    messages=[{"role": "user", "content": "Calculate 15 * 23 + 7"}],
    tools=tools
)
# Returns: tool_calls with calculate({"expression": "15*23+7"})
```

### Long Context

Test with full books (Ulysses, Moby Dick) from Project Gutenberg:

```bash
python long_context_test.py
```

Processes 200K+ tokens efficiently, demonstrating real document understanding beyond synthetic benchmarks.

---

## Test Suites

Run comprehensive tests to validate your deployment:

```bash
pip install -r requirements.txt

# Test all capabilities
python comprehensive_test.py

# Test financial use cases (transactions, portfolios, risk)
python financial_test.py

# Test long documents (full books)
python long_context_test.py
```

**What gets tested:**
- JSON Schema compliance (100% with xgrammar)
- Tool/function calling accuracy
- Context scaling (1K to 200K tokens)
- Financial data extraction
- Reasoning with step-by-step traces
- Multi-turn conversations

See [`docs/`](./docs/) for detailed test documentation.

---

## Deployment

### Koyeb (One-Click)

1. Fork this repo
2. Create Koyeb account
3. Add HuggingFace token as secret: `hf-token`
4. Push to trigger deploy via GitHub Actions

Configured for H100 GPU with auto-scaling (0-1 replicas).

### Local (Docker)

```bash
docker build -t nemotron-inference .
docker run --gpus all -p 8000:8000 \
  -e HF_TOKEN=your_token \
  nemotron-inference
```

---

## Configuration

The deployment is optimized for production use:

```dockerfile
--guided-decoding-backend xgrammar      # Fast JSON Schema enforcement
--enable-auto-tool-choice               # Function calling
--tool-call-parser qwen3_coder         # Tool extraction
--reasoning-parser deepseek_r1         # Reasoning traces
--max-model-len 262144                 # 262K token context
--enable-chunked-prefill               # Fast time-to-first-token
--gpu-memory-utilization 0.95          # Performance
```

Outlines library is also installed for custom grammar support (SWIFT, FIX, regulatory formats).

---

## Performance

Tested on Koyeb H100:

| Metric | Value |
|--------|-------|
| Context window | 262K tokens (expandable to 1M) |
| Throughput | 17K-23K tokens/sec |
| Latency | 0.7-5s typical |
| JSON compliance | 100% (with xgrammar) |

---

## Contributing

We'd welcome:

- **More test examples** - Real-world patterns you've tested
- **Bug reports** - Issues with specific use cases
- **Performance data** - Benchmarks on different hardware
- **Documentation** - Clearer explanations or missing info

Open an issue or submit a PR. Even small contributions help.

---

## Acknowledgments

**Kudos to the NVIDIA team** for releasing Nemotron-3 as open source. This model's combination of reasoning capability, structured output support, and efficient inference makes it practical for real applications—not just research.

The decision to release both the model and training details enables the community to build on this work. That's valuable.

---

## License

This deployment code is provided as-is under the MIT License. You're free to use, modify, and commercialize it.

**Important:** Respect the licenses of underlying components:
- [NVIDIA Nemotron-3 Model License](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8/blob/main/LICENSE)
- [vLLM License (Apache 2.0)](https://github.com/vllm-project/vllm/blob/main/LICENSE)
- [xgrammar License](https://github.com/mlc-ai/xgrammar/blob/main/LICENSE)
- [Outlines License (Apache 2.0)](https://github.com/dottxt-ai/outlines/blob/main/LICENSE)

---

## Disclaimer

**Deal ex Machina provides this code "as is" without warranty of any kind.**

You assume full responsibility for:
- Deployment and hosting costs
- Model output quality and accuracy
- Compliance with applicable regulations
- Security and data handling
- Any use in production systems

Use at your own risk. This is demonstration code—adapt it for your requirements and test thoroughly before production use.

---

## Questions?

- 📖 **Documentation**: See [`docs/`](./docs/) for detailed guides
- 🐛 **Issues**: [Open an issue](https://github.com/DealExMachina/nemotron-3-inference/issues)
- 💬 **Discussions**: [Start a discussion](https://github.com/DealExMachina/nemotron-3-inference/discussions)

---

<p align="center">
  <sub>Built by <a href="https://github.com/DealExMachina">Deal ex Machina</a> • Powered by <a href="https://huggingface.co/nvidia">NVIDIA</a> • Deployed on <a href="https://www.koyeb.com/">Koyeb</a></sub>
</p>
