#!/usr/bin/env python3

import argparse
import datetime as dt
import os
import re
import sys
from typing import Dict, Tuple

NOTES_DIR = os.path.join(".rhizome", "notes")


def timestamp() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower())
    slug = slug.strip("-")
    return slug or "note"


def ensure_notes_dir() -> None:
    os.makedirs(NOTES_DIR, exist_ok=True)


def parse_front_matter(text: str) -> Tuple[Dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    lines = text.splitlines()
    metadata: Dict[str, str] = {}
    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx] == "---":
            end_index = idx
            break
        if ":" in lines[idx]:
            key, value = lines[idx].split(":", 1)
            metadata[key.strip()] = value.strip()

    if end_index is None:
        return {}, text

    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return metadata, body


def build_front_matter(metadata: Dict[str, str]) -> str:
    if not metadata:
        return ""
    content = ["---"]
    for key, value in metadata.items():
        content.append(f"{key}: {value}")
    content.append("---\n")
    return "\n".join(content)


def format_links(raw_links) -> str:
    if not raw_links:
        return ""
    links = []
    for item in raw_links:
        for part in item.split(","):
            clean = part.strip()
            if clean:
                links.append(f"[[{clean}]]")
    if not links:
        return ""
    return "Links: " + " ".join(links)


def read_stdin_if_needed(content_arg: str) -> str:
    if content_arg is not None:
        return content_arg.strip()
    if sys.stdin.isatty():
        return ""
    data = sys.stdin.read().strip()
    return data


def update_note(title: str, body: str, links_line: str) -> str:
    slug = slugify(title)
    path = os.path.join(NOTES_DIR, f"{slug}.md")
    now = timestamp()

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            existing = fh.read()
        metadata, existing_body = parse_front_matter(existing)
        metadata.setdefault("title", title)
        metadata["updated"] = now
        addition_lines = []
        addition_lines.append(f"## {now}")
        if body:
            addition_lines.append(body)
        if links_line:
            addition_lines.append(links_line)
        addition = "\n\n".join(line for line in addition_lines if line)
        new_body = existing_body.rstrip()
        if new_body:
            new_body += "\n\n"
        new_body += addition
    else:
        metadata = {"title": title, "created": now, "updated": now}
        initial_lines = [f"# {title}", f"## {now}"]
        if body:
            initial_lines.append(body)
        if links_line:
            initial_lines.append(links_line)
        new_body = "\n\n".join(line for line in initial_lines if line)

    with open(path, "w", encoding="utf-8") as fh:
        fm = build_front_matter(metadata)
        if fm:
            fh.write(fm)
        fh.write(new_body.strip() + "\n")

    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or update associative memory notes under .rhizome/notes."
    )
    parser.add_argument(
        "title",
        help="Title of the note. Determines the filename and display header.",
    )
    parser.add_argument(
        "-c",
        "--content",
        help="Content to add. If omitted, the script will read from STDIN.",
    )
    parser.add_argument(
        "-l",
        "--link",
        action="append",
        dest="links",
        help="Associative links (repeatable or comma separated).",
    )
    args = parser.parse_args()

    ensure_notes_dir()
    body = read_stdin_if_needed(args.content)
    links_line = format_links(args.links)
    path = update_note(args.title, body, links_line)
    print(f"Updated note: {path}")


if __name__ == "__main__":
    main()
