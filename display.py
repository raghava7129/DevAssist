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
from rich.markdown import Markdown


HISTORY = Path.home() / ".agents" / "history"

STYLE = Style.from_dict({"prompt": "bold #f34b25"})

TOOL = "#5ade8a"
MUTED = "#565f89"
ACCENT = "#7aa2f7"
USER = "#9ece6a"

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

    def user(self, text):
        self.console.print(
            Padding(
                Text(text.strip(), style=f"bold {USER}"),
                (1, 0, 0, 2)
            )
        )

    def agent(self, text):
        self.console.print(
            Padding(
                Group(
                    Text("agent", style=f"bold {ACCENT}"),
                    Padding(Markdown(text.strip()), (1, 0, 0, 0)),
                ),
                (1, 2, 0, 2),
            )
        )

    def view_tool_activity(self, name, args, result, nested=False):
        header = Text.assemble(
            (f'{name}   ', f'bold {TOOL}'),
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

    def banner(self, sandbox_name='None'):
        self.console.print()
        self.console.print(
            Rule(Text(" coding agent ", style=f"bold {ACCENT}"), style=MUTED)
        )
        self.console.print(
            Padding(
                Text(
                    f"sandbox: {sandbox_name}  ·  enter for a newline  ·  ctrl-d to exit",
                    style=MUTED
                ),
                (0, 0, 0, 2)
            )
        )

    def resumed(self, messages, label="resumed"):
        turns = sum(1 for m in messages if m["role"] == "user")
        self.console.print(
            Padding(
                Text(
                    f"{label} · {len(messages)} messages · {turns} turns",
                    style=MUTED
                ),
                (0, 0, 0, 2),
            )
        )

    def replay(self, messages):
        results = {
            m["tool_call_id"]: m["content"] for m in messages if m["role"] == "tool"
        }
        for message in messages:
            if message["role"] == "user":
                self.user(message["content"])
            elif message["role"] == "assistant":
                if message.get("content"):
                    self.agent(message["content"])
                for call in message.get("tool_calls") or []:
                    self.view_tool_activity(
                        call["function"]["name"],
                        json.loads(call["function"]["arguments"]),
                        results.get(call["id"], ""),
                    )


display = Display()


if __name__ == "__main__":
    from .config import SYSTEM_PROMPT

    llm_file_path = Path(__file__).parent / "llm.py"
    content = llm_file_path.read_text().splitlines()

    messages = [
        {
            'role': 'system',
            'content': SYSTEM_PROMPT
        },
        {
            'role': 'user',
            'content': 'hey can you print the contents of the /llm.py file ?'
        },
        {
            'role': 'assistant',
            'reasoning': 'We need to read /lll... Actually path is /home/raghs/llm.py? The user says "/llm.py". Probably file at project root named llm.py. Let\'s read.',
            'tool_calls': [
                {
                    'id': 'fc_63b8ce8c-17d2-4b4d-9035-7713191dd7f7',
                    'function': {'arguments': '{"path":"llm.py"}', 'name': 'read_file'}, 'type': 'function'
                }
            ]
        },
        {
            'role': 'assistant',
            'content': "```python\n" + "\n".join(content) + "\n```",
            'reasoning': 'We need to output the contents.'
        },
        {
            'role': 'user',
            'content': 'what is the purpose of this file ?'
        },
        {
            'role': 'assistant',
            'content': "Some random code.",
            'reasoning': 'The purpose of the file is to facilitate interaction with a language model and manage tool calls.'
        }
    ]

    display.banner('linux')
    display.resumed(messages, label="demo")

    display.replay(messages)