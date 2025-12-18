# Documentation

Technical documentation for Nemotron-3 deployment and testing.

---

## Guides

| Document | Description |
|----------|-------------|
| [**SUCCESS_REPORT.md**](../SUCCESS_REPORT.md) | 100% test achievement summary |
| [**DOCKERFILE_OPTIMIZATIONS.md**](./DOCKERFILE_OPTIMIZATIONS.md) | vLLM configuration deep dive |
| [**FINANCIAL_USE_CASES.md**](./FINANCIAL_USE_CASES.md) | Financial applications guide |
| [**LONG_CONTEXT_TESTING.md**](./LONG_CONTEXT_TESTING.md) | Testing with full books (200K+ tokens) |
| [**PYDANTIC_V2_UPDATES.md**](./PYDANTIC_V2_UPDATES.md) | Pydantic V2 migration notes |
| [**TEST_IMPROVEMENTS.md**](./TEST_IMPROVEMENTS.md) | Test suite capabilities |

---

## Quick Links

### For Operators
- **Deployment**: See main [README.md](../README.md)
- **Optimization**: [DOCKERFILE_OPTIMIZATIONS.md](./DOCKERFILE_OPTIMIZATIONS.md)

### For Developers
- **Financial Apps**: [FINANCIAL_USE_CASES.md](./FINANCIAL_USE_CASES.md)
- **Long Context**: [LONG_CONTEXT_TESTING.md](./LONG_CONTEXT_TESTING.md)
- **Testing**: [TEST_IMPROVEMENTS.md](./TEST_IMPROVEMENTS.md)

### For Contributors
- **What Works**: [SUCCESS_REPORT.md](../SUCCESS_REPORT.md)
- **Pydantic V2**: [PYDANTIC_V2_UPDATES.md](./PYDANTIC_V2_UPDATES.md)

---

## Test Suites

Located in project root:

- `comprehensive_test.py` - All capabilities
- `financial_test.py` - Financial use cases
- `long_context_test.py` - Document processing

Run any test to validate your deployment:

```bash
python comprehensive_test.py
```

---

Questions? [Open an issue](https://github.com/DealExMachina/nemotron-3-inference/issues)
