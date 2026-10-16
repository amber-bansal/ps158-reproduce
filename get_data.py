"""Download the Federal Reserve's Survey of Consumer Finances (SCF) summary extracts.

The Fed publishes one "summary extract" per survey year (1989-2025, every three
years) as a zipped CSV. Since the 2025 release (October 9, 2026), every year's
file has its dollar values in 2025 dollars (CPI-U-RS), so the years can be
compared directly.

Source: https://www.federalreserve.gov/econres/scfindex.htm

Usage:
    python get_data.py            # downloads into data/raw/
    python get_data.py --force    # re-download even if the CSV already exists
"""

import argparse
import io
import zipfile
from pathlib import Path

import requests

BASE_URL = "https://www.federalreserve.gov/econres/files/scfp{year}excel.zip"
YEARS = list(range(1989, 2026, 3))  # 1989, 1992, ..., 2022, 2025
RAW_DIR = Path(__file__).parent / "data" / "raw"


def download_year(year, force=False):
    csv_name = f"SCFP{year}.csv"
    out_path = RAW_DIR / csv_name
    if out_path.exists() and not force:
        print(f"{year}: already have {out_path.relative_to(RAW_DIR.parent.parent)}")
        return out_path

    url = BASE_URL.format(year=year)
    print(f"{year}: downloading {url}")
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    payload = resp.content

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        # Extract only the expected CSV, by name, so nothing in the archive can
        # write outside data/raw/.
        members = {Path(n).name.lower(): n for n in zf.namelist()}
        member = members.get(csv_name.lower())
        if member is None:
            raise RuntimeError(f"{csv_name} not found in {url}; archive has {zf.namelist()}")
        out_path.write_bytes(zf.read(member))

    print(f"{year}: wrote {out_path.relative_to(RAW_DIR.parent.parent)}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--force", action="store_true", help="re-download existing files")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for year in YEARS:
        download_year(year, force=args.force)


if __name__ == "__main__":
    main()
