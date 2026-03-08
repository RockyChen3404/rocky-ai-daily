"""
RSS 新闻收集器
"""
import logging
import feedparser
from datetime import datetime, timezone

from config import RSS_FEEDS
from utils.helpers import clean_html, truncate_text, parse_date_flexible, is_within_hours

logger = logging.getLogger(__name__)


def collect_rss_news(hours: int = 24) -> list[dict]:
    """从所有配置的 RSS 源收集过去 N 小时的新闻。"""
    all_items: list[dict] = []

    for source_name, feed_url in RSS_FEEDS.items():
        try:
            logger.info(f"[RSS] 正在抓取: {source_name}")
            feed = feedparser.parse(feed_url)

            if feed.bozo and not feed.entries:
                logger.warning(f"[RSS] 解析失败: {source_name} - {feed.bozo_exception}")
                continue

            for entry in feed.entries:
                pub_date = parse_date_flexible(
                    entry.get("published") or entry.get("updated") or ""
                )
                if not is_within_hours(pub_date, hours):
                    continue

                summary = clean_html(
                    entry.get("summary") or entry.get("content", [{}])[0].get("value", "")
                )

                all_items.append({
                    "source": source_name,
                    "title": entry.get("title", "").strip(),
                    "url": entry.get("link", ""),
                    "summary": truncate_text(summary, 600),
                    "published_at": pub_date.isoformat() if pub_date else "",
                    "type": "news",
                })

            logger.info(f"[RSS] {source_name}: 找到 {len(feed.entries)} 条, 过滤后新增")

        except Exception as e:
            logger.error(f"[RSS] 抓取失败 {source_name}: {e}")

    logger.info(f"[RSS] 共收集 {len(all_items)} 条新闻")
    return all_items
