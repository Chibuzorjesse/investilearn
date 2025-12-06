"""Cache warming utilities to precompute data on app startup"""

import time
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st

from .ratio_calculator import _get_cached_peer_data, _load_sector_tickers


@st.cache_data(ttl=3600, show_spinner=False)
def warm_sector_caches():
    """
    Precompute and cache peer data for all sectors on app startup
    Uses parallel processing to speed up loading

    Returns:
        dict: Status of cache warming for each sector
    """
    sector_tickers = _load_sector_tickers()
    status = {}

    with st.spinner("🔥 Warming up caches (one-time, ~20-30 seconds)..."):
        progress_text = "Preloading sector data for faster comparisons..."
        progress_bar = st.progress(0, text=progress_text)

        sectors = list(sector_tickers.keys())
        total = len(sectors)
        completed = 0

        def load_sector(sector):
            """Load a single sector's data with rate limiting"""
            try:
                # Add delay to avoid rate limiting (250ms between requests)
                time.sleep(0.25)

                # Suppress the ScriptRunContext warnings from threads
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")
                    _get_cached_peer_data(sector)
                return sector, "success"
            except Exception as e:
                return sector, f"error: {str(e)}"

        # Use ThreadPoolExecutor with reduced parallelism to avoid rate limits
        # max_workers=2 reduces API call rate while still providing speedup
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit all sector loading tasks
            future_to_sector = {executor.submit(load_sector, sector): sector for sector in sectors}

            # Process completed tasks as they finish
            for future in as_completed(future_to_sector):
                sector, result = future.result()
                status[sector] = result
                completed += 1

                progress_bar.progress(
                    completed / total,
                    text=f"{progress_text} ({completed}/{total} sectors)",
                )

        progress_bar.empty()

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
