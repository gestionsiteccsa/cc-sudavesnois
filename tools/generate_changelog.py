"""
Génère CHANGELOG.md depuis l'historique git.

Usage :
    python tools/generate_changelog.py [--stdout]

Comportement :
    - Conserve la section [Non publié] actuelle (entrées manuelles)
    - Parcourt tout le log git pour générer des sections par mois
    - Classe chaque commit par type (feat → Ajouté, fix → Corrigé, etc.)
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
CHANGELOG = REPO_DIR / "CHANGELOG.md"

FRENCH_MONTHS = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
}

TYPE_MAP: dict[str, str] = {
    "feat": "Ajouté",
    "feature": "Ajouté",
    "add": "Ajouté",
    "create": "Ajouté",
    "new": "Ajouté",
    "fix": "Corrigé",
    "bugfix": "Corrigé",
    "hotfix": "Corrigé",
    "correctif": "Corrigé",
    "refactor": "Modifié",
    "refacto": "Modifié",
    "update": "Modifié",
    "up": "Modifié",
    "change": "Modifié",
    "modification": "Modifié",
    "edit": "Modifié",
    "rename": "Modifié",
    "amelioration": "Modifié",
    "perf": "Performances",
    "performance": "Performances",
    "optimize": "Performances",
    "optim": "Performances",
    "optimisation": "Performances",
    "docs": "Documentation",
    "doc": "Documentation",
    "documentation": "Documentation",
    "readme": "Documentation",
    "chore": "Technique / Maintenance",
    "build": "Technique / Maintenance",
    "ci": "Technique / Maintenance",
    "deps": "Technique / Maintenance",
    "dep": "Technique / Maintenance",
    "style": "Technique / Maintenance",
    "css": "Technique / Maintenance",
    "test": "Technique / Maintenance",
    "tests": "Technique / Maintenance",
    "security": "Sécurité",
    "securite": "Sécurité",
    "secu": "Sécurité",
    "delete": "Supprimé",
    "remove": "Supprimé",
    "del": "Supprimé",
    "suppression": "Supprimé",
    "supp": "Supprimé",
}

SKIP_COMMIT_PATTERNS: list[str] = [
    r"^build\(css\)",
    r"^build\(static\)",
    r"^merge:?",
    r"^Merge branch",
    r"^first commit$",
    r"^fix \.$",
    r"^debug$",
    r"^wip",
]

SECTION_ORDER = [
    "Ajouté",
    "Modifié",
    "Corrigé",
    "Sécurité",
    "Performances",
    "Documentation",
    "Supprimé",
    "Technique / Maintenance",
]


def get_git_log() -> list[str]:
    result = subprocess.run(
        ["git", "log", "--format=%ad|%s", "--date=short", "--reverse"],
        capture_output=True,
        encoding="utf-8",
        check=True,
        cwd=REPO_DIR,
    )
    return [line for line in result.stdout.strip().split("\n") if line]


def classify_commit(msg: str) -> tuple[str | None, str]:
    for pattern in SKIP_COMMIT_PATTERNS:
        if re.match(pattern, msg, re.IGNORECASE):
            return None, msg

    m = re.match(r"^(\w+)(?:\(([^)]*)\))?:\s*(.*)", msg)
    if m:
        prefix = m.group(1).lower()
        scope = m.group(2)
        desc = m.group(3).strip()
        section = TYPE_MAP.get(prefix)
        if section:
            if scope:
                desc = f"**{scope}** : {desc}"
            return section, desc

    first_word = msg.split()[0].lower() if msg.split() else ""
    section = TYPE_MAP.get(first_word)
    if section:
        rest = " ".join(msg.split()[1:]).strip()
        return section, rest if rest else msg

    return None, msg


def format_month_key(dt: datetime) -> str:
    return f"{FRENCH_MONTHS[dt.month]} {dt.year}"


def read_existing_non_publie() -> str:
    if not CHANGELOG.exists():
        return ""
    content = CHANGELOG.read_text("utf-8")
    if "## [Non publié]" not in content:
        return ""
    parts = content.split("## [Non publié]", 1)
    remaining = parts[1].strip()
    m = re.search(r"^## ", remaining, re.MULTILINE)
    if m:
        return remaining[: m.start()].strip()
    return remaining.strip()


def build_commit_groups() -> dict[str, dict[str, list[str]]]:
    monthly: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    lines = get_git_log()
    for line in lines:
        if "|" not in line:
            continue
        date_str, msg = line.split("|", 1)
        msg = msg.strip()
        section, desc = classify_commit(msg)
        if section is None:
            continue
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            month_key = format_month_key(dt)
        except ValueError:
            month_key = date_str
        monthly[month_key][section].append(desc)
    return monthly


def month_sort_key(month_str: str) -> tuple:
    m = re.match(r"(\w+) (\d{4})", month_str)
    if not m:
        return (9999, 0)
    name_fr = m.group(1).lower()
    year = int(m.group(2))
    rev_map = {v.lower(): k for k, v in FRENCH_MONTHS.items()}
    return (year, rev_map.get(name_fr, 0))


def generate() -> str:
    non_publie = read_existing_non_publie()
    groups = build_commit_groups()
    sorted_months = sorted(groups.keys(), key=month_sort_key)

    lines: list[str] = ["# Changelog", ""]

    if non_publie:
        lines.append("## [Non publié]")
        lines.append("")
        lines.append(non_publie)
        lines.append("")

    for month in sorted_months:
        lines.append(f"## {month}")
        lines.append("")
        sections = groups[month]
        for section_name in SECTION_ORDER:
            items = sections.get(section_name)
            if not items:
                continue
            lines.append(f"### {section_name}")
            for desc in items:
                lines.append(f"- {desc}")
            lines.append("")

    return "\n".join(lines).strip() + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Génère CHANGELOG.md depuis les commits git"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Affiche sur stdout au lieu d'écraser CHANGELOG.md",
    )
    args = parser.parse_args()

    output = generate()
    if args.stdout:
        sys.stdout.buffer.write(output.encode("utf-8"))
    else:
        CHANGELOG.write_text(output, "utf-8")
        line_count = sum(1 for line in output.split(chr(10)) if line.strip())
        print(f"CHANGELOG.md genere ({line_count} lignes)")


if __name__ == "__main__":
    main()
