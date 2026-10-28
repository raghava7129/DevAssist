from pathlib import Path

PROJECT = Path.cwd().resolve()


def inside_project_dir(path):
    return PROJECT in Path(path).resolve().parents


def is_bash_allowed(command):
    return "ask"


def check_permissions(name, args):
    """Return (action, reason). Action is allow, ask or deny."""
    if name == "bash":
        return (
            is_bash_allowed(args["command"]),
            f"run: {args['command']}"
        )

    if (
        name == 'write_file' and not
        inside_project_dir(args["path"])
    ):
        return (
            "ask",
            f"{name} outside {PROJECT}: {args['path']}"
        )

    return "allow", None