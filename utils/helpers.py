"""
工具函数
"""
import logging
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup


def setup_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("rocky_daily")


def truncate_text(text: str, max_len: int = 500) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "…"


def clean_html(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    return soup.get_text(separator=" ", strip=True)


def parse_date_flexible(date_str: str) -> datetime | None:
    """尝试多种格式解析日期字符串，返回 UTC aware datetime 或 None。"""
    if not date_str:
        return None

    # feedparser 常见格式
    try:
        return parsedate_to_datetime(date_str).astimezone(timezone.utc)
    except Exception:
        pass

    # ISO 8601
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(date_str[:19], fmt[:len(fmt)])
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            continue

    return None


def is_within_hours(dt: datetime | None, hours: int = 24) -> bool:
    if dt is None:
        return True  # 如果无法解析日期，默认包含
    now = datetime.now(timezone.utc)
    diff = now - dt
    return diff.total_seconds() <= hours * 3600


def deduplicate(items: list[dict], key: str = "url") -> list[dict]:
    seen = set()
    result = []
    for item in items:
        val = item.get(key, "")
        if val and val not in seen:
            seen.add(val)
            result.append(item)
        elif not val:
            result.append(item)
    return result
