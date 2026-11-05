import json

from pathlib import Path

from contextlib import contextmanager

from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style

from rich.console import Console, Group
from rich.padding import Padding
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text


HISTORY = Path.home() / ".agents" / "history"

STYLE = Style.from_dict({"prompt": "bold #f34b25"})

TOOL = "#5ade8a"
MUTED = "#565f89"
ACCENT = "#7aa2f7"

MAX_TOOL_OUTPUT_LINES = 12


class Display():
    def __init__(self):
        self.console = Console()
        self.SESSION = None
        self.agg_stats = {}

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

    def show_context(self, context):
        self.console.print(
            Padding(
                Panel(
                    Text(context.strip(), style=MUTED),
                    title=Text("subagent's context", style=f"bold {ACCENT}"),
                    title_align="left",
                    border_style=ACCENT,
                    padding=(0, 1),
                ),
                (1, 2, 0, 4),
            )
        )

    @contextmanager
    def loading(self, label='working...'):
        with self.console.status(
            Text(label, style=MUTED), spinner="dots", spinner_style=ACCENT
        ):
            yield

    def usage(self, stats):
        for key, value in stats.items():
            self.agg_stats[key] = self.agg_stats.get(key, 0) + (value or 0)

        parts = " · ".join(
            f"{value:,} {key.replace('_tokens', '')}"
            for key, value in stats.items()
            if value
        )
        self.console.print(Padding(Text(parts, style=MUTED), (1, 0, 0, 2)))

    def view_tool_activity(self, name, args, result, nested=False):
        header = Text.assemble(
            (f'{name}', f'bold {TOOL}'),
            (self._format_args(args), MUTED)
        )
        self.console.print(
            Padding(
                Panel(
                    Group(
                        header, Rule(style=MUTED), self._format_result(result)
                    ),
                    border_style=MUTED,
                    padding=(0, 1),
                ),
                (1, 2, 0, 6 if nested else 2),
            )
        )

    def _format_args(self, args):
        if len(args) == 1:
            return str(next(iter(args.values())))
        return json.dumps(args)

    def _format_result(self, result):
        lines = result.strip().splitlines() or ["(no output)"]
        shown = lines[:MAX_TOOL_OUTPUT_LINES]
        body = Text("\n".join(shown), style=MUTED)
        hidden = len(lines) - len(shown)
        if hidden > 0:
            body.append(f"\n… {hidden} more lines", style=f"italic {TOOL}")
        return body


display = Display()