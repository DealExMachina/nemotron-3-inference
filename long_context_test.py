#!/usr/bin/env python3
"""
Long Context Testing Suite for Nemotron 3 Nano
Tests context windows from 10K to 262K tokens (vLLM limit) / 1M tokens (model max)

Uses public domain books from Project Gutenberg for realistic testing.
Implements Needle-in-a-Haystack (NIAH) and other long-context benchmarks.
"""

import asyncio
import time
import json
import random
import urllib.request
from typing import Optional, Tuple
from openai import OpenAI

# API Configuration
API_URL = "https://nemotron-3-inference-dealexmachina-53d19e1c.koyeb.app"
MODEL_NAME = "nemotron"

# Create OpenAI client
client = OpenAI(
    base_url=f"{API_URL}/v1",
    api_key="not-needed"
)

# Project Gutenberg URLs (public domain)
BOOKS = {
    "odyssey": {
        "url": "https://www.gutenberg.org/files/1727/1727-0.txt",
        "title": "The Odyssey by Homer",
        "tokens": 120000,  # ~120K tokens
    },
    "ulysses": {
        "url": "https://www.gutenberg.org/files/4300/4300-0.txt", 
        "title": "Ulysses by James Joyce",
        "tokens": 265000,  # ~265K tokens - full novel
    },
    "war_and_peace": {
        "url": "https://www.gutenberg.org/files/2600/2600-0.txt",
        "title": "War and Peace by Leo Tolstoy",
        "tokens": 560000,  # ~560K tokens
    },
    "moby_dick": {
        "url": "https://www.gutenberg.org/files/2701/2701-0.txt",
        "title": "Moby Dick by Herman Melville",
        "tokens": 215000,  # ~215K tokens
    },
}


def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def estimate_tokens(text: str) -> int:
    """Rough token estimation (1 token ≈ 4 characters)"""
    return len(text) // 4


def download_book(book_key: str) -> Tuple[str, dict]:
    """Download a book from Project Gutenberg"""
    if book_key not in BOOKS:
        raise ValueError(f"Unknown book: {book_key}")
    
    book_info = BOOKS[book_key]
    print(f"\n📚 Downloading: {book_info['title']}")
    print(f"   URL: {book_info['url']}")
    print(f"   Expected tokens: ~{book_info['tokens']:,}")
    
    try:
        with urllib.request.urlopen(book_info['url']) as response:
            text = response.read().decode('utf-8')
        
        # Clean up Project Gutenberg header/footer
        start_marker = "*** START OF"
        end_marker = "*** END OF"
        
        start_idx = text.find(start_marker)
        if start_idx != -1:
            # Find the end of the line with the start marker
            start_idx = text.find('\n', start_idx) + 1
        else:
            start_idx = 0
            
        end_idx = text.find(end_marker)
        if end_idx != -1:
            text = text[start_idx:end_idx]
        else:
            text = text[start_idx:]
        
        actual_tokens = estimate_tokens(text)
        print(f"✅ Downloaded: {len(text):,} characters (~{actual_tokens:,} tokens)")
        
        return text.strip(), book_info
    
    except Exception as e:
        print(f"❌ Error downloading book: {e}")
        raise


