from agent import Agent

agent = Agent(
    provider="openai",
    model="gpt-3.5-turbo",
    api_key="sk-proj-1234567890"
)

response = agent.generate(
    prompt="What is the capital of France?"
)