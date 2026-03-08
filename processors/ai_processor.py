"""
AI 处理器 - 使用阿里云通义千问（DashScope）对收集到的内容进行智能筛选、分类和中文摘要

接口：DashScope OpenAI 兼容模式
文档：https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope
"""
import json
import logging

from openai import OpenAI

from config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    QWEN_MODEL,
    QWEN_MODEL_STRONG,
    MAX_ITEMS_PER_SECTION,
    MIN_RELEVANCE_SCORE,
    REPORT_SECTIONS,
)

logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=DASHSCOPE_BASE_URL,
)


# ──────────────────────────────────────────────────────────────────────────────
# 第一步：快速相关性评分 + 分类（批量，用 qwen-turbo 省钱）
# ──────────────────────────────────────────────────────────────────────────────

_FILTER_SYSTEM = """你是一位专业的AI行业分析师，负责为"Rocky的大模型日报"筛选和分类内容。

日报的板块结构如下：
- 资讯：AI行业重要新闻、公司动态、政策法规
- 推特：X/Twitter 上有价值的AI相关帖子和观点
- 产品：新发布的AI产品、工具、应用
- HuggingFace&Github：开源模型、数据集、代码库的重要更新
- 投融资：AI领域的融资、收购、IPO等资本动态
- 学习：高质量的技术文章、论文解读、教程

评分标准（1-10分）：
10分：行业里程碑事件，极具影响力
7-9分：重要更新，值得关注
5-6分：有一定价值但不紧迫
1-4分：普通内容，意义不大

只保留6分及以上的内容。"""

_FILTER_USER_TEMPLATE = """请对以下 {count} 条内容进行评分和分类。

内容列表（JSON格式）：
{items_json}

请返回严格的 JSON 数组，每个元素包含：
- "index": 原始索引（整数）
- "score": 相关性评分（1-10整数）
- "section": 分配到的板块（从以下选择：资讯/推特/产品/HuggingFace&Github/投融资/学习）
- "zh_title": 中文标题（简洁，20字以内）
- "zh_summary": 中文摘要（100-200字，说明内容的价值和要点）

只返回 JSON 数组，不要其他文字。"""


def _call_qwen(model: str, system: str, user: str, max_tokens: int = 4096) -> str:
    """封装 DashScope 调用，返回文本内容。"""
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content.strip()


def _parse_json_response(text: str) -> list:
    """清理并解析模型返回的 JSON（处理 markdown 代码块包裹的情况）。"""
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def _batch_filter_and_categorize(items: list[dict]) -> list[dict]:
    """批量对条目进行相关性评分和分类。"""
    if not items:
        return []

    # 精简数据以节省 Token
    simplified = [
        {
            "index": i,
            "type": item.get("type", ""),
            "source": item.get("source", ""),
            "title": item.get("title") or item.get("name") or item.get("content", "")[:100],
            "summary": (
                item.get("summary") or item.get("description") or
                item.get("content", "") or item.get("abstract", "")
            )[:400],
        }
        for i, item in enumerate(items)
    ]

    # 分批处理（每批最多40条）
    batch_size = 40
    enriched: list[dict] = []

    for batch_start in range(0, len(simplified), batch_size):
        batch = simplified[batch_start: batch_start + batch_size]
        prompt = _FILTER_USER_TEMPLATE.format(
            count=len(batch),
            items_json=json.dumps(batch, ensure_ascii=False, indent=2),
        )

        try:
            text = _call_qwen(QWEN_MODEL, _FILTER_SYSTEM, prompt)
            results = _parse_json_response(text)

            for r in results:
                abs_idx = batch_start + r.get("index", 0)
                if abs_idx < len(items):
                    item = items[abs_idx].copy()
                    item["score"] = r.get("score", 0)
                    item["section"] = r.get("section", "资讯")
                    item["zh_title"] = r.get("zh_title", item.get("title", ""))
                    item["zh_summary"] = r.get("zh_summary", "")
                    enriched.append(item)

        except json.JSONDecodeError as e:
            logger.error(f"[AI] JSON 解析失败: {e}\n响应前200字: {text[:200]}")
        except Exception as e:
            logger.error(f"[AI] 批次处理失败: {e}")

    return enriched


# ──────────────────────────────────────────────────────────────────────────────
# 第二步：按板块组织，每板块保留最优条目
# ──────────────────────────────────────────────────────────────────────────────

def _organize_by_section(enriched: list[dict]) -> dict[str, list[dict]]:
    """将已评分条目按板块分组，每板块保留最多 N 条最高分内容。"""
    sections: dict[str, list[dict]] = {s: [] for s in REPORT_SECTIONS}

    for item in sorted(enriched, key=lambda x: x.get("score", 0), reverse=True):
        if item.get("score", 0) < MIN_RELEVANCE_SCORE:
            continue

        # 根据内容类型强制归类
        item_type = item.get("type", "")
        if item_type == "tweet":
            section = "推特"
        elif item_type == "paper":
            section = "学习"
        elif item_type in ("github", "huggingface_model", "huggingface_space"):
            section = "HuggingFace&Github"
        else:
            section = item.get("section", "资讯")
            if section not in sections:
                section = "资讯"

        if len(sections[section]) < MAX_ITEMS_PER_SECTION:
            sections[section].append(item)

    return sections


# ──────────────────────────────────────────────────────────────────────────────
# 公共入口
# ──────────────────────────────────────────────────────────────────────────────

def process_and_categorize(raw_data: dict) -> dict[str, list[dict]]:
    """
    输入：各来源的原始数据字典
    输出：按板块分类的内容字典

    raw_data 格式：
    {
        "news": [...],
        "twitter": [...],
        "papers": [...],
        "github": [...],
        "huggingface": [...],
    }
    """
    if not DASHSCOPE_API_KEY:
        logger.error("[AI] DASHSCOPE_API_KEY 未设置，无法处理内容")
        raise ValueError("请在 .env 文件中设置 DASHSCOPE_API_KEY（阿里云 DashScope API Key）")

    all_items: list[dict] = []
    for items in raw_data.values():
        all_items.extend(items)

    logger.info(f"[AI] 开始处理 {len(all_items)} 条原始内容（模型：{QWEN_MODEL}）...")

    if not all_items:
        logger.warning("[AI] 没有收集到任何内容")
        return {s: [] for s in REPORT_SECTIONS}

    enriched = _batch_filter_and_categorize(all_items)
    logger.info(f"[AI] 评分完成，{len(enriched)} 条通过过滤")

    sections = _organize_by_section(enriched)

    for section, items in sections.items():
        logger.info(f"[AI]   {section}: {len(items)} 条")

    return sections
