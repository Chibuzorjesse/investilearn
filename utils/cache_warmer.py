"""Cache warming utilities to precompute data on app startup"""

from pathlib import Path

import pandas as pd
import streamlit as st

from .ratio_calculator import _PEER_DATA_CACHE, _load_sector_tickers


def warm_sector_caches():
    """
    Load pre-computed sector data from parquet files.
    This is fast (no API calls) and loads in ~1-2 seconds.

    Falls back to API calls if cached files don't exist.
    Run scripts/refresh_data.py to update cached files.

    Returns:
        dict: Status of cache loading for each sector
    """
    sector_tickers = _load_sector_tickers()
    status = {}

    # Path to cached sector data
    cache_dir = Path(__file__).parent.parent / "data" / "sector_data"

    with st.spinner("🚀 Loading pre-computed data..."):
        progress_text = "Loading sector data from cache..."
        progress_bar = st.progress(0, text=progress_text)

        sectors = list(sector_tickers.keys())
        total = len(sectors)
        completed = 0

        for sector in sectors:
            try:
                cache_file = cache_dir / f"{sector}.parquet"

                if cache_file.exists():
                    # Load from pre-computed cache (fast!)
                    sector_df = pd.read_parquet(cache_file)
                    _PEER_DATA_CACHE[sector] = sector_df
                    status[sector] = f"loaded ({len(sector_df)} companies)"
                else:
                    # Cache file doesn't exist
                    status[sector] = "no cache - run scripts/refresh_data.py"

            except Exception as e:
                status[sector] = f"error: {str(e)}"

            completed += 1
            progress_bar.progress(
                completed / total,
                text=f"{progress_text} ({completed}/{total} sectors)",
            )

        progress_bar.empty()

    # Show warning if any sectors missing cache files
    missing = [s for s, v in status.items() if "no cache" in v]
    if missing:
        st.warning(
            f"⚠️ Missing cache files for {len(missing)} sectors. "
            f"Run `uv run python scripts/refresh_data.py --all`"
        )

    return status


def get_cache_stats():
    """
    Get statistics about cached data

    Returns:
        dict: Cache statistics
    """
    from .ratio_calculator import _PEER_DATA_CACHE

    return {
        "sectors_cached": len(_PEER_DATA_CACHE),
        "total_companies": sum(len(df) for df in _PEER_DATA_CACHE.values()),
    }
