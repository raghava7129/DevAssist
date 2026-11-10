from .config import SYSTEM_PROMPT
from pathlib import Path

llm_file_path = Path(__file__).parent.resolve() / "llm.py"
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