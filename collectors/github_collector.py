"""
GitHub Trending 收集器
"""
import logging
import requests
from bs4 import BeautifulSoup

from config import GITHUB_TRENDING_LANGUAGES, GITHUB_TRENDING_SINCE
from utils.helpers import truncate_text

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

AI_ML_KEYWORDS = [
    "llm", "gpt", "ai", "ml", "machine learning", "deep learning",
    "neural", "transformer", "diffusion", "language model", "embedding",
    "vector", "rag", "agent", "model", "inference", "training",
    "reinforcement", "multimodal", "vision", "nlp", "cuda", "gpu",
    "pytorch", "tensorflow", "huggingface", "openai", "anthropic",
    "stable diffusion", "fine-tun", "dataset", "benchmark",
]


def _is_ai_repo(name: str, description: str) -> bool:
    text = (name + " " + description).lower()
    return any(kw in text for kw in AI_ML_KEYWORDS)


def _scrape_trending(language: str = "") -> list[dict]:
    lang_path = f"/{language}" if language else ""
    url = f"https://github.com/trending{lang_path}?since={GITHUB_TRENDING_SINCE}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[GitHub] 请求失败 ({language or 'all'}): {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    repos = []

    for article in soup.select("article.Box-row"):
        try:
            title_el = article.select_one("h2 a")
            if not title_el:
                continue

            full_name = title_el.get_text(strip=True).replace("\n", "").replace(" ", "")
            desc_el = article.select_one("p")
            description = desc_el.get_text(strip=True) if desc_el else ""

            stars_el = article.select_one("a[href$='/stargazers']")
            stars = stars_el.get_text(strip=True).replace(",", "") if stars_el else "0"

            stars_today_el = article.select_one("span.d-inline-block.float-sm-right")
            stars_today = stars_today_el.get_text(strip=True) if stars_today_el else ""

            lang_el = article.select_one("span[itemprop='programmingLanguage']")
            lang = lang_el.get_text(strip=True) if lang_el else ""

            repos.append({
                "name": full_name,
                "description": truncate_text(description, 300),
                "url": f"https://github.com/{full_name.replace(' ', '')}",
                "stars": stars,
                "stars_today": stars_today,
                "language": lang,
                "type": "github",
                "source": "GitHub Trending",
            })
        except Exception:
            continue

    return repos


def collect_github_trending() -> list[dict]:
    """收集 GitHub Trending 中的 AI/ML 相关项目。"""
    logger.info("[GitHub] 开始收集 Trending 项目...")
    all_repos: list[dict] = []
    seen: set[str] = set()

    for lang in GITHUB_TRENDING_LANGUAGES:
        repos = _scrape_trending(lang)
        for repo in repos:
            if repo["name"] not in seen:
                seen.add(repo["name"])
                # 过滤非 AI 项目（全语言列表时才过滤）
                if not lang or _is_ai_repo(repo["name"], repo["description"]):
                    all_repos.append(repo)

    # 去重 + 保留前25个
    all_repos = all_repos[:25]
    logger.info(f"[GitHub] 共收集 {len(all_repos)} 个 Trending 项目")
    return all_repos
