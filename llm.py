import os
import json
from dotenv import load_dotenv

from groq import Groq

from . import config
from .tools import TOOLS, Tool_Schema


load_dotenv()

groq_client = Groq()


def call_llm(msg, tools=None):
    response = groq_client.chat.completions.create(
        messages=msg,
        model = os.getenv("model", 'openai/gpt-oss-120b'),
        temperature=0.5,
        tools=tools or Tool_Schema
    )
    message = response.choices[0].message

    completion_details = response.usage.completion_tokens_details
    prompt_details = response.usage.prompt_tokens_details

    usage = {
        "prompt_tokens": response.usage.prompt_tokens,
        "completion_tokens": response.usage.completion_tokens,
        "reasoning_tokens": getattr(completion_details, "reasoning_tokens", None),
        "cached_tokens": getattr(prompt_details, "cached_tokens", None),
    }

    return message, usage


if __name__ == "__main__":
    user_input = input("What's on your mind?> ")

    message, usage = call_llm([
        {"role": "system", "content": config.SYSTEM_PROMPT},
        {"role": "user", "content": user_input},
    ])

    print("\nAgent: ", message.content, "\n")

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = TOOLS[tool_call.function.name](**args)
        print("Tool: ", tool_call.function.name, args)
        print(result, "\n")

    print(usage)