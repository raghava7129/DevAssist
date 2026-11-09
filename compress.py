import json
import tempfile
from pathlib import Path

from . import config

CAP = 10000
STUB = 300

SUMMARY = "<summary>"
TRIMMED = "[output trimmed:"
SPILLS = []

#   *************************************************************


def spill(text):
    handle = tempfile.NamedTemporaryFile(
        mode='w', prefix='DevAssist-',
        suffix='.txt', delete=False
    )
    handle.write(text)
    handle.close()
    SPILLS.append(Path(handle.name))
    return handle.name


def store_in_tempfile(text):
    if len(text) <= CAP:
        return text

    try:
        path = spill(text)
    except OSError:
        return (
            text[:CAP] + 
            f"\n\n{TRIMMED} {len(text) - CAP} chars cut and could not be saved.]"
        )

    return (
        text[:CAP] + f"\n\n{TRIMMED} {len(text) - CAP} of {len(text)} chars cut. "
        f"The whole output is at {path} - page through it with "
        "head, tail, sed -n or grep. It is deleted when this turn ends.]"
    )

def sweep():
    for path in SPILLS:
        path.unlink(missing_ok=True)
    SPILLS.clear()

#   ***************************************************************


def locked(messages):
    for i in range(len(messages) -1, -1, -1):
        if SUMMARY in (messages[i].get('content') or ''):
            return (i+1)
    return 0


def strip(messages):
    shrunk = 0
    for msg in messages[locked(messages):]:
        content = msg.get('content') or ''
        if msg['role'] != 'tool' or TRIMMED in content or len(content) <= STUB:
            continue

        msg['content'] = (
            content[:STUB] + f"\n\n{TRIMMED} {len(content) - STUB} chars cut. "
            "Run the command again to see the full output.]"
        )
        shrunk += 1
    return shrunk

#   ***************************************************************


def estimate(messages):
    return sum(len(json.dumps(m)) for m in messages) // 4

def remove_tool_output(messages):
    budget = config.CONTEXT_WINDOW * config.COMPACT_AT
    dropped = 0
    for message in messages[locked(messages):]:
        if estimate(messages) <= budget:
            break
        if (
            message["role"] == "tool" and
            TRIMMED not in (message.get("content") or "")
        ):
            message["content"] = f"{TRIMMED} dropped to fit the context window.]"
            dropped += 1
    return dropped


if __name__ == "__main__":
    msgs = [
        {"role": "user", "content": "read llm.py"},
        {"role": "tool", "tool_call_id": "call_1", "content": "x" * 8000},
    ]
    print('Before: ', len(msgs[1]['content']))
    strip(msgs)
    print('After: ', len(msgs[1]['content']))