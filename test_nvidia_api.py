import asyncio
import os
import sys

# Add app to path
sys.path.append("c:/Users/chait/Desktop/TrustLayer")

from dotenv import load_dotenv
load_dotenv()

from app.integrations.nvidia_client import QwenReasoningProvider

async def main():
    print("Initializing QwenReasoningProvider...")
    provider = QwenReasoningProvider()
    print("Generating reasons for test context...")
    context = {"amount": 50000, "merchant": "Unknown", "upi_transaction_id_valid": False}
    try:
        reasons = await provider.generate_reasons(context)
        print("Success! Reasons generated:")
        for r in reasons:
            print(f"- {r}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
