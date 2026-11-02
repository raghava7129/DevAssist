import tempfile
from pathlib import Path

CAP = 10000

TRIMMED = "[output trimmed:"
SPILLS = []

#   *************************************************************


def spill(text):
    handle = tempfile.NamedTemporaryFile(
        mode='w', prefix='DevAssist-',
        suffix='.txt', delete=False
    )
    handle.write(text)
    handle.close()
    SPILLS.append(Path(handle.name))
    return handle.name


def cap(text):
    if len(text) <= CAP:
        return text

    try:
        path = spill(text)
    except OSError:
        return (
            text[:CAP] + 
            f"\n\n{TRIMMED} {len(text) - CAP} chars cut and could not be saved.]"
        )

    return (
        text[:CAP] + f"\n\n{TRIMMED} {len(text) - CAP} of {len(text)} chars cut. "
        f"The whole output is at {path} - page through it with "
        "head, tail, sed -n or grep. It is deleted when this turn ends.]"
    )

def sweep():
    for path in SPILLS:
        path.unlink(missing_ok=True)
    SPILLS.clear()