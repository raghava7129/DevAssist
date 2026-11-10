from .import sandbox
from .display import display
from . import session


COMMANDS = {
    '/sessions': 'open a previous session',
    '/goto': 'go back to the previous step',
}


def redraw(messages, label):
    display.clear()
    display.banner('linux')
    display.resumed(messages, label)
    display.replay(messages)
    return messages


def sessions(messages):
    saved = session.all_sessions()
    if not saved:
        display.note("no saved chats yet")
        return messages
    rows = [f'{s['id']} {s['title']}' for s in saved]
    pick = display.pick_idx('open chat', rows)
    if not pick:
        return messages
    return redraw(
        session.open_session(saved[pick]['id']),
        'opened'
    )


def preview(message):
    if message.get("tool_calls"):
        return "-> " + message["tool_calls"][0]["function"]["name"]
    return " ".join(str(message.get("content") or "").split())[:70]


def goto(messages):
    rows = [f"{m['role']:<9} {preview(m)}" for m in messages]
    choice = display.pick_idx("goto message", rows)
    if choice is None:
        return messages
    session.rewind_to(choice + 1)
    return redraw(messages[: choice + 1], "reverted back")


def cmd_handler(command, messages):
    if command == '/sessions':
        return sessions(messages)
    if command == '/goto':
        return goto(messages)


if __name__ == "__main__":
    from .test_msg import messages
    command = '/sessions'
    updated_messages = cmd_handler(command, messages)
    display.replay(updated_messages)