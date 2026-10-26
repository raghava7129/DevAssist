import os
from .llm import call_llm

MAX_TURNS = 3


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
    pass