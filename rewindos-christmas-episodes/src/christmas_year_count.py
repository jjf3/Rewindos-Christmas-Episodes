from __future__ import annotations

import re
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup


URL = "https://en.wikipedia.org/wiki/List_of_United_States_Christmas_television_episodes"

# Finds a 4-digit year like 1998, 2006, 2023, etc.
YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")
# Often dates are in parentheses like (December 17, 2006)
DATE_PARENS_RE = re.compile(r"\(([^)]*\b(19\d{2}|20\d{2})\b[^)]*)\)")

ANIM_HEADING_RE = re.compile(r"\b(animation|animated)\b", re.I)


def repo_root() -> Path:
    # assumes script is in repo_root/src/
    return Path(__file__).resolve().parents[1]


def extract_year(text: str) -> int | None:
    """Try to pull a year from an air-date parenthetical, else any year in the text."""
    m = DATE_PARENS_RE.search(text)
    if m:
        y = YEAR_RE.search(m.group(1))
        if y:
            return int(y.group(1))

    y = YEAR_RE.search(text)
    return int(y.group(1)) if y else None


def main() -> None:
    root = repo_root()
    data_dir = root / "data"
    out_dir = root / "outputs"
    data_dir.mkdir(exist_ok=True)
    out_dir.mkdir(exist_ok=True)

    # PROOF FILE: guarantees you can see *something* was written
    proof = out_dir / "it_ran.txt"
    proof.write_text(f"Script executed from: {Path.cwd()}\nScript path: {Path(__file__).resolve()}\n",
                     encoding="utf-8")
    print("[OK] Wrote proof file:", proof)

    print("[INFO] Downloading:", URL)
    r = requests.get(
        URL,
        headers={"User-Agent": "RewindOS-Christmas/1.0 (personal project)"},
        timeout=30,
    )
    r.raise_for_status()
    print("[OK] Downloaded bytes:", len(r.text))

    soup = BeautifulSoup(r.text, "lxml")

    # Wikipedia article content usually lives under this wrapper
    wrapper = soup.select_one("#mw-content-text .mw-parser-output")
    if not wrapper:
        raise RuntimeError("Could not find #mw-content-text .mw-parser-output — page structure changed?")

    rows = []
    in_animation = False
    total_li = 0
    li_with_year = 0

    for node in wrapper.find_all(["h2", "h3", "h4", "li"], recursive=True):
        if node.name in ("h2", "h3", "h4"):
            heading = node.get_text(" ", strip=True)
            # Toggle animation mode based on heading text
            if ANIM_HEADING_RE.search(heading):
                in_animation = True
            else:
                in_animation = False
            continue

        if node.name == "li":
            total_li += 1
            text = node.get_text(" ", strip=True)

            year = extract_year(text)
            if year is None:
                continue

            li_with_year += 1
            rows.append({
                "year": year,
                "in_animation_section": in_animation,
                "entry": text
            })

    print("[INFO] Total <li> items scanned:", total_li)
    print("[INFO] <li> items that contained a year:", li_with_year)
    print("[INFO] Rows captured (before filtering):", len(rows))

    df = pd.DataFrame(rows)
    if df.empty:
        print("[WARN] No rows captured. Check network access or page structure.")
        return

    # FILTERS:
    # 1) remove animation sections
    df_filt = df[df["in_animation_section"] == False].copy()

    # 2) remove obvious holiday specials (simple keyword heuristic)
    #    You can tune this list later.
    specials_keywords = [
        "christmas special", "holiday special", "special presentation",
        "tv special", "television special"
    ]
    pat = re.compile("|".join(re.escape(k) for k in specials_keywords), re.I)
    df_filt = df_filt[~df_filt["entry"].str.contains(pat, na=False)]

    print("[INFO] Rows after filtering:", len(df_filt))

    # Count by year
    counts = df_filt.groupby("year").size().sort_values(ascending=False)

    top_year = int(counts.index[0])
    top_count = int(counts.iloc[0])

    print("\n[RESULT] Top 10 years:")
    print(counts.head(10))
    print(f"\n[RESULT] Year with the most Christmas episodes (filtered): {top_year} ({top_count})")

    # Save outputs
    out_all = data_dir / "wiki_christmas_entries_all.csv"
    out_filtered = data_dir / "wiki_christmas_entries_filtered.csv"
    out_counts = data_dir / "wiki_christmas_counts_by_year.csv"
    out_png = out_dir / "wiki_christmas_counts_by_year.png"

    df.to_csv(out_all, index=False)
    df_filt.to_csv(out_filtered, index=False)
    counts.to_csv(out_counts, header=["count"])

    print("[OK] Wrote:", out_all)
    print("[OK] Wrote:", out_filtered)
    print("[OK] Wrote:", out_counts)

    # Chart
    ax = counts.sort_index().plot(kind="bar", figsize=(14, 5), title="US Christmas TV Episodes by Year (filtered)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    fig = ax.get_figure()
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    print("[OK] Wrote chart:", out_png)


if __name__ == "__main__":
    main()
