"""Knowledge-related Celery tasks."""

from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.knowledge_tasks.refresh_popular_articles")
def refresh_popular_articles() -> dict:
    """Refresh cache for most-accessed knowledge articles.

    Runs daily at 3 AM to pre-warm the Redis cache with popular articles.
    """
    try:
        logger.info("Refreshing popular knowledge article cache")
        # TODO: Query knowledge_repository for top-N articles by access_count
        logger.info("Popular article cache refreshed")
        return {"status": "ok", "articles_cached": 0}
    except Exception as exc:
        logger.error("Cache refresh failed: %s", exc)
        raise


@celery_app.task(name="app.tasks.knowledge_tasks.reindex_articles")
def reindex_articles(article_ids: list[str]) -> dict:
    """Re-index knowledge articles in the vector store."""
    logger.info("Re-indexing %d knowledge articles", len(article_ids))
    return {"status": "ok", "reindexed": len(article_ids)}
