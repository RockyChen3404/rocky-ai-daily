"""
ArXiv 论文收集器
"""
import logging
import arxiv
from datetime import datetime, timezone, timedelta

from config import ARXIV_CATEGORIES, ARXIV_MAX_RESULTS, ARXIV_KEYWORDS
from utils.helpers import truncate_text, is_within_hours

logger = logging.getLogger(__name__)


def _is_ai_relevant(paper: arxiv.Result) -> bool:
    """检查论文是否与 AI/ML 核心话题相关。"""
    text = (paper.title + " " + paper.summary).lower()
    return any(kw.lower() in text for kw in ARXIV_KEYWORDS)


def collect_arxiv_papers(hours: int = 24) -> list[dict]:
    """收集 ArXiv 最新 AI/ML 论文。"""
    logger.info("[ArXiv] 开始收集论文...")
    all_papers: list[dict] = []
    seen_ids: set[str] = set()

    client = arxiv.Client(page_size=ARXIV_MAX_RESULTS, delay_seconds=1.0)

    for category in ARXIV_CATEGORIES:
        try:
            search = arxiv.Search(
                query=f"cat:{category}",
                max_results=ARXIV_MAX_RESULTS,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending,
            )

            for paper in client.results(search):
                paper_id = paper.entry_id
                if paper_id in seen_ids:
                    continue

                # ArXiv 时间是 UTC
                pub_dt = paper.published.replace(tzinfo=timezone.utc) if paper.published.tzinfo is None else paper.published
                if not is_within_hours(pub_dt, hours):
                    continue

                if not _is_ai_relevant(paper):
                    continue

                seen_ids.add(paper_id)
                all_papers.append({
                    "title": paper.title.strip(),
                    "authors": ", ".join(a.name for a in paper.authors[:5]),
                    "summary": truncate_text(paper.summary.replace("\n", " "), 600),
                    "url": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "published_at": pub_dt.isoformat(),
                    "categories": [category] + [c for c in paper.categories if c != category],
                    "type": "paper",
                    "source": "ArXiv",
                })

        except Exception as e:
            logger.error(f"[ArXiv] 抓取 {category} 失败: {e}")

    logger.info(f"[ArXiv] 共收集 {len(all_papers)} 篇论文")
    return all_papers
