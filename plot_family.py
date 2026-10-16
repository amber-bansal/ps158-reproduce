"""Extension: median net worth of families with children, single parents vs. couples.

Same sample and dollars as plot.py, but median net worth grouped by family
structure instead of education.

  FAMSTRUCT  1 = not married or living with a partner, with child(ren)
             4 = married or living with a partner, with child(ren)
             (2, 3 and 5 are families without children, already excluded)

Output: figure_family.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from get_data import YEARS
from plot import (SAMPLE_LABEL, SURFACE, TEXT_PRIMARY, TEXT_SECONDARY,
                  load_year, style_axis, weighted_median)

OUT_PATH = Path(__file__).parent / "figure_family.png"

FAMILIES = {4: "Couple with children", 1: "Single parent"}

# Categorical slots 1 and 2 of the dataviz reference palette (light mode).
COLORS = {"Couple with children": "#2a78d6", "Single parent": "#eb6834"}


def compute_table():
    rows = []
    for year in YEARS:
        df = load_year(year, ["WGT", "FAMSTRUCT", "NETWORTH", "KIDS"])
        for code, family in FAMILIES.items():
            sub = df[df["FAMSTRUCT"] == code]
            rows.append({
                "year": year,
                "family": family,
                "median_networth": weighted_median(sub["NETWORTH"].to_numpy(), sub["WGT"].to_numpy()),
                "share_of_sample": sub["WGT"].sum() / df["WGT"].sum(),
                "n_records": len(sub),
            })
    table = pd.DataFrame(rows)
    wide = table.pivot(index="year", columns="family", values="median_networth")
    ratio = (wide["Couple with children"] / wide["Single parent"]).rename("ratio")
    return table, ratio


def plot(table, ratio):
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    fig.patch.set_facecolor(SURFACE)

    for family, color in COLORS.items():
        sub = table[table["family"] == family]
        y = sub["median_networth"] / 1000
        ax.plot(sub["year"], y, color=color, linewidth=2, marker="o", markersize=5,
                markeredgecolor=SURFACE, markeredgewidth=1.5, label=family)
        ax.annotate(f"{family}\n${y.iloc[-1]:,.0f}k", (sub["year"].iloc[-1], y.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center",
                    fontsize=9, color=TEXT_PRIMARY)
    style_axis(ax)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_formatter(lambda v, _: f"${v:,.0f}k")
    ax.set_title(f"Median net worth of {SAMPLE_LABEL}, 2025 dollars.\n"
                 f"Couples had {ratio.iloc[0]:.1f}× single parents' wealth in 1989, "
                 f"{ratio.min():.1f}× at the low ({ratio.idxmin()}), {ratio.iloc[-1]:.1f}× in 2025",
                 loc="left", fontsize=10, color=TEXT_PRIMARY)
    ax.legend(loc="upper left", frameon=False, fontsize=9, labelcolor=TEXT_PRIMARY)

    fig.subplots_adjust(top=0.84, bottom=0.15, right=0.84)
    fig.suptitle("Single parents and couples with children, 1989–2025",
                 x=0.125, y=0.96, ha="left", fontsize=13, fontweight="bold", color=TEXT_PRIMARY)
    fig.text(0.125, 0.02,
             "Source: Federal Reserve Survey of Consumer Finances, public summary extracts.\n"
             "Couple = married or living with a partner. Single parent = neither, with a child at home.",
             fontsize=7.5, color=TEXT_SECONDARY)
    return fig


def main():
    table, ratio = compute_table()
    wide = table.pivot(index="year", columns="family", values="median_networth") / 1000
    print(wide.join(ratio).round(1).to_string())

    plot(table, ratio).savefig(OUT_PATH, dpi=200, facecolor=SURFACE)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
