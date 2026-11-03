"""Build data.json and data.csv for the chart from the checked CSVs in data/.

Stops if any check fails. Run from the project folder: python3 scripts/build.py
"""
import csv, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"

def rows(name):
    with open(D / name) as f:
        return list(csv.DictReader(f))

def check(ok, msg):
    if not ok:
        sys.exit("CHECK FAILED: " + msg)

# Yearly totals, 1960-2025 (Rent Guidelines Board)
yearly = {int(r["year"]): int(r["nyc_total"]) for r in rows("completions_1960_2025.csv")}
check(sorted(yearly) == list(range(1960, 2026)), "1960-2025 must be complete")
for r in rows("completions_1960_2025.csv"):
    parts = sum(int(r[k]) for k in ["bronx", "brooklyn", "manhattan", "queens", "staten_island"])
    check(parts == int(r["nyc_total"]), f"boroughs do not add up in {r['year']}")

# Decade totals (City Planning, via Where We Live NYC 2025)
dec = {r["decade"]: int(r["homes_completed"]) for r in rows("completions_by_decade_dcp.csv")}
check(dec["1920s"] == 729000, "1920s decade total")

# Yearly sums must sit close to the decade totals where both exist
for d0 in (1960, 1970, 1980, 1990, 2000, 2010):
    s = sum(yearly[y] for y in range(d0, d0 + 10))
    gap = abs(s - dec[f"{d0}s"]) / dec[f"{d0}s"]
    check(gap < 0.02, f"{d0}s yearly sum {s} is {gap:.1%} off the decade total")

# Apartments in tenements, 1920-1928 (State Board of Housing)
ten = {int(r["year"]): int(r["apartments_completed"]) for r in rows("completions_1920_1928_tenements.csv")}
check(sum(ten.values()) == 382670, "tenement total must match the printed 382,670")

stock = [r for r in rows("stock_by_decade_pluto.csv") if r["decade_built"] != "unknown"]

bars = []
for d0 in (1920, 1930, 1940, 1950):
    avg = dec[f"{d0}s"] / 10
    for y in range(d0, d0 + 10):
        bars.append({"y": y, "v": round(avg), "kind": "avg"})
for y in range(1960, 2026):
    bars.append({"y": y, "v": yearly[y], "kind": "year"})

out = {
    "bars": bars,
    "decades": {k: v for k, v in dec.items()},
    "peak1927": 107185,
    "tenements": [{"y": y, "v": v} for y, v in sorted(ten.items())],
    "stock": [{"d": r["decade_built"], "v": int(r["residential_units"]), "s": float(r["share"])} for r in stock],
    "stockTotal": sum(int(r["residential_units"]) for r in rows("stock_by_decade_pluto.csv")),
}
(ROOT / "data.json").write_text(json.dumps(out, separators=(",", ":")))

with open(ROOT / "data.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["year", "homes_completed", "what_it_is", "source"])
    for b in bars:
        if b["kind"] == "avg":
            w.writerow([b["y"], b["v"], "decade total divided by 10 (yearly counts for all homes not found)",
                        "NYC Department of City Planning, via Where We Live NYC 2025, Appendix A, Figure 5.73"])
        else:
            src = ("Rent Guidelines Board, Housing NYC: Rents, Markets and Trends 2006, Appendix G.3"
                   if b["y"] < 1967 else "Rent Guidelines Board, 2026 Housing Supply Report, Appendix 4")
            w.writerow([b["y"], b["v"], "homes completed that year", src])
    w.writerow([1927, 107185, "homes completed that year",
                "Rent Guidelines Board, An Introduction to the NYC Rent Guidelines Board (Nov. 2025), Table II"])
    for y, v in sorted(ten.items()):
        w.writerow([y, v, "apartments completed in buildings for three or more families only",
                    "Report of the State Board of Housing, 1928-29, Table VI"])

print(f"ok: {len(bars)} bars, data.json {len(json.dumps(out))} bytes")
