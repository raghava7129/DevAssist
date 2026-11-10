import json
from pathlib import Path
from datetime import datetime


PROJECT = str(Path.cwd().resolve()).replace('/', '-')
SESSION_DIR = Path.home() / '.agents' / 'sessions' / PROJECT
CURRENT = datetime.now().strftime('%H%M%S-%d%m%Y')

DISK_MSG_IDX = 0

def get_session_path(session_id):
    return SESSION_DIR / f'{session_id}.jsonl'


def save(messages):
    global DISK_MSG_IDX
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    with get_session_path(CURRENT).open('a') as f:
        for message in messages[DISK_MSG_IDX:]:
            f.write(json.dumps(message) + '\n')
    DISK_MSG_IDX = len(messages)


def load(session_id):
    messages = []
    for line in get_session_path(session_id).read_text().splitlines():
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            pass
        if 'rewind_to' in entry:
            del messages[entry['rewind_to']:]
        elif 'compact' in entry:
            messages = list(entry['compacted'])
        else:
            messages.append(entry)
    return messages


def open_session(session_id):
    global DISK_MSG_IDX, CURRENT
    CURRENT = session_id
    messages = load(session_id)
    DISK_MSG_IDX = len(messages)
    return messages


def title(messages):
    for message in messages:
        if message["role"] == 'user':
            return (
                " ".join(
                    str(message.get('content') or ""
                ).split())[:50] + '...'
            )
    return "Untitled"


def all_sessions():
    if not SESSION_DIR.exists():
        return []
    files = sorted(
        SESSION_DIR.glob('*.jsonl'),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return [
        {
            'id': p.stem,
            'title': title(load(p.stem))
        } for p in files
    ]


def rewind_to(count):
    global WRITTEN
    with get_session_path(CURRENT).open("a") as f:
        f.write(json.dumps({"rewind_to": count}) + "\n")
    WRITTEN = count


if __name__ == '__main__':
    msgs = [
        {'role': 'user', 'content': 'hey how is it going?'},
        {'role': 'assistent', 'content': 'This msg should not appear.'},
        {'rewind_to': 1},
        {'role': 'user', 'content': 'Msg after rewind?'},
    ]

    save(msgs)
    all_sessions = all_sessions()
    print('msgs from latest session: ', open_session(all_sessions[0]['id']))