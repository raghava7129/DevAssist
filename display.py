from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from rich.console import Console
from rich.padding import Padding
from rich.text import Text


HISTORY = Path.home() / ".agents" / "history"

STYLE = Style.from_dict({"prompt": "bold #f34b25"})

TOOL = "#5ade8a"


class Display():
    def __init__(self):
        self.console = Console()
        self.SESSION = None

    def clear(self):
        self.console.clear()

    def read(self, prompt='> '):
        self.SESSION
        if self.SESSION is None:
            HISTORY.parent.mkdir(parents=True, exist_ok=True)
            self.SESSION = PromptSession(
                history=FileHistory(str(HISTORY)),
                style=STYLE,
            )
        return self.SESSION.prompt(HTML(f"<prompt>{prompt}</prompt>"))

    def approve(self, reason):
        self.console.print(Padding(Text(reason, style=f"bold {TOOL}"), (1, 0, 0, 2)))
        try:
            answer = self.read("  allow? (y/n)> ").strip()
        except (EOFError, KeyboardInterrupt):
            return False
        return answer.lower().startswith("y")


display = Display()