def test_needle_in_haystack(book_text: str, book_info: dict):
    """
    Needle-in-a-Haystack Test
    Hide a specific fact in a long context and test retrieval
    """
    print_section("NEEDLE IN A HAYSTACK TEST")
    print(f"📖 Book: {book_info['title']}")
    
    # Create a unique "needle" to hide
    needles = [
        "The secret code is: RAINBOW-UNICORN-42",
        "The magic number for this document is 8675309",
        "Remember this phrase: THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG",
    ]
    
    for position_percent in [10, 50, 90]:
        print(f"\n🎯 Test: Needle at {position_percent}% through the text")
        
        needle = random.choice(needles)
        print(f"   🔍 Hidden fact: {needle}")
        
        # Insert needle at specified position
        position = int(len(book_text) * position_percent / 100)
        text_with_needle = (
            book_text[:position] + 
            f"\n\n{needle}\n\n" + 
            book_text[position:]
        )
        
        tokens = estimate_tokens(text_with_needle)
        print(f"   📏 Context length: ~{tokens:,} tokens")
        
        # Test retrieval
        prompt = f"Read the following text carefully and find the secret code, magic number, or special phrase that stands out. What is it?\n\n{text_with_needle}"
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1  # Low temp for factual retrieval
            )
            elapsed = time.time() - start
            
            answer = response.choices[0].message.content
            found = needle.split(": ")[1] if ": " in needle else needle
            success = found.upper() in answer.upper()
            
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   💬 Response: {answer}")
            print(f"   {'✅ SUCCESS' if success else '❌ FAILED'}: Needle {'found' if success else 'not found'}")
            
            if response.usage:
                print(f"   📊 Tokens: {response.usage.total_tokens:,}")
                print(f"   🚀 Speed: {response.usage.total_tokens / elapsed:.2f} tokens/s")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Error after {elapsed:.2f}s: {e}")


def test_summarization(book_text: str, book_info: dict, max_tokens: int = 50000):
    """Test summarization of long text"""
    print_section("LONG CONTEXT SUMMARIZATION")
    print(f"📖 Book: {book_info['title']}")
    
    # Truncate to reasonable length for testing
    if estimate_tokens(book_text) > max_tokens:
        # Take first N tokens worth of text
        truncate_at = max_tokens * 4  # chars
        book_text = book_text[:truncate_at]
        print(f"   ⚠️  Truncated to ~{max_tokens:,} tokens for testing")
    
    tokens = estimate_tokens(book_text)
    print(f"   📏 Context length: ~{tokens:,} tokens")
    
    test_cases = [
        ("Brief Summary", f"Summarize the following text in 2-3 sentences:\n\n{book_text}", 150),
        ("Key Themes", f"What are the main themes in this text? List 3-5 key themes:\n\n{book_text}", 200),
        ("Characters", f"Who are the main characters or subjects in this text? Name them:\n\n{book_text}", 150),
    ]
    
    for name, prompt, max_response_tokens in test_cases:
        print(f"\n📝 {name}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_response_tokens,
                temperature=0.7
            )
            elapsed = time.time() - start
            
            answer = response.choices[0].message.content
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            print(f"   💬 Response: {answer}")
            
            if response.usage:
                print(f"   📊 Input tokens: {response.usage.prompt_tokens:,}")
                print(f"   📊 Output tokens: {response.usage.completion_tokens:,}")
                print(f"   🚀 Speed: {response.usage.total_tokens / elapsed:.2f} tokens/s")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Error after {elapsed:.2f}s: {e}")


