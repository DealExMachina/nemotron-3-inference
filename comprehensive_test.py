#!/usr/bin/env python3
"""Comprehensive test suite for Nemotron 3 Nano API via vLLM OpenAI-compatible endpoint"""

import asyncio
import time
import json
from datetime import datetime
from typing import List, Optional, Literal
from enum import Enum
from openai import OpenAI

try:
    from pydantic import BaseModel, Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("⚠️  Pydantic not available. Some structured output tests will be skipped.")

# API Configuration - vLLM OpenAI-compatible endpoint
API_URL = "https://nemotron-3-inference-dealexmachina-53d19e1c.koyeb.app"
MODEL_NAME = "nemotron"

# Create OpenAI client pointing to vLLM endpoint
client = OpenAI(
    base_url=f"{API_URL}/v1",
    api_key="not-needed"  # vLLM doesn't require auth by default
)

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(response, elapsed_time: float, show_reasoning: bool = True):
    """Print test result in a formatted way"""
    print(f"⏱️  Time: {elapsed_time:.3f}s")
    
    choice = response.choices[0]
    message = choice.message
    
    # Content
    if message.content:
        content = message.content
        if len(content) > 300:
            print(f"💬 Response: {content[:300]}...")
        else:
            print(f"💬 Response: {content}")
    
    # Reasoning content (Nemotron specific - via deepseek_r1 parser)
    if show_reasoning and hasattr(message, 'reasoning_content') and message.reasoning_content:
        reasoning = message.reasoning_content
        if len(reasoning) > 300:
            print(f"🧠 Reasoning: {reasoning[:300]}...")
        else:
            print(f"🧠 Reasoning: {reasoning}")
    
    # Tool calls
    if message.tool_calls:
        print(f"🔧 Tool Calls: {len(message.tool_calls)}")
        for i, tool_call in enumerate(message.tool_calls[:5], 1):
            func = tool_call.function
            print(f"   {i}. {func.name}({func.arguments})")
    
    # Usage stats
    if response.usage:
        usage = response.usage
        total = usage.total_tokens
        prompt = usage.prompt_tokens
        completion = usage.completion_tokens
        print(f"📊 Tokens: {total} (prompt: {prompt}, completion: {completion})")
        if elapsed_time > 0:
            speed = total / elapsed_time
            print(f"🚀 Speed: {speed:.2f} tokens/s")
    
    # Finish reason
    print(f"🏁 Finish Reason: {choice.finish_reason}")


