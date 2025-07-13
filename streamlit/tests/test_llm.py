"""
Simple OpenAI SDK Test for Qwen Models
Command-line version for testing OpenAI SDK with DashScope compatible API

Usage:
    python tests/test_openai_simple.py
"""

import os
import json
from openai import OpenAI


def test_basic_connection():
    """Test basic connection to Qwen model"""
    print("🔍 Testing basic connection...")

    # Check environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    if not api_key or not api_base:
        print("❌ Environment variables not set!")
        print("Please set:")
        print("export OPENAI_API_KEY='your_dashscope_api_key'")
        print(
            "export OPENAI_API_BASE='https://dashscope.aliyuncs.com/compatible-mode/v1'"
        )
        return None

    print(f"✅ API Key: {api_key[:8]}...")
    print(f"✅ API Base: {api_base}")

    # Initialize OpenAI client
    try:
        client = OpenAI(api_key=api_key, base_url=api_base)
        print("✅ OpenAI client initialized successfully")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize OpenAI client: {e}")
        return None


def test_model_selection(client, model_name="qwen-turbo"):
    """Test model selection and basic chat"""
    print(f"\n🤖 Testing model: {model_name}")

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, please respond with a simple greeting.",
                }
            ],
            max_tokens=50,
            temperature=0.1,
        )

        print(f"✅ Model {model_name} is available")
        print(f"📊 Usage: {response.usage}")
        print(f"🤖 Response: {response.choices[0].message.content}")

        return True
    except Exception as e:
        print(f"❌ Model {model_name} test failed: {e}")
        return False


def test_chat_parameters(client):
    """Test various chat parameters"""
    print("\n⚙️ Testing chat parameters...")

    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Explain artificial intelligence in one sentence.",
                }
            ],
            temperature=0.3,
            max_tokens=100,
            top_p=0.9,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=False,
        )

        print("✅ Chat parameters test successful")
        print(f"📊 Usage: {response.usage}")
        print(f"🤖 Response: {response.choices[0].message.content}")

        return True
    except Exception as e:
        print(f"❌ Chat parameters test failed: {e}")
        return False


def test_thinking_mode_control(client):
    """Test thinking mode control"""
    print("\n🧠 Testing thinking mode control...")

    # Test with thinking mode enabled
    print("🔢 Testing with thinking mode enabled...")
    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Calculate 15 * 23 and explain the process.",
                }
            ],
            max_tokens=200,
            temperature=0.1,
            # Enable thinking mode
            tools=[{"type": "function", "function": {"name": "thinking"}}],
            tool_choice={"type": "function", "function": {"name": "thinking"}},
        )

        print("✅ Thinking mode enabled response:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Thinking mode enabled test failed: {e}")

    # Test with thinking mode disabled
    print("\n⚡ Testing with thinking mode disabled...")
    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Calculate 15 * 23 and explain the process.",
                }
            ],
            max_tokens=200,
            temperature=0.1,
            # No tools parameter = thinking mode disabled
        )

        print("✅ Direct response mode:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Direct mode test failed: {e}")


def test_streaming(client):
    """Test streaming response"""
    print("\n🌊 Testing streaming response...")

    try:
        stream = client.chat.completions.create(
            model="qwen-turbo",
            messages=[{"role": "user", "content": "Write a short poem about spring."}],
            max_tokens=150,
            temperature=0.7,
            stream=True,
        )

        print("✅ Streaming response:")
        full_response = ""

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)

        print("\n✅ Streaming completed")
        return True

    except Exception as e:
        print(f"❌ Streaming test failed: {e}")
        return False


def test_function_calling(client):
    """Test function calling capability"""
    print("\n🔧 Testing function calling...")

    # Define a sample function
    functions = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather information for a specific city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string", "description": "City name"},
                        "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                    },
                    "required": ["city"],
                },
            },
        }
    ]

    try:
        response = client.chat.completions.create(
            model="qwen-turbo",
            messages=[
                {"role": "user", "content": "What's the weather like in Beijing today?"}
            ],
            functions=functions,
            function_call="auto",
            max_tokens=200,
        )

        print("✅ Function calling response:")

        # Check if there's a function call
        if response.choices[0].message.function_call:
            function_call = response.choices[0].message.function_call
            print(f"📞 Function called: {function_call.name}")
            print(f"📋 Arguments: {json.loads(function_call.arguments)}")
        else:
            print("💬 Regular response:")
            print(response.choices[0].message.content)

        return True

    except Exception as e:
        print(f"❌ Function calling test failed: {e}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting OpenAI SDK + Qwen Model Tests")
    print("=" * 50)

    # Test basic connection
    client = test_basic_connection()
    if not client:
        return

    # Test different models
    models_to_test = [
        "qwen3-235b-a22b",
        "qwen3-30b-a3b",
        "qwen3-32b",
        "qwen-turbo-2025-04-28",
        "qwen-plus-2025-04-28",
    ]
    for model in models_to_test:
        test_model_selection(client, model)

    # Test chat parameters
    test_chat_parameters(client)

    # Test thinking mode control
    test_thinking_mode_control(client)

    # Test streaming
    test_streaming(client)

    # Test function calling
    test_function_calling(client)

    print("\n" + "=" * 50)
    print("✅ All tests completed!")


if __name__ == "__main__":
    main()
