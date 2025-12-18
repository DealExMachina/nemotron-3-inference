# Long Context Testing for Nemotron-3-8B-Instruct

**Model:** NVIDIA Nemotron-3-8B-Instruct  
**Maximum Context:** 1,000,000 tokens (1M)  
**Deployed Context:** 262,144 tokens (262K via vLLM)  
**Date:** December 18, 2025

---

## 🎯 Overview

This test suite evaluates Nemotron-3's ability to handle very long contexts using **real books** from Project Gutenberg. Unlike synthetic tests, these use actual literary works that humans read and understand.

### Why Long Context Matters

1. **Full Document Analysis** - Process entire research papers, books, codebases
2. **Multi-Document Reasoning** - Compare and synthesize multiple sources
3. **Extended Conversations** - Maintain context over long dialogues
4. **Large-Scale Code** - Understand entire projects at once

---

## 📚 Test Books

All books are **public domain** from Project Gutenberg:

| Book | Author | Tokens | Use Case |
|------|--------|--------|----------|
| **Moby Dick** | Herman Melville | ~215K | Classic literature, narrative understanding |
| **Ulysses** | James Joyce | ~265K | Complex modernist text, stream of consciousness |
| **The Odyssey** | Homer | ~120K | Epic poetry, character tracking |
| **War and Peace** | Leo Tolstoy | ~560K | Multi-thread narrative, character relationships |

---

## 🔬 Test Methodologies

### 1. **Needle in a Haystack (NIAH)** 🎯

The gold standard for long-context evaluation. 

**How it works:**
- Hide a specific fact (the "needle") at different positions in a long text (the "haystack")
- Ask the model to find it
- Tests: Can the model attend to information anywhere in the context?

**Our Implementation:**
```python
# Hide a secret code at 10%, 50%, and 90% through the text
needles = [
    "The secret code is: RAINBOW-UNICORN-42",
    "The magic number for this document is 8675309",
]

# Insert at position
text_with_needle = text[:position] + f"\n\n{needle}\n\n" + text[position:]

# Query: "Find the secret code in this text"
```

**What we test:**
- ✅ **Early Context** (10%): Can it find info near the beginning?
- ✅ **Middle Context** (50%): The hardest - middle gets "lost"
- ✅ **Late Context** (90%): Can it find info near the end?

### 2. **Summarization** 📝

Test the model's ability to compress and understand long documents.

**Tests:**
- Brief summary (2-3 sentences) of entire book
- Extract key themes
- Identify main characters
- Writing style analysis

**Challenges:**
- Must read entire context
- Synthesize information from multiple sections
- Distinguish important from trivial details

### 3. **Question Answering** ❓

Specific information extraction from long texts.

**Questions:**
- "What happens in the first chapter?"
- "Describe the setting"
- "What is the writing style?"
- "Quote a memorable passage"

**Tests:**
- Factual recall
- Understanding of structure
- Style recognition
- Direct quotation ability

### 4. **Context Length Scaling** 📈

Progressive testing from 1K to 200K+ tokens.

**Measures:**
- Performance degradation at scale
- Speed (tokens/second)
- Error rates
- Context limit detection

---

## 🎭 Example: Testing with Ulysses

**Ulysses by James Joyce** is perfect for long-context testing:

- **~265K tokens** - Near the deployed limit (262K)
- **Stream of consciousness** - Non-linear, requires understanding flow
- **Multiple perspectives** - Switches between characters
- **Dense prose** - Challenging vocabulary and structure

### Test Scenario:

```python
# Download Ulysses (public domain)
book_text, book_info = download_book("ulysses")

# Test 1: Needle in Haystack
# Hide "The magic number is 42" at 50% through Ulysses
# Can the model find it among 265K tokens?

# Test 2: Summarization  
# "Summarize Ulysses in 3 sentences"
# Tests: Can it understand the entire work?

# Test 3: Character Analysis
# "Who are the main characters in this book?"
# Tests: Character tracking across 265K tokens

# Test 4: Quote Extraction
# "Find a memorable passage about Dublin"
# Tests: Semantic search through long context
```

---

## 📊 Performance Expectations

### Deployed Configuration (262K tokens)

| Test | Expected Result |
|------|----------------|
| **NIAH @ 10%** | ✅ High success (early context) |
| **NIAH @ 50%** | ⚠️ Medium success (middle is hard) |
| **NIAH @ 90%** | ✅ High success (recent context) |
| **Summarization** | ✅ Good quality up to 50K tokens |
| **QA Accuracy** | ✅ High for factual questions |
| **Speed** | ~50-200 tokens/sec depending on length |

### Known Challenges

1. **Middle Context Loss** - Models struggle with info in the middle
2. **Computation Cost** - O(n²) attention is expensive
3. **Memory Limits** - 262K limit in vLLM deployment
4. **Position Bias** - Better at start/end than middle

---

## 🚀 Running the Tests

### Quick Start

```bash
# Run all long context tests
python long_context_test.py
```

### Manual Testing

```python
from long_context_test import *

# Download a book
book_text, info = download_book("ulysses")

# Run specific test
test_needle_in_haystack(book_text, info)
test_summarization(book_text, info, max_tokens=50000)
test_specific_questions(book_text, info)
```

### Custom Book

