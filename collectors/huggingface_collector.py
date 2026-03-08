"""
HuggingFace 模型/数据集收集器
"""
import logging
import requests
from datetime import datetime, timezone

from config import HF_TOKEN, HF_MAX_MODELS, HF_MODEL_TAGS
from utils.helpers import truncate_text, is_within_hours, parse_date_flexible

logger = logging.getLogger(__name__)

API_BASE = "https://huggingface.co/api"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}


def _fetch_models(tag: str, hours: int) -> list[dict]:
    try:
        params = {
            "sort": "lastModified",
            "direction": -1,
            "limit": HF_MAX_MODELS,
            "filter": tag,
            "full": True,
        }
        resp = requests.get(f"{API_BASE}/models", params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        models = resp.json()
    except Exception as e:
        logger.error(f"[HuggingFace] 获取模型失败 ({tag}): {e}")
        return []

    items = []
    for m in models:
        last_modified = parse_date_flexible(m.get("lastModified", ""))
        if not is_within_hours(last_modified, hours):
            continue

        items.append({
            "name": m.get("id", ""),
            "description": truncate_text(m.get("cardData", {}).get("model_description") or
                                         m.get("description", "") or
                                         f"{tag} model", 300),
            "url": f"https://huggingface.co/{m.get('id', '')}",
            "downloads": m.get("downloads", 0),
            "likes": m.get("likes", 0),
            "tags": m.get("tags", [])[:5],
            "author": m.get("author", ""),
            "published_at": last_modified.isoformat() if last_modified else "",
            "type": "huggingface_model",
            "source": "HuggingFace",
        })

    return items


def _fetch_spaces(hours: int) -> list[dict]:
    """获取最新的 HuggingFace Spaces（演示应用）。"""
    try:
        params = {"sort": "lastModified", "direction": -1, "limit": 20, "full": True}
        resp = requests.get(f"{API_BASE}/spaces", params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        spaces = resp.json()
    except Exception as e:
        logger.error(f"[HuggingFace] 获取 Spaces 失败: {e}")
        return []

    items = []
    for s in spaces:
        last_modified = parse_date_flexible(s.get("lastModified", ""))
        if not is_within_hours(last_modified, hours):
            continue

        items.append({
            "name": s.get("id", ""),
            "description": truncate_text(s.get("cardData", {}).get("short_description") or
                                          s.get("title", "") or "HuggingFace Space", 300),
            "url": f"https://huggingface.co/spaces/{s.get('id', '')}",
            "likes": s.get("likes", 0),
            "published_at": last_modified.isoformat() if last_modified else "",
            "type": "huggingface_space",
            "source": "HuggingFace Spaces",
        })

    return items


def collect_huggingface_updates(hours: int = 24) -> list[dict]:
    """收集 HuggingFace 最新模型和 Spaces。"""
    logger.info("[HuggingFace] 开始收集更新...")
    all_items: list[dict] = []
    seen: set[str] = set()

    for tag in HF_MODEL_TAGS:
        for item in _fetch_models(tag, hours):
            if item["name"] not in seen:
                seen.add(item["name"])
                all_items.append(item)

    for item in _fetch_spaces(hours):
        if item["name"] not in seen:
            seen.add(item["name"])
            all_items.append(item)

    # 按 likes 降序排列
    all_items.sort(key=lambda x: x.get("likes", 0), reverse=True)

    logger.info(f"[HuggingFace] 共收集 {len(all_items)} 个更新")
    return all_items
