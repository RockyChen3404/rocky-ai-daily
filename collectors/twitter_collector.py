"""
X (Twitter) 内容收集器

优先策略：
  1. 通过 Nitter 实例的 RSS 接口抓取（无需 API Key）
  2. 备用：ntscraper 库
"""
import logging
import time
import random
import feedparser
import requests

from config import TWITTER_ACCOUNTS, NITTER_INSTANCES
from utils.helpers import clean_html, truncate_text, parse_date_flexible, is_within_hours

logger = logging.getLogger(__name__)

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}


def _find_working_nitter_instance(timeout: int = 5) -> str | None:
    """测试 Nitter 实例可用性，返回第一个可用的实例域名。"""
    for instance in NITTER_INSTANCES:
        try:
            url = f"https://{instance}/OpenAI/rss"
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            if resp.status_code == 200 and "<rss" in resp.text[:200]:
                logger.info(f"[Twitter] 使用 Nitter 实例: {instance}")
                return instance
        except Exception:
            continue
    return None


def _collect_via_nitter_rss(instance: str, hours: int) -> list[dict]:
    """通过 Nitter RSS 接口收集推文。"""
    items: list[dict] = []

    for account in TWITTER_ACCOUNTS:
        url = f"https://{instance}/{account}/rss"
        try:
            time.sleep(random.uniform(0.3, 0.8))  # 礼貌性延迟
            feed = feedparser.parse(url)

            if not feed.entries:
                continue

            for entry in feed.entries[:15]:  # 每账号最多取15条
                pub_date = parse_date_flexible(
                    entry.get("published") or entry.get("updated") or ""
                )
                if not is_within_hours(pub_date, hours):
                    continue

                content = clean_html(
                    entry.get("summary") or entry.get("description", "")
                )
                # 去掉"RT by"转推内容
                if content.startswith("RT by"):
                    continue

                # 从 Nitter RSS 链接提取原始 Twitter 链接
                link = entry.get("link", "").replace(instance, "x.com").replace(
                    "https://x.com", "https://x.com"
                )

                items.append({
                    "author": account,
                    "content": truncate_text(content, 500),
                    "url": link,
                    "published_at": pub_date.isoformat() if pub_date else "",
                    "type": "tweet",
                    "source": "X (Twitter)",
                })

        except Exception as e:
            logger.debug(f"[Twitter] Nitter RSS 失败 @{account}: {e}")

    return items


def _collect_via_ntscraper(hours: int) -> list[dict]:
    """通过 ntscraper 库收集推文（备用方案）。"""
    try:
        from ntscraper import Nitter
    except ImportError:
        logger.warning("[Twitter] ntscraper 未安装，跳过备用方案")
        return []

    items: list[dict] = []
    try:
        scraper = Nitter(log_level=1, skip_instance_check=False)

        for account in TWITTER_ACCOUNTS[:10]:  # 备用方案限制10个账号
            try:
                result = scraper.get_tweets(account, mode="user", number=10)
                tweets = result.get("tweets", [])

                for tweet in tweets:
                    pub_date = parse_date_flexible(tweet.get("date", ""))
                    if not is_within_hours(pub_date, hours):
                        continue

                    content = tweet.get("text", "").strip()
                    if not content or content.startswith("RT @"):
                        continue

                    items.append({
                        "author": account,
                        "content": truncate_text(content, 500),
                        "url": tweet.get("link", ""),
                        "published_at": pub_date.isoformat() if pub_date else "",
                        "type": "tweet",
                        "source": "X (Twitter)",
                    })
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"[Twitter] ntscraper 失败 @{account}: {e}")

    except Exception as e:
        logger.warning(f"[Twitter] ntscraper 初始化失败: {e}")

    return items


def collect_twitter_updates(hours: int = 24) -> list[dict]:
    """收集 X/Twitter 更新，返回推文列表。"""
    logger.info("[Twitter] 开始收集推文...")

    # 策略1：Nitter RSS
    nitter_instance = _find_working_nitter_instance()
    if nitter_instance:
        items = _collect_via_nitter_rss(nitter_instance, hours)
        if items:
            logger.info(f"[Twitter] Nitter RSS 收集到 {len(items)} 条推文")
            return items

    # 策略2：ntscraper
    logger.info("[Twitter] Nitter RSS 不可用，尝试 ntscraper...")
    items = _collect_via_ntscraper(hours)
    if items:
        logger.info(f"[Twitter] ntscraper 收集到 {len(items)} 条推文")
        return items

    logger.warning("[Twitter] 所有抓取方式均失败，推文部分将跳过")
    return []
