"""Model loader and cache manager for ML models"""

import logging
from typing import Any, Optional

import streamlit as st

logger = logging.getLogger(__name__)

# Global model cache
_MODEL_CACHE: dict[str, Any] = {}


def get_models() -> dict[str, Any]:
    """
    Get or load ML models with caching

    Returns:
        Dictionary with loaded models
    """
    global _MODEL_CACHE

    if _MODEL_CACHE:
        return _MODEL_CACHE

    # Check if ML is enabled
    use_ml = st.session_state.get("use_ml_ranking", True)
    if not use_ml:
        return {}

    try:
        from sentence_transformers import SentenceTransformer
        from transformers import pipeline

        models = {}

        # Load sentence transformer for semantic similarity
        logger.info("Loading sentence transformer model...")
        models["embedding"] = SentenceTransformer("all-MiniLM-L6-v2")

        # Load FinBERT for sentiment analysis
        logger.info("Loading FinBERT sentiment model...")
        models["sentiment"] = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            device=-1,  # CPU
        )

        _MODEL_CACHE = models
        logger.info("All ML models loaded successfully")
        return models

    except ImportError:
        logger.warning("ML libraries not available")
        return {}
    except Exception as e:
        logger.error("Failed to load ML models: %s", str(e))
        return {}


def preload_models_with_ui() -> None:
    """
    Preload ML models with UI progress indicators

    Shows loading progress in Streamlit UI
    """
    global _MODEL_CACHE

    # Check if already loaded
    if _MODEL_CACHE or not st.session_state.get("use_ml_ranking", True):
        return

    try:
        from sentence_transformers import SentenceTransformer
        from transformers import pipeline

        # Create progress container
        progress_container = st.empty()

        with progress_container.container():
            st.markdown("### 🧠 Loading ML Models...")
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Load sentence transformer
            status_text.text("📦 Loading sentence transformer (80MB)...")
            progress_bar.progress(10)

            try:
                embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                progress_bar.progress(50)
                status_text.text("✅ Sentence transformer loaded")
            except Exception as e:
                logger.error("Failed to load sentence transformer: %s", str(e))
                status_text.text("❌ Failed to load sentence transformer")
                progress_bar.progress(50)
                return

            # Load FinBERT
            status_text.text("📦 Loading FinBERT sentiment model (440MB)...")
            progress_bar.progress(60)

            try:
                sentiment_model = pipeline(
                    "sentiment-analysis",
                    model="ProsusAI/finbert",
                    device=-1,  # CPU
                )
                progress_bar.progress(95)
                status_text.text("✅ FinBERT loaded")
            except Exception as e:
                logger.error("Failed to load FinBERT: %s", str(e))
                status_text.text("❌ Failed to load FinBERT")
                progress_bar.progress(95)
                return

            # Cache models
            _MODEL_CACHE = {
                "embedding": embedding_model,
                "sentiment": sentiment_model,
            }

            progress_bar.progress(100)
            status_text.text("✅ All models loaded successfully!")

        # Clear the progress display after a moment
        import time

        time.sleep(1)
        progress_container.empty()

        # Show success toast
        st.toast("🧠 ML models ready!", icon="✅")

    except ImportError:
        logger.warning(
            "ML libraries not available. Install with: pip install transformers sentence-transformers torch"
        )
        st.warning(
            "⚠️ ML libraries not installed. "
            "Advanced features disabled. "
            "Install with: `pip install transformers sentence-transformers torch`"
        )
    except Exception as e:
        logger.error("Failed to preload models: %s", str(e))
        st.error(f"❌ Failed to load ML models: {str(e)}")


def get_embedding_model() -> Optional[Any]:
    """Get the cached embedding model"""
    return _MODEL_CACHE.get("embedding")


def get_sentiment_model() -> Optional[Any]:
    """Get the cached sentiment model"""
    return _MODEL_CACHE.get("sentiment")


def clear_model_cache() -> None:
    """Clear the model cache (useful for testing)"""
    global _MODEL_CACHE
    _MODEL_CACHE = {}
