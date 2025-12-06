"""
Background worker to refresh cached financial data.

This script fetches fresh data from APIs and stores it in parquet files
for fast loading by the dashboard. Run this periodically (daily/weekly)
via cron job or task scheduler.

Usage:
    uv run python scripts/refresh_data.py [--sector SECTOR] [--all]
"""

import argparse
import os
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

# Suppress Streamlit warnings when running outside Streamlit context
os.environ["STREAMLIT_RUNTIME_SCRIPT_RUN_CTX"] = "1"
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
warnings.filterwarnings("ignore", message=".*No runtime found.*")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.ratio_calculator import (  # noqa: E402
    _fetch_sector_peer_data,
    _load_sector_tickers,
)


def refresh_sector_data(sector: str, delay: float = 1.0) -> bool:
    """
    Refresh data for a single sector and save to parquet file.

    Args:
        sector: Sector name to refresh
        delay: Delay in seconds before fetching to avoid rate limits

    Returns:
        bool: True if successful, False otherwise
    """
    print(f"📊 Refreshing {sector} sector data...")
    time.sleep(delay)

    try:
        # Fetch fresh data from API
        sector_df = _fetch_sector_peer_data(sector)

        if sector_df is None or sector_df.empty:
            print(f"⚠️  No data returned for {sector}")
            return False

        # Add metadata
        sector_df["last_updated"] = datetime.now()

        # Save to parquet (efficient columnar format)
        output_dir = Path(__file__).parent.parent / "data" / "sector_data"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{sector}.parquet"
        sector_df.to_parquet(output_file, index=False, compression="snappy")

        print(
            f"✅ Saved {len(sector_df)} companies to {output_file.name} "
            f"({output_file.stat().st_size / 1024:.1f} KB)"
        )
        return True

    except Exception as e:
        print(f"❌ Error refreshing {sector}: {e}")
        return False


def refresh_all_sectors(delay: float = 1.0) -> dict:
    """
    Refresh data for all sectors.

    Args:
        delay: Delay in seconds between sector requests

    Returns:
        dict: Status of each sector refresh
    """
    sector_tickers = _load_sector_tickers()
    sectors = list(sector_tickers.keys())

    print(f"🔄 Starting data refresh for {len(sectors)} sectors...")
    print(f"⏱️  Estimated time: {len(sectors) * delay / 60:.1f} minutes\n")

    results = {}
    start_time = time.time()

    for i, sector in enumerate(sectors, 1):
        print(f"[{i}/{len(sectors)}] ", end="")
        success = refresh_sector_data(sector, delay=delay)
        results[sector] = "success" if success else "failed"

    elapsed = time.time() - start_time
    successful = sum(1 for v in results.values() if v == "success")

    print(f"\n{'=' * 60}")
    print("✨ Refresh complete!")
    print(f"   Successful: {successful}/{len(sectors)} sectors")
    print(f"   Time taken: {elapsed / 60:.1f} minutes")
    print(f"{'=' * 60}")

    return results


def main():
    """Main entry point for data refresh script."""
    parser = argparse.ArgumentParser(description="Refresh cached financial data for InvestiLearn")
    parser.add_argument(
        "--sector",
        type=str,
        help="Refresh specific sector only",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Refresh all sectors (default)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay in seconds between API requests (default: 1.0)",
    )

    args = parser.parse_args()

    print("🚀 InvestiLearn Data Refresh Worker")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if args.sector:
        # Refresh specific sector
        success = refresh_sector_data(args.sector, delay=args.delay)
        sys.exit(0 if success else 1)
    else:
        # Refresh all sectors
        results = refresh_all_sectors(delay=args.delay)
        failed = sum(1 for v in results.values() if v == "failed")
        sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
