# Christmas Episodes Trend (1947–2025)
This RewindOS mini-project analyzes U.S. Christmas-themed television episodes over time to explore whether holiday episodes are still as prevalent in the modern era of shorter seasons and higher show churn.

Using the Wikipedia list of U.S. Christmas television episodes as a starting dataset, this project:
- Scrapes and extracts entries containing air-date years
- Filters out standalone holiday specials and animation sections (heuristic-based)
- Produces a year-by-year count of Christmas-themed episodes
- Exports CSV outputs and a chart for quick inspection

## Outputs
- `outputs/it_ran.txt` (proof the script executed + paths)
- `data/wiki_christmas_entries_all.csv`
- `data/wiki_christmas_entries_filtered.csv`
- `data/wiki_christmas_counts_by_year.csv`
- `outputs/wiki_christmas_counts_by_year.png`

## Notes / Disclaimer
This dataset is derived from a community-edited Wikipedia page and uses simple heuristics to filter entries. Results should be treated as a directional indicator, not a definitive census.

Keywords: cultural analytics, TV history, holiday programming, RewindOS, media data journalism
