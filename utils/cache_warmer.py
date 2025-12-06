"""Cache warming utilities to precompute data on app startup"""

import streamlit as st

from .ratio_calculator import _get_cached_peer_data, _load_sector_tickers


@st.cache_data(ttl=3600, show_spinner=False)
def warm_sector_caches():
    """
    Precompute and cache peer data for all sectors on app startup

    Returns:
        dict: Status of cache warming for each sector
    """
    sector_tickers = _load_sector_tickers()
    status = {}

    with st.spinner("🔥 Warming up caches (one-time, ~30-60 seconds)..."):
        progress_text = "Preloading sector data for faster comparisons..."
        progress_bar = st.progress(0, text=progress_text)

        sectors = list(sector_tickers.keys())
        total = len(sectors)

        for idx, sector in enumerate(sectors):
            try:
                # This will cache the data for this sector
                _get_cached_peer_data(sector)
                status[sector] = "success"
            except Exception as e:
                status[sector] = f"error: {str(e)}"

            progress_bar.progress(
                (idx + 1) / total, text=f"{progress_text} ({idx + 1}/{total} sectors)"
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
