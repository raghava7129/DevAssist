import os

MAX_TURNS = 3

SUBAGENT_SYSTEM_PROMPT = f"""
You are an exploration subagent. You were given one question by a lead agent
and you answer it.

You cannot see the conversation that spawned you, and the lead agent cannot
see anything you do here. Only your final message crosses back, so it has to
stand on its own.

You are working in {os.getcwd()}. Search inside it. Never search from / or
from the home directory.

How to work:
    - Use bash, read_file and read_skill to find out what is actually true.
    Prefer rg, grep and find to guess at where things live.
    - You are here to read and report, not to change anything. Do not write or
    edit files, and do not run commands with side effects.
    - Search in batches. Several greps in one turn beats one grep per turn.
    - Stop as soon as you can answer. Do not keep looking to be thorough.

Your final message is the entire report, and it is the only thing that costs
the lead agent anything - so keep it short. Aim for under 200 words. Findings
only: file paths with line numbers, names, values. No preamble, no restating
the question, no long code blocks - cite the path and line and let the lead
agent open it. Say plainly what you could not find.
"""

RESTRICTED_TOOLS = ['write_file', 'write_todos', 'subagent']


def toolset():
    from .tools import Tool_Schema
    return [s for s in Tool_Schema if s['function']['name'] not in RESTRICTED_TOOLS]


def subagent(description: str) -> str:
    """
    Hand a self-contained exploration question to a fresh agent that
    has its own context window, and get back its findings. Use this
    to learn how the codebase works - tracing behaviour, locating
    where something is implemented, surveying files - so the search
    costs you one answer instead of dozens of tool results. It cannot
    see this conversation, so include every detail it needs. It reads
    and reports; it never edits.
    """
    from .llm import call_llm
    from .display import display
    from .compress import remove_tool_output
    from .tools import execute_tool_call

    display.show_context(description)

    messages = [
        {"role": "system", "content": SUBAGENT_SYSTEM_PROMPT},
        {"role": "user", "content": description},
    ]

    report = None

    for _ in range(MAX_TURNS):
        remove_tool_output(messages)

        with display.loading('subagent working...'):
            message, usage = call_llm(messages, tools=toolset())

        messages.append(message.model_dump(exclude_none=True))
        display.usage(usage)
        report = message.content or report

        if not message.tool_calls:
            return report or "(subagent didn't find anything.)"

        for tool_call in message.tool_calls:
            args, result = execute_tool_call(tool_call)
            display.view_tool_activity(
                tool_call.function.name, args, result, nested=True
            )
            messages.append({
                "role": 'tool',
                "tool_call_id": tool_call.id,
                "content": result
            })

    if report:
        return  (
            f'(SUBAGENT HAS DONE {MAX_TURNS} TURNS, BEFORE FINISHING.'
            f'PARTIAL FINDINGS ARE AS BELOW - NARROW THE QUESTION AND ASK AGAIN IF NEEDED.)'
            f'\n\n{report}'
        )
    return  {
        f'SUBAGENT HAS DONE {MAX_TURNS} TURNS AND FOUND NOTHING.'
    }


if __name__ == '__main__':
    subagent(
        'can you read and print the llm.py file?'
    )