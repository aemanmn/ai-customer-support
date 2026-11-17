import os
import re
from pathlib import Path

import psycopg
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def parse(path: Path) -> list[tuple[str, str, str]]:
    """Split a section file into (section, title, content) rows, one per ## heading."""
    text = path.read_text(encoding="utf-8")
    headings = list(re.finditer(r"^##[ \t]+(.+?)[ \t]*$", text, re.MULTILINE))
    if not headings:
        raise ValueError(f"No level-two headings found in {path}.")

    entries = []
    for index, heading in enumerate(headings):
        next_start = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        title = heading.group(1).strip()
        content = text[heading.end() : next_start].strip()
        if not content:
            raise ValueError(f"Entry {title!r} in {path} has no content.")
        entries.append((path.stem, title, content))
    return entries


def main() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL must be set in the environment or project .env file.")

    paths = sorted(KNOWLEDGE_BASE_DIR.glob("*.md"))
    if not paths:
        raise SystemExit(f"No Markdown files found in {KNOWLEDGE_BASE_DIR}.")

    section_entries = [(path, parse(path)) for path in paths]
    with psycopg.connect(database_url) as conn:
        for _, entries in section_entries:
            conn.cursor().executemany(
                """
                insert into knowledge_base (section, title, content)
                values (%s, %s, %s)
                on conflict (section, title) do update
                  set content = excluded.content, updated_at = now()
                """,
                entries,
            )

    for path, entries in section_entries:
        print(f"{path.stem}: {len(entries)} entries")


if __name__ == "__main__":
    main()
