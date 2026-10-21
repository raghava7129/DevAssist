from .skills import read_skill

TODOS = []
TASK_STATUS_MAPPING = {
    "pending": "[ ]",
    "in_progress": "[~]",
    "done": "[x]"
}

def read_file(path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File '{path}' not found."

def write_file(path: str, content: str) -> None:
    """Create a file, or overwrite it if it already exists."""
    with open(path, "w") as f:
        f.write(content)
    return f'Wrote to {path}'

def todos_prompt():
    return "\n".join(
        f"{TASK_STATUS_MAPPING[t['status']]} {t['content']}" for t in TODOS
    )

def write_todos(todos):
    """
    Record the plan for a multi-step task. Send the whole list everytime.
    Keep exactly one task in_progress and update it as you go.
    """

    active = [t for t in todos if t["status"] == "in_progress"]
    if len(active) > 1:
        return f"Error: {len(active)} tasks are in_progress. Only one task at a time is allowed."

    TODOS[:] = todos
    return todos_prompt() or "Todo list cleared."

Tool_Schema = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": read_file.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": write_file.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File to write"},
                    "content": {"type": "string", "description": "The full contents"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_skill",
            "description": read_skill.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the skill to open",
                    }
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_todos",
            "description": write_todos.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "todos": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "content": {
                                    "type": "string",
                                    "description": "The task, imperative: 'Fix the parser'",
                                },
                                "activeForm": {
                                    "type": "string",
                                    "description": "Present continuous: 'Fixing the parser'",
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "done"],
                                },
                            },
                            "required": ["content", "activeForm", "status"],
                        },
                    }
                },
                "required": ["todos"],
            },
        },
    }
]


TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "read_skill": read_skill,
    "write_todos": write_todos
}