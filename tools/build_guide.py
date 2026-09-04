#!/usr/bin/env python3
"""Generate the public usage guide from the Tina app's string catalog.

The guide shown in the app (UsageGuideView.swift) and the guide on the website
are the same seven topics in the same five languages. Rather than keep a second
copy of that prose here, where it would quietly drift, this script reads the
catalog that the app itself ships and writes the HTML.

The English text IS the catalog key, so the TOPICS table below holds the English
source strings verbatim. If someone edits the English copy in Swift, the key
renames, this script fails loudly on the missing key, and that is the signal to
update the table rather than to publish stale text.

Usage:
    tools/build_guide.py [path/to/Localizable.xcstrings]

Default path assumes the private app repo sits beside this one:
    ../Tina/Pantrio/Resources/Localizable.xcstrings
"""

from __future__ import annotations

import html
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO.parent / "Tina" / "Pantrio" / "Resources" / "Localizable.xcstrings"
OUT_ROOT = REPO / "public" / "guide"

# Order matters: it is the order the app shows them in.
PAGE_TITLE_KEY = "How to use Tina"
TOPICS = [
    (
        "spaces",
        "Your home, in spaces",
        "A space is a place your items live: the kitchen, the pantry, the basement, a bathroom cabinet. Everything you keep at home goes into one of them, with an amount.",
    ),
    (
        "swipes",
        "Swipe an item left or right",
        "Swipe an item right to put it straight on your shopping list. Swipe it left to reach Move, Edit and Delete. Tap its name to read the note.",
    ),
    (
        "quantities",
        "Amounts and running low",
        "Tap − and + to change an amount, or tap the number between them to type an exact one like 1.5. You can give every item the smallest amount you want to keep at home; reach it and the item joins your shopping list on its own, ready to stock up again.",
    ),
    (
        "all-items",
        "All your items on one page",
        "In Spaces, under All items, one page shows every item you keep at home with the total amount of each. If an item is in more than one space, tap it: you'll see every space it is in, and can change its amount in each one right there.",
    ),
    (
        "shopping",
        "Everything you need to buy",
        "The Shopping tab holds your shopping list. Pressing the button on the right takes a product off the list; once you are home, you add it back to your spaces however you like. The same product measured differently — 1 L of milk and 2 bottles of milk — stays two separate products, because they are two different things to buy.",
    ),
    (
        "scanning",
        "Scan instead of typing",
        "Tap the barcode button to scan a product. If you already stock it, Tina asks how many you bought and adds them. If you don't, it fills the name in for you to confirm — and remembers what your household calls that code.",
    ),
    (
        "sharing",
        "Everyone's list, live",
        "Invite the people you live with from Settings and you share the same spaces, items and list. Every change updates in the app in real time.",
    ),
]

# language code -> (html lang attribute, name in that language, path segment)
LANGUAGES = [
    ("en", "English", ""),
    ("it", "Italiano", "it"),
    ("de", "Deutsch", "de"),
    ("es", "Español", "es"),
    ("fr", "Français", "fr"),
]

# Only these need translating; everything else on the page comes from the catalog.
CHROME = {
    "en": {"back": "Back to Tina", "intro": "Everything Tina does, and the few things the app does not say out loud."},
    "it": {"back": "Torna a Tina", "intro": "Tutto quello che fa Tina, comprese le poche cose che l’app non dice apertamente."},
    "de": {"back": "Zurück zu Tina", "intro": "Alles, was Tina kann – auch das, was die App nicht von selbst erklärt."},
    "es": {"back": "Volver a Tina", "intro": "Todo lo que hace Tina, incluidas las pocas cosas que la app no dice en voz alta."},
    "fr": {"back": "Retour à Tina", "intro": "Tout ce que fait Tina, y compris les rares choses que l’app n’explique pas d’elle-même."},
}


def load_catalog(path: pathlib.Path) -> dict:
    if not path.exists():
        sys.exit(
            f"error: string catalog not found at {path}\n"
            "Pass the path explicitly: tools/build_guide.py <path to Localizable.xcstrings>"
        )
    return json.loads(path.read_text(encoding="utf-8"))["strings"]


