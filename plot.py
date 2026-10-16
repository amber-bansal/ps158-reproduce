"""Redraw the "Growing wealth gap" figure from the SCF summary extracts.

Mean net worth of families with a child at home, by education of the SCF
reference person (college degree vs. high school or less), 1989-2025, in 2025
dollars.

Definitions (from the Fed's bulletin macro, bulletin.macro.txt):
  EDCL      education of the reference person: 1 = no high school diploma,
            2 = high school diploma or GED, 3 = some college, 4 = college degree
  KIDS      number of children (incl. step- and foster children) in the household
  NETWORTH  total assets minus total debts, already in 2025 dollars in every
            year's file, so no further inflation adjustment is applied
  WGT       sampling weight, already divided by 5 so that pooling all five
            imputation replicates gives population totals

Output: figure.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from get_data import RAW_DIR, YEARS

OUT_PATH = Path(__file__).parent / "figure.png"

SAMPLE_LABEL = "families with a child at home"

GROUPS = {
    "BA or more": lambda edcl: edcl == 4,
    "HS or less": lambda edcl: edcl <= 2,
}

# Black and grey, as in the original figure.
COLORS = {"BA or more": "#1a1a1a", "HS or less": "#9a9a9a"}
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"
SURFACE = "#ffffff"
SHADE = "#f1f1f1"


def in_sample(df):
    return df["KIDS"] >= 1


def weighted_median(values, weights):
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cumulative = np.cumsum(weights)
    return values[np.searchsorted(cumulative, cumulative[-1] / 2)]


def load_year(year, columns):
    path = RAW_DIR / f"SCFP{year}.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} is missing; run get_data.py first")
    df = pd.read_csv(path, usecols=columns)
    return df[in_sample(df)]


def compute_table():
    rows = []
    for year in YEARS:
        df = load_year(year, ["WGT", "EDCL", "NETWORTH", "KIDS"])
        for group, select in GROUPS.items():
            sub = df[select(df["EDCL"])]
            rows.append({
                "year": year,
                "group": group,
                "mean_networth": np.average(sub["NETWORTH"], weights=sub["WGT"]),
            })
    return pd.DataFrame(rows)


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(TEXT_SECONDARY)
    ax.tick_params(colors=TEXT_SECONDARY, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xticks(YEARS)
    ax.set_xlim(YEARS[0] - 1, YEARS[-1] + 1)


def plot(table):
    fig, ax = plt.subplots(figsize=(8.5, 6))
    fig.patch.set_facecolor(SURFACE)

    # Shade the years added since Putnam (2015).
    ax.axvspan(2014.5, YEARS[-1] + 1, color=SHADE, zorder=0)
    ax.text(2015, 2_380, "Added since Putnam (2015)\n2016–2025", va="top",
            fontsize=8.5, color=TEXT_SECONDARY)

    for group, color in COLORS.items():
        sub = table[table["group"] == group]
        y = sub["mean_networth"] / 1000
        ax.plot(sub["year"], y, color=color, linewidth=2.5, label=group)
        ax.annotate(f"${y.iloc[-1]:,.0f}K", (sub["year"].iloc[-1], y.iloc[-1]),
                    xytext=(8, 0), textcoords="offset points", va="center",
                    fontsize=9, color=TEXT_PRIMARY, annotation_clip=False)
    style_axis(ax)
    ax.set_ylim(0, 2_400)
    ax.set_yticks(range(0, 2_401, 400))
    ax.yaxis.set_major_formatter(lambda v, _: f"${v * 1000:,.0f}")
    ax.set_ylabel("Mean family net worth", fontsize=10, fontweight="bold", color=TEXT_PRIMARY)
    ax.legend(loc="upper left", fontsize=10, labelcolor=TEXT_PRIMARY,
              frameon=True, edgecolor=GRID, bbox_to_anchor=(0.03, 0.97))

    fig.subplots_adjust(top=0.84, bottom=0.17, left=0.15, right=0.88)
    fig.text(0.04, 0.95, "Growing wealth gap", fontsize=15, fontweight="bold", color=TEXT_PRIMARY)
    fig.text(0.04, 0.905, "By parental education, in constant (2025) dollars, 1989–2025",
             fontsize=11, color=TEXT_PRIMARY)
    fig.text(0.04, 0.03,
             "Families with a child of the reference person living at home. Education of the SCF reference person.\n"
             "Dollar values as published by the Federal Reserve (2025 dollars, R-CPI-U-RS); no further adjustment.\n"
             "Source: Survey of Consumer Finances, Federal Reserve Board, https://www.federalreserve.gov/econres/scfindex.htm",
             fontsize=7.5, color=TEXT_SECONDARY)
    return fig


def main():
    table = compute_table()
    print((table.pivot(index="year", columns="group", values="mean_networth") / 1000).round(1).to_string())
    plot(table).savefig(OUT_PATH, dpi=200, facecolor=SURFACE)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