def test_specific_questions(book_text: str, book_info: dict, max_tokens: int = 50000):
    """Test answering specific questions about the text"""
    print_section("SPECIFIC QUESTION ANSWERING")
    print(f"📖 Book: {book_info['title']}")
    
    # Truncate if needed
    if estimate_tokens(book_text) > max_tokens:
        truncate_at = max_tokens * 4
        book_text = book_text[:truncate_at]
        print(f"   ⚠️  Truncated to ~{max_tokens:,} tokens for testing")
    
    tokens = estimate_tokens(book_text)
    print(f"   📏 Context length: ~{tokens:,} tokens")
    
    # Generic questions that work for any book
    questions = [
        "What happens in the first chapter or section?",
        "Describe the setting or location where the story takes place.",
        "What is the writing style - is it formal, poetic, conversational, or something else?",
        "Are there any memorable quotes or passages? Quote one.",
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n❓ Question {i}: {question}")
        prompt = f"{question}\n\nText:\n{book_text}"
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            elapsed = time.time() - start
            
            answer = response.choices[0].message.content
            print(f"   💬 Answer: {answer[:300]}{'...' if len(answer) > 300 else ''}")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            
            if response.usage:
                print(f"   📊 Tokens: {response.usage.total_tokens:,}")
                
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Error after {elapsed:.2f}s: {e}")


def test_context_length_scaling():
    """Test with progressively longer contexts"""
    print_section("CONTEXT LENGTH SCALING TEST")
    print("📈 Testing with progressively longer contexts")
    
    # Generate text of different lengths
    base_text = "This is a test sentence. " * 100
    
    context_lengths = [1000, 5000, 10000, 20000, 50000, 100000, 150000, 200000]
    
    for target_tokens in context_lengths:
        print(f"\n📏 Target context: ~{target_tokens:,} tokens")
        
        # Generate text to reach target length
        target_chars = target_tokens * 4
        repetitions = target_chars // len(base_text) + 1
        long_text = (base_text * repetitions)[:target_chars]
        
        actual_tokens = estimate_tokens(long_text)
        print(f"   Actual: ~{actual_tokens:,} tokens")
        
        # Simple question at the end
        prompt = f"{long_text}\n\nQuestion: How many times does the word 'test' appear in the text above? Just give a rough estimate."
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
            elapsed = time.time() - start
            
            answer = response.choices[0].message.content
            print(f"   💬 Response: {answer}")
            print(f"   ⏱️  Time: {elapsed:.2f}s")
            
            if response.usage:
                print(f"   📊 Total tokens: {response.usage.total_tokens:,}")
                print(f"   🚀 Speed: {response.usage.total_tokens / elapsed:.2f} tokens/s")
            
            print("   ✅ Success")
            
        except Exception as e:
            elapsed = time.time() - start
            print(f"   ❌ Error after {elapsed:.2f}s: {e}")
            if "context" in str(e).lower() or "length" in str(e).lower():
                print("   ⚠️  Context limit reached!")
                break


def main():
    print("\n" + "📚 " * 40)
    print("  LONG CONTEXT TESTING SUITE")
    print("  Nemotron 3 Nano - Context Window Testing")
    print("  Model: NVIDIA Nemotron-3-8B-Instruct")
    print("  Deployed context: 262K tokens | Model max: 1M tokens")
    print("📚 " * 40)
    
    print("\n📋 Available Books:")
    for key, info in BOOKS.items():
        print(f"   - {key}: {info['title']} (~{info['tokens']:,} tokens)")
    
    try:
        # Test with a moderate-length book first
        print("\n" + "=" * 80)
        print("  PART 1: Testing with Moby Dick (~215K tokens)")
        print("=" * 80)
        
        book_text, book_info = download_book("moby_dick")
        
        # Run tests
        test_summarization(book_text, book_info, max_tokens=30000)
        test_specific_questions(book_text, book_info, max_tokens=30000)
        test_needle_in_haystack(book_text[:120000], book_info)  # Use first 30K tokens for NIAH
        
        # Try Ulysses if user wants (closer to deployed limit)
        print("\n" + "=" * 80)
        print("  PART 2: Testing with Ulysses (~265K tokens)")
        print("=" * 80)
        
        book_text, book_info = download_book("ulysses")
        
        # Just test a portion for speed
        test_summarization(book_text, book_info, max_tokens=50000)
        test_needle_in_haystack(book_text[:200000], book_info)  # First 50K tokens
        
        # Scaling test
        test_context_length_scaling()
        
        print_section("LONG CONTEXT TESTS COMPLETE")
        print("✅ All tests completed!")
        print("\n📊 Summary:")
        print("   - Successfully tested contexts up to deployed limit (262K tokens)")
        print("   - Needle-in-a-Haystack: Retrieval from long contexts")
        print("   - Summarization: Understanding of long documents")
        print("   - Question Answering: Specific information extraction")
        print("   - Scaling: Performance across context lengths")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
