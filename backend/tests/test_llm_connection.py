"""Simple test to verify LLM API connections"""
import asyncio
import sys
from openai import AsyncOpenAI

# Your API keys from .env
XAI_API_KEY = "xai-HH2WFz8UceXghoujtSnLUM1AmX6uBomYWfDYUzWC6CoWtRfXSucwqkvifew62rzPFdOCkAWx78WzIq"
OPENAI_API_KEY = "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"

async def test_xai_connection():
    """Test xAI API connection"""
    print("\n" + "="*50)
    print("Testing xAI API Connection...")
    print("="*50)
    
    client = AsyncOpenAI(
        api_key=XAI_API_KEY,
        base_url="https://api.x.ai/v1"
    )
    
    # Test different model names
    models = ["grok-2", "grok-1", "grok-beta", "grok-2-mini"]
    
    for model in models:
        try:
            print(f"\nTrying model: {model}")
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Say 'Hello from xAI!' in exactly 3 words"}
                ],
                max_tokens=20,
                temperature=0.7
            )
            print(f"✅ SUCCESS with {model}!")
            print(f"Response: {response.choices[0].message.content}")
            return True, model
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"❌ Model '{model}' not found")
            elif "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                print(f"❌ Authentication failed: {error_msg[:100]}")
                return False, None
            else:
                print(f"❌ Error with {model}: {error_msg[:100]}")
    
    return False, None

async def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n" + "="*50)
    print("Testing OpenAI API Connection...")
    print("="*50)
    
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    try:
        print("\nTrying model: gpt-3.5-turbo")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello from OpenAI!' in exactly 3 words"}
            ],
            max_tokens=20,
            temperature=0.7
        )
        print(f"✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

async def main():
    print("\n🔍 Testing LLM API Connections")
    print("This will help diagnose why the chat isn't working\n")
    
    # Test xAI
    xai_works, working_model = await test_xai_connection()
    
    # Test OpenAI
    openai_works = await test_openai_connection()
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    if xai_works:
        print(f"✅ xAI is working with model: {working_model}")
    else:
        print("❌ xAI is NOT working")
        
    if openai_works:
        print("✅ OpenAI is working")
    else:
        print("❌ OpenAI is NOT working")
    
    if not xai_works and not openai_works:
        print("\n⚠️  BOTH APIs FAILED!")
        print("\nPossible issues:")
        print("1. API keys are invalid or expired")
        print("2. No internet connection")
        print("3. API service is down")
        print("4. You need to add payment method to your API account")
    elif xai_works:
        print(f"\n🎉 xAI is working! Update your LLMService to use model: {working_model}")
    elif openai_works:
        print("\n🎉 OpenAI is working! The system can use OpenAI as fallback")
    
    print("\n💡 Recommendation:")
    if xai_works:
        print(f"   Use model '{working_model}' in your LLMService")
    elif openai_works:
        print("   Use OpenAI as the primary service")
    else:
        print("   Use mock mode or check your API keys")

if __name__ == "__main__":
    asyncio.run(main())