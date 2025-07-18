import os
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from agents.run import RunConfig
from dotenv import load_dotenv
import chainlit as cl

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

external_client = AsyncOpenAI(
    api_key = gemini_api_key,
    base_url = "https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model = "gemini-2.0-flash",
    openai_client= external_client
)

config = RunConfig(
    model = model,
    model_provider = external_client,
    tracing_disabled = True
)

agent = Agent(
    name = "Fitness Assistant",
    instructions = "You are a fitness assistant that helps users with workout plans, nutrition advice, and general fitness tips.",
    model = model
)

# result = Runner.run_sync(
#     agent,
#     "Create a beginner-friendly workout plan for someone who wants to get fit and lose weight. Include exercises, sets, and reps.",
#     run_config = config
# )

# print("\nCALLING AGENT...\n")
# print(result.final_output)


# chainlit 

@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="Welcome to the Fitness Assistant! How can I help you today?"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")
    history.append({
        "role": "user", 
        "content": message.content
    })

    result = await Runner.run_streamed(
        agent,
        input=message.content,
        run_config = config,
)
    history.append({
        "role": 'assistant',
        "content": result.final_output
    })
    cl.user_session.set("history", history)
    await cl.Message(
        content=result.final_output
    ).send()

        # msg = cl.Message(content = "")
    # await msg.send()

    # final_output = "" 
    # async for chunk in Runner.run_streamed(
    #     agent,
    #     input = "message.content",
    #     run_config = config
    # ):
    #     if chunk.final_output:
    #         final_output += chunk.final_output
    #         await msg.stream_token(
    #             chunk.final_output
    #         )
    # await msg.update()
    # history.append({
    #     "role": 'assistant',
    #     "content": final_output
    # })
    # cl.user_session.set("history", history)