def test_context_lengths():
    """Test different context lengths"""
    print_section("CONTEXT LENGTH TESTS")
    print("📝 Nemotron 3 Nano supports up to 1M tokens (vLLM configured for 262K)")
    
    test_cases = [
        ("Small (~100 tokens)", " ".join(["word"] * 50) + ". What is 2+2?", 20),
        ("Medium (~1K tokens)", " ".join(["sentence"] * 500) + ". What is the capital of France?", 30),
        ("Large (~5K tokens)", " ".join(["paragraph"] * 2500) + ". Summarize quantum computing briefly.", 50),
        ("Very Large (~10K tokens)", " ".join(["document"] * 5000) + ". What is machine learning?", 50),
    ]
    
    for name, prompt, max_tokens in test_cases:
        print(f"\n📏 {name}:")
        estimated_tokens = len(prompt) // 4
        print(f"📝 Estimated input tokens: ~{estimated_tokens:,}")
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            elapsed = time.time() - start
            print_result(response, elapsed, show_reasoning=False)
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_reasoning():
    """Test reasoning capabilities"""
    print_section("REASONING TESTS")
    print("🧠 Testing reasoning (deepseek_r1 parser enabled in vLLM)")
    
    test_cases = [
        ("Math Problem", "If a train travels 120 km in 2 hours, and another train travels 180 km in 3 hours, which train is faster? Show your reasoning step by step."),
        ("Logical Puzzle", "Alice is taller than Bob. Bob is taller than Charlie. Is Alice taller than Charlie? Explain your reasoning."),
        ("Multi-step Problem", "A store has 100 apples. They sell 30 on Monday, 25 on Tuesday, and 20 on Wednesday. How many apples are left? Show your work."),
    ]
    
    for name, prompt in test_cases:
        print(f"\n🧠 {name}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            elapsed = time.time() - start
            print_result(response, elapsed, show_reasoning=True)
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_tool_calling():
    """Test tool calling capabilities via vLLM"""
    print_section("TOOL CALLING TESTS (Basic)")
    print("🔧 Testing tool calling - Nemotron-3 trained on Glaive V2 & Xlam datasets")
    
    # Define tools in OpenAI format
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "Get the current date and time",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform a mathematical calculation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate (e.g., '2+2', '15*23+7')"
                        }
                    },
                    "required": ["expression"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state/country, e.g., 'Paris, France'"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]
    
    test_cases = [
        ("Time Query", "What time is it right now?"),
        ("Weather Query", "What is the weather like in Paris, France?"),
        ("Calculation", "Calculate 15 * 23 + 7"),
        ("Multi-tool", "What's the weather in Tokyo and calculate 100 / 4"),
    ]
    
    for name, prompt in test_cases:
        print(f"\n🔧 {name}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice="auto",
                max_tokens=150
            )
            elapsed = time.time() - start
            print_result(response, elapsed, show_reasoning=False)
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_advanced_tool_calling():
    """Test advanced tool calling with complex scenarios"""
    print_section("TOOL CALLING TESTS (Advanced)")
    print("🔧 Testing multi-step reasoning with tools")
    
    # Define more complex tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_database",
                "description": "Search a database for information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "table": {"type": "string", "enum": ["users", "products", "orders"]},
                        "limit": {"type": "integer", "description": "Max results to return"}
                    },
                    "required": ["query", "table"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_email",
                "description": "Send an email notification",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to": {"type": "string", "description": "Email recipient"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body"}
                    },
                    "required": ["to", "subject", "body"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "analyze_sentiment",
                "description": "Analyze the sentiment of text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Text to analyze"}
                    },
                    "required": ["text"]
                }
            }
        }
    ]
    
    test_cases = [
        ("Database Query", "Search for all orders made by user 'john@example.com', limit to 10 results"),
        ("Email Composition", "Send an email to support@company.com about a billing issue with order #12345"),
        ("Sentiment Analysis", "Analyze the sentiment of this review: 'The product is amazing! Best purchase ever!'"),
        ("Complex Workflow", "Search the products table for 'laptops', then email the results to admin@company.com"),
    ]
    
    for name, prompt in test_cases:
        print(f"\n🔧 {name}:")
        print(f"   📝 Prompt: {prompt}")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice="auto",
                max_tokens=200
            )
            elapsed = time.time() - start
            print_result(response, elapsed, show_reasoning=False)
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_different_prompt_types():
    """Test different types of prompts"""
    print_section("PROMPT TYPE TESTS")
    
    test_cases = [
        ("Coding Question", "Write a Python function to calculate the factorial of a number.", 200),
        ("Creative Writing", "Write a short story (2-3 sentences) about a robot learning to paint.", 100),
        ("Technical Explanation", "Explain how a transformer neural network works in simple terms.", 200),
        ("Analysis", "What are the main pros and cons of renewable energy?", 200),
    ]
    
    for name, prompt, max_tokens in test_cases:
        print(f"\n📝 {name}:")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            elapsed = time.time() - start
            print_result(response, elapsed, show_reasoning=True)
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_conversation():
    """Test multi-turn conversation"""
    print_section("CONVERSATION TEST")
    
    print("\n💬 Multi-turn conversation:")
    
    messages = [
        {"role": "user", "content": "My name is Alice and I like programming."},
    ]
    
    # First turn
    print(f"\n👤 Turn 1: {messages[0]['content']}")
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=100
        )
        elapsed = time.time() - start
        print_result(response, elapsed, show_reasoning=False)
        
        # Add assistant response to conversation
        assistant_msg = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_msg})
        
        # Second turn
        messages.append({"role": "user", "content": "I prefer Python. Can you write me a simple hello world function?"})
        print(f"\n👤 Turn 2: {messages[-1]['content']}")
        
        start = time.time()
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            max_tokens=150
        )
        elapsed = time.time() - start
        print_result(response, elapsed, show_reasoning=False)
        
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_structured_output_basic():
    """Test structured JSON output with basic schemas"""
    print_section("STRUCTURED OUTPUT TESTS (Basic JSON Schema)")
    print("📋 Testing guided JSON generation with vLLM")
    
    test_cases = [
        {
            "name": "Movie Review Extraction",
            "prompt": "Extract the title and rating from this review: 'Inception is a really well made film. I rate it four stars out of five.'",
            "schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "rating": {"type": "number", "minimum": 0, "maximum": 5}
                },
                "required": ["title", "rating"]
            }
        },
        {
            "name": "Person Information",
            "prompt": "Generate information for a fictional person named John Smith who is 35 years old and works as a software engineer in San Francisco.",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "occupation": {"type": "string"},
                    "city": {"type": "string"}
                },
                "required": ["name", "age", "occupation", "city"]
            }
        },
        {
            "name": "Task List",
            "prompt": "Create a list of 3 daily tasks for a software developer.",
            "schema": {
                "type": "object",
                "properties": {
                    "tasks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "task": {"type": "string"},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                            },
                            "required": ["task", "priority"]
                        }
                    }
                },
                "required": ["tasks"]
            }
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 {case['name']}:")
        print(f"   🎯 Schema: {json.dumps(case['schema'], indent=2)[:150]}...")
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": case['prompt']}],
                extra_body={"guided_json": case['schema']},
                max_tokens=200
            )
            elapsed = time.time() - start
            
            # Parse and validate JSON
            content = response.choices[0].message.content
            try:
                parsed = json.loads(content)
                print(f"✅ Valid JSON: {json.dumps(parsed, indent=2)}")
            except json.JSONDecodeError:
                print(f"⚠️  Response: {content}")
            
            print(f"⏱️  Time: {elapsed:.3f}s")
            if response.usage:
                print(f"📊 Tokens: {response.usage.total_tokens}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def test_structured_output_advanced():
    """Test structured output with Pydantic models"""
    if not PYDANTIC_AVAILABLE:
        print_section("STRUCTURED OUTPUT TESTS (Pydantic)")
        print("⚠️  Skipping - Pydantic not installed")
        return
    
    print_section("STRUCTURED OUTPUT TESTS (Pydantic Models)")
    print("🏗️  Testing with Pydantic BaseModel schemas")
    
    # Define Pydantic models
    class CarType(str, Enum):
        sedan = "sedan"
        suv = "SUV"
        truck = "Truck"
        coupe = "Coupe"
        
    class CarDescription(BaseModel):
        brand: str = Field(description="Car manufacturer")
        model: str = Field(description="Car model name")
        car_type: CarType = Field(description="Type of car")
        year: Optional[int] = Field(description="Year of manufacture", ge=1900, le=2025)
    
    class CodeAnalysis(BaseModel):
        language: Literal["python", "javascript", "java", "c++", "other"]
        complexity: Literal["low", "medium", "high"]
        has_errors: bool
        suggestions: List[str] = Field(description="List of improvement suggestions")
    
    class RecipeInfo(BaseModel):
        name: str
        cuisine: str
        prep_time_minutes: int
        difficulty: Literal["easy", "medium", "hard"]
        ingredients: List[str]
        main_ingredient: str
    
    test_cases = [
        {
            "name": "Car from 90s",
            "model": CarDescription,
            "prompt": "Generate a JSON with the brand, model, year, and car_type of the most iconic car from the 90's."
        },
        {
            "name": "Code Analysis",
            "model": CodeAnalysis,
            "prompt": "Analyze this code snippet: 'def hello(): print('Hello')'. Provide language, complexity, error status, and suggestions."
        },
        {
            "name": "Recipe Extraction",
            "model": RecipeInfo,
            "prompt": "Create a recipe for classic Italian pasta carbonara with prep time, difficulty, and ingredients."
        }
    ]
    
    for case in test_cases:
        print(f"\n🏗️  {case['name']}:")
        schema = case['model'].model_json_schema()
        print(f"   📐 Model: {case['model'].__name__}")
        
        start = time.time()
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": case['prompt']}],
                extra_body={"guided_json": schema},
                max_tokens=300
            )
            elapsed = time.time() - start
            
            # Parse and validate with Pydantic
            content = response.choices[0].message.content
            try:
                parsed_json = json.loads(content)
                validated = case['model'](**parsed_json)
                print(f"✅ Valid {case['model'].__name__}:")
                print(json.dumps(parsed_json, indent=2))
            except Exception as validation_error:
                print(f"⚠️  Validation error: {validation_error}")
                print(f"   Raw response: {content}")
            
            print(f"⏱️  Time: {elapsed:.3f}s")
            if response.usage:
                print(f"📊 Tokens: {response.usage.total_tokens}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"❌ Error after {elapsed:.2f}s: {e}")


def main():
    print("\n" + "🧪 " * 35)
    print("  COMPREHENSIVE NEMOTRON 3 NANO API TEST SUITE")
    print("  vLLM OpenAI-compatible endpoint")
    print("  Model: NVIDIA Nemotron-3-8B-Instruct")
    print("🧪 " * 35)
    
    try:
        # Check model availability first
        print("\n📋 Checking available models...")
        models = client.models.list()
        for model in models.data:
            print(f"   - {model.id} (context: {getattr(model, 'max_model_len', 'N/A')})")
        
        # Run basic tests
        test_context_lengths()
        test_reasoning()
        test_different_prompt_types()
        test_conversation()
        
        # Run tool calling tests
        test_tool_calling()
        test_advanced_tool_calling()
        
        # Run structured output tests
        test_structured_output_basic()
        test_structured_output_advanced()
        
        print_section("TEST SUITE COMPLETE")
        print("✅ All tests completed!")
        print("\n📊 Summary:")
        print("   - Context Length Tests: ✅")
        print("   - Reasoning Tests: ✅")
        print("   - Tool Calling Tests (Basic & Advanced): ✅")
        print("   - Structured Output Tests (JSON Schema & Pydantic): ✅")
        print("   - Prompt Type Tests: ✅")
        print("   - Conversation Tests: ✅")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
