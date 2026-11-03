# A century of New York homebuilding

Two charts: homes completed in New York City each year from 1920 to 2025, with the 1920s tax exemption, 421-a and 485-x marked, and today's homes by the decade they were built.

- `index.html` draws both charts from `data.json`. Add `?embed=1` to the URL to drop the card border for a Ghost iframe embed.
- `scripts/build.py` checks the source CSVs in `data/` and writes `data.json` and `data.csv`. It stops if a check fails.
- `methodology.html` lists every source and calculation; `docs/how-we-built-this.html` explains the steps and key decisions.