def translate(strings: dict, key: str, lang: str) -> str:
    """English is the key itself; every other language comes from the catalog."""
    if key not in strings:
        sys.exit(
            f"error: key not in catalog: {key!r}\n"
            "The English copy in UsageGuideView.swift probably changed, which renames the key. "
            "Update TOPICS in this script to match before regenerating."
        )
    if lang == "en":
        return key
    unit = strings[key].get("localizations", {}).get(lang, {}).get("stringUnit")
    if not unit or not unit.get("value"):
        sys.exit(f"error: {key!r} has no {lang} translation. Run xcstringstool sync and translate it first.")
    return unit["value"]


def lang_switcher(current: str) -> str:
    links = []
    for code, name, seg in LANGUAGES:
        href = "/guide/" if seg == "" else f"/guide/{seg}/"
        if code == current:
            links.append(f'<span class="lang-current" aria-current="true">{html.escape(name)}</span>')
        else:
            links.append(f'<a href="{href}" hreflang="{code}">{html.escape(name)}</a>')
    return '<nav class="lang-switch">' + "\n      ".join(links) + "</nav>"


def alternates(current: str) -> str:
    out = []
    for code, _name, seg in LANGUAGES:
        href = "https://tinapantry.app/guide/" if seg == "" else f"https://tinapantry.app/guide/{seg}/"
        out.append(f'<link rel="alternate" hreflang="{code}" href="{href}">')
    out.append('<link rel="alternate" hreflang="x-default" href="https://tinapantry.app/guide/">')
    return "\n  ".join(out)


def render(strings: dict, lang: str) -> str:
    title = translate(strings, PAGE_TITLE_KEY, lang)
    chrome = CHROME[lang]
    depth_prefix = "/"  # absolute paths, so nesting depth does not matter

    cards = []
    for topic_id, title_key, body_key in TOPICS:
        t = html.escape(translate(strings, title_key, lang))
        b = html.escape(translate(strings, body_key, lang))
        cards.append(
            f'    <section class="guide-topic" id="{topic_id}">\n'
            f"      <h2>{t}</h2>\n"
            f"      <p>{b}</p>\n"
            f"    </section>"
        )

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} — Tina</title>
  <meta name="description" content="{html.escape(chrome['intro'])}">
  {alternates(lang)}
  <link rel="stylesheet" href="{depth_prefix}style.css">
</head>
<body>
  <header class="site-header">
    <span class="mark" role="img" aria-label="Tina raccoon">🦝</span>
    <a class="wordmark" href="{depth_prefix}">Tina</a>
  </header>

  <main class="container guide">
    <h1>{html.escape(title)}</h1>
    <p class="guide-intro">{html.escape(chrome['intro'])}</p>
    {lang_switcher(lang)}

{chr(10).join(cards)}

    <a class="back" href="{depth_prefix}">← {html.escape(chrome['back'])}</a>
  </main>

  <footer class="site-footer">
    <nav>
      <a href="{depth_prefix}privacy.html">Privacy</a> ·
      <a href="{depth_prefix}terms.html">Terms</a> ·
      <a href="mailto:fdrc.tech@gmail.com">Support</a>
    </nav>
    <div>© 2026 Tina</div>
  </footer>
</body>
</html>
"""


def main() -> None:
    catalog_path = pathlib.Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else DEFAULT_CATALOG
    strings = load_catalog(catalog_path)

    written = []
    for lang, _name, seg in LANGUAGES:
        out_dir = OUT_ROOT if seg == "" else OUT_ROOT / seg
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "index.html"
        out_file.write_text(render(strings, lang), encoding="utf-8")
        written.append(out_file.relative_to(REPO))

    print(f"Read {catalog_path}")
    for w in written:
        print(f"  wrote {w}")
    print(f"{len(TOPICS)} topics × {len(LANGUAGES)} languages")


if __name__ == "__main__":
    main()
