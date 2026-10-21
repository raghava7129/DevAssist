import yaml

from pathlib import Path


SKILLS_DIR = [
    Path.cwd() / "agents/skills",
    Path.home() / "agents/skills",
]


def find_skills():
    skills = {}
    for dir in SKILLS_DIR:
        if not dir.exists():
            continue
        for file_name in sorted(dir.glob("*/SKILL.md")):
            _, front_matter, _ = file_name.read_text().split("---", 2)
            meta = yaml.safe_load(front_matter)
            description = " ".join(meta["description"].split())
            skills[meta["name"]] = {"description": description, "path": file_name}
    return skills


SKILLS = find_skills()


def skills_prompt():
    return "\n".join(
        f"- {name}: {s['description']}" for name, s in SKILLS.items()
    )


def read_skill(name: str) -> str:
    """Open a skill by name and return its full instructions."""
    if name not in SKILLS:
        raise ValueError(f"Skill '{name}' not found.")
    return SKILLS[name]["path"].read_text()