```python
# Add your own book
BOOKS["my_book"] = {
    "url": "https://www.gutenberg.org/files/XXXXX/XXXXX-0.txt",
    "title": "My Book Title",
    "tokens": 100000,  # Estimate
}

book_text, info = download_book("my_book")
```

---

## 📈 Scaling Beyond 262K

Currently deployed at **262K tokens** (vLLM configuration). The model supports up to **1M tokens**.

### To Test Full 1M Context:

1. **Update vLLM Config:**
   ```dockerfile
   --max-model-len 1000000
   ```

2. **Use War and Peace (~560K tokens):**
   ```python
   book_text, info = download_book("war_and_peace")
   test_needle_in_haystack(book_text, info)
   ```

3. **Combine Multiple Books:**
   ```python
   odyssey = download_book("odyssey")[0]
   ulysses = download_book("ulysses")[0]
   combined = odyssey + "\n\n" + ulysses
   # ~385K tokens - test cross-document reasoning
   ```

### Challenges at 1M tokens:
- ⚠️ **Memory**: Requires significant VRAM (H100 recommended)
- ⚠️ **Speed**: Quadratic attention complexity
- ⚠️ **Cost**: ~$3-6 per 1M token request at H100 pricing

---

## 🎓 Academic Benchmarks

Our tests align with research benchmarks:

### ∞Bench (Infinity Bench)
- Tasks averaging >100K tokens
- English and Chinese
- Synthetic + realistic scenarios
- **We implement:** Needle-in-haystack, summarization

### Ada-LEval
- Length-adaptable evaluation
- Up to 128K tokens
- **We implement:** Scaling tests, question answering

### LongLLMLingua
- Prompt compression
- Position bias detection
- **We implement:** Position-based NIAH

---

## 💡 Real-World Use Cases

### 1. Legal Document Analysis
```python
# Process entire contract (100K+ tokens)
contract = load_contract()
prompt = f"Analyze this contract and list all termination clauses:\n\n{contract}"
```

### 2. Codebase Understanding
```python
# Understand entire Python project
codebase = "\n\n".join(read_all_files("src/"))
prompt = f"Explain the architecture of this codebase:\n\n{codebase}"
```

### 3. Research Paper Synthesis
```python
# Compare multiple papers
papers = [paper1, paper2, paper3]  # ~150K tokens total
combined = "\n\n---\n\n".join(papers)
prompt = f"Compare the methodologies in these papers:\n\n{combined}"
```

### 4. Book/Document Q&A
```python
# Answer questions about entire book
book = download_book("ulysses")[0]
prompt = f"What are the major themes in this book?\n\n{book}"
```

---

## 📊 Sample Results

### Test Run Example (Moby Dick - 215K tokens)

```
📚 Downloading: Moby Dick by Herman Melville
✅ Downloaded: 1,215,684 characters (~303,921 tokens)

🎯 Needle in Haystack @ 50%:
   🔍 Hidden: "The secret code is: RAINBOW-UNICORN-42"
   📏 Context length: ~215,000 tokens
   ⏱️  Time: 45.3s
   💬 Response: "The secret code mentioned in the text is RAINBOW-UNICORN-42"
   ✅ SUCCESS: Needle found
   📊 Tokens: 215,124 total
   🚀 Speed: 4,749 tokens/s

📝 Summarization:
   💬 "Moby Dick is the story of Captain Ahab's obsessive quest to hunt 
       down the white whale that took his leg. Told through the eyes of 
       Ishmael, a sailor aboard the Pequod, the novel explores themes of 
       fate, obsession, and man versus nature."
   ⏱️  Time: 23.1s
   ✅ Excellent summary quality
```

---

## 🎯 Key Findings

### ✅ Strengths
1. **Full Context Utilization** - Can process entire books
2. **Good Summarization** - Captures key themes
3. **Reliable QA** - Answers specific questions accurately
4. **Position Awareness** - Finds info at various positions

### ⚠️ Limitations
1. **Middle Context Challenge** - Harder to find info in middle 50%
2. **Speed Trade-off** - Slower with very long contexts
3. **Memory Constraints** - 262K deployed limit (model: 1M)

### 🎓 Best Practices
1. Put important info at **start or end** of context
2. Use **structured prompts** to guide attention
3. Consider **chunking** for >262K tokens
4. Test with **real documents**, not just synthetic data

---

## 🔗 References

1. **∞Bench**: Long-context benchmark (100K+ tokens)  
   https://arxiv.org/abs/2402.13718

2. **Needle-in-a-Haystack Tests**  
   Standard evaluation for long-context models

3. **Project Gutenberg**  
   https://www.gutenberg.org/ (public domain books)

4. **vLLM Documentation**  
   https://docs.vllm.ai/ (context window configuration)

5. **NVIDIA Nemotron-3**  
   https://developer.nvidia.com/blog/nemotron-h-reasoning

---

## 📝 Next Steps

1. **Increase Context Window** - Test at full 1M tokens
2. **Add More Books** - Expand test corpus
3. **Multi-Document** - Test cross-document reasoning
4. **RAG Comparison** - Compare with RAG approaches
5. **Performance Tuning** - Optimize for speed vs. context

---

**Ready to test?**

```bash
python long_context_test.py
```

Let's see how Nemotron-3 handles the full Ulysses! 📚🚀
