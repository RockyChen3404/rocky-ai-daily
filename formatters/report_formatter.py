"""
报告格式化器 - 将分类后的内容格式化为 Markdown 日报
"""
from datetime import datetime


# 板块对应的 emoji
SECTION_EMOJIS = {
    "资讯": "📰",
    "推特": "🐦",
    "产品": "🚀",
    "HuggingFace&Github": "🤗",
    "投融资": "💰",
    "学习": "📚",
}

# 内容类型对应的小图标
TYPE_ICONS = {
    "news": "📄",
    "tweet": "🐦",
    "paper": "📜",
    "github": "💻",
    "huggingface_model": "🤗",
    "huggingface_space": "🌐",
}


def _format_item(item: dict) -> str:
    """将单条内容格式化为 Markdown。"""
    zh_title = item.get("zh_title") or item.get("title") or item.get("name") or item.get("content", "")[:50]
    zh_summary = item.get("zh_summary") or item.get("summary") or item.get("description") or ""
    url = item.get("url") or item.get("pdf_url") or ""
    source = item.get("source", "")
    author = item.get("author", "")

    lines = []

    # 标题行
    if url:
        lines.append(f"### [{zh_title}]({url})")
    else:
        lines.append(f"### {zh_title}")

    # 元信息行（来源 / 作者）
    meta_parts = []
    if author:
        meta_parts.append(f"@{author}")
    if source:
        meta_parts.append(source)

    # 对于论文，显示作者
    paper_authors = item.get("authors", "")
    if paper_authors:
        meta_parts = [f"作者：{paper_authors}"] + meta_parts

    if meta_parts:
        lines.append(f"*{' · '.join(meta_parts)}*")

    # 摘要
    if zh_summary:
        lines.append("")
        lines.append(zh_summary)

    # 特殊字段
    stars = item.get("stars", "")
    stars_today = item.get("stars_today", "")
    if stars:
        lines.append(f"\n⭐ {stars} stars {stars_today}")

    likes = item.get("likes", 0)
    downloads = item.get("downloads", 0)
    if likes or downloads:
        parts = []
        if likes:
            parts.append(f"❤️ {likes}")
        if downloads:
            parts.append(f"⬇️ {downloads:,}")
        lines.append(f"\n{' · '.join(parts)}")

    return "\n".join(lines)


def _format_section(section_name: str, items: list[dict]) -> str:
    """格式化单个板块。"""
    if not items:
        return ""

    emoji = SECTION_EMOJIS.get(section_name, "📌")
    lines = [f"## {emoji} {section_name}", ""]

    for item in items:
        lines.append(_format_item(item))
        lines.append("")
        lines.append("---")
        lines.append("")

    # 移除最后一个分隔线
    if lines and lines[-2] == "---":
        lines = lines[:-3] + [""]

    return "\n".join(lines)


def format_report(sections: dict[str, list[dict]]) -> str:
    """
    将分类后的内容格式化为完整的 Markdown 日报。
    """
    today = datetime.now()
    date_str = today.strftime("%-m月%-d日")
    full_date = today.strftime("%Y年%m月%d日")

    lines = []

    # 标题
    lines.append(f"# Rocky的大模型日报（{date_str}）")
    lines.append("")
    lines.append(f"> 生成时间：{full_date} · 由 Claude AI 智能整理")
    lines.append("")

    # 目录
    has_content = any(items for items in sections.values())
    if has_content:
        lines.append("## 📋 今日速览")
        lines.append("")
        for section_name, items in sections.items():
            if items:
                emoji = SECTION_EMOJIS.get(section_name, "📌")
                titles = [item.get("zh_title") or item.get("title") or "未命名" for item in items[:3]]
                preview = " / ".join(titles)
                lines.append(f"- **{emoji} {section_name}**：{preview}{'...' if len(items) > 3 else ''}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # 各板块内容
    section_order = ["资讯", "推特", "产品", "HuggingFace&Github", "投融资", "学习"]
    for section_name in section_order:
        items = sections.get(section_name, [])
        section_md = _format_section(section_name, items)
        if section_md:
            lines.append(section_md)
            lines.append("")

    # 声明
    lines.append("---")
    lines.append("")
    lines.append("## 📢 声明")
    lines.append("")
    lines.append(
        "本日报由程序自动收集互联网公开信息，经 Claude AI 筛选和整理生成。"
        "内容仅供参考，不代表任何立场或投资建议。"
        "如有版权问题请联系删除。"
    )
    lines.append("")
    lines.append(f"*Rocky的大模型日报 · {full_date}*")

    return "\n".join(lines)
