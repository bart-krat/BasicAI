import asyncio
import os
from dotenv import load_dotenv
from agent import Agent

# Load environment variables
load_dotenv()

async def main():
    # Get API key from environment
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your API key in .env file or environment")
        return
    
    agent = Agent(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key=api_key  # Use real API key
    )
    
    await agent.start_chat(
        system_message= "You are a pirate, always speak in pirate slang."
    )

if __name__ == "__main__":
    asyncio.run(main())