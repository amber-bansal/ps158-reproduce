# Growing wealth gap, 1989–2025

## Figure

`figure.png` reproduces the "Growing wealth gap" figure: **mean** net worth of
**families with a child at home**, by parental education (BA or more vs. high
school or less), in **2025 dollars**, extended through the 2025 survey. In 2025
the BA-or-more mean was $2,291k against $269k (8.5×), up from 4.7× in 1989.

`figure_family.png` is an extension: the same families, split into couples and
single parents (median net worth). The gap went from 8.9× in 1989 to 4.5× in
2019, then back up to 7.3× in 2025.

## Data

Federal Reserve [Survey of Consumer Finances](https://www.federalreserve.gov/econres/scfindex.htm),
public summary extract files for the 13 surveys from 1989 to 2025
(`https://www.federalreserve.gov/econres/files/scfp{year}excel.zip`).

- Values are already in 2025 dollars, so no further inflation adjustment is
  applied.
- "Parental education" is the SCF reference person's education (`EDCL`):
  BA or more = 4, HS or less = 1–2. Families with children have `KIDS >= 1`.
- Run on all families, the code reproduces the Fed's own published 2025 means
  and medians by education.

## Rerun

Tested with Python 3.13.

```bash
pip install pandas matplotlib requests
```

```bash
python get_data.py
```

```bash
python plot.py
```

```bash
python plot_family.py
```

`get_data.py` downloads about 340 MB into `data/raw/` (ignored by git).
`plot.py` writes `figure.png`; `plot_family.py` writes `figure_family.png`.
When the Fed releases a new survey it re-bases all files to that year's
dollars: rerun `python get_data.py --force` and expect the numbers to change.
