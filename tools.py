from .skills import read_skill

TODOS = []
TASK_STATUS_MAPPING = {
    "pending": "[ ]",
    "in_progress": "[~]",
    "done": "[x]"
}

def read_file(path: str) -> str:
    """Read a file and return its contents."""
    with open(path, "r") as f:
        return f.read()

def write_file(path: str, content: str) -> None:
    """Create a file, or overwrite it if it already exists."""
    with open(path, "w") as f:
        f.write(content)
    return f'Wrote to {path}'

def todos_prompt():
    return "\n".join(
        f"{TASK_STATUS_MAPPING[t['status']]} {t['content']}" for t in TODOS
    )

def write_todos(todos: str) -> None:
    """
    Record the plan for a multi-step task. Send the whole list everytime.
    Keep exactly one task in_progress and update it as you go.
    """

    active = [t for t in todos if t["status"] == "in_progress"]
    if len(active) > 1:
        return f"Error: {len(active)} tasks are in_progress. Only one task at a time is allowed."

    TODOS[:] = todos
    return todos_prompt() or "Todo list cleared."


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "read_skill": read_skill,
    "write_todos": write_todos
}