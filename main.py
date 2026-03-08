#!/usr/bin/env python3
"""
Rocky的大模型日报 - 主程序
用法:
    python main.py            # 生成今日报告（过去24小时）
    python main.py --hours 48 # 生成过去48小时的报告
    python main.py --no-twitter  # 跳过 Twitter/X 抓取
    python main.py --output custom_report.md  # 自定义输出文件名
"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from config import ANTHROPIC_API_KEY, OUTPUT_DIR, LOG_LEVEL
from utils.helpers import setup_logging


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rocky的大模型日报 - AI行业每日资讯整理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--hours", type=int, default=24, help="收集过去N小时的内容（默认24）")
    parser.add_argument("--no-twitter", action="store_true", help="跳过 Twitter/X 抓取")
    parser.add_argument("--no-arxiv", action="store_true", help="跳过 ArXiv 论文抓取")
    parser.add_argument("--no-github", action="store_true", help="跳过 GitHub Trending 抓取")
    parser.add_argument("--no-hf", action="store_true", help="跳过 HuggingFace 抓取")
    parser.add_argument("--output", type=str, default="", help="自定义输出文件路径")
    parser.add_argument("--print", action="store_true", help="同时在终端打印报告")
    return parser.parse_args()


def check_prerequisites() -> bool:
    if not ANTHROPIC_API_KEY:
        print("❌ 错误：未找到 ANTHROPIC_API_KEY")
        print("   请复制 .env.example 为 .env，并填入你的 API Key")
        print("   获取地址：https://console.anthropic.com/")
        return False
    return True


def main():
    args = parse_args()
    logger = setup_logging(LOG_LEVEL)

    print("=" * 55)
    print("  🤖  Rocky的大模型日报")
    print(f"  📅  {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print("=" * 55)

    if not check_prerequisites():
        sys.exit(1)

    # 确保输出目录存在
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_data: dict = {}

    # ── 1. 收集 RSS 新闻 ─────────────────────────────────
    print("\n📰 收集 RSS 新闻...")
    from collectors.rss_collector import collect_rss_news
    raw_data["news"] = collect_rss_news(hours=args.hours)
    print(f"   → 收集到 {len(raw_data['news'])} 条")

    # ── 2. 收集 X/Twitter 推文 ───────────────────────────
    if not args.no_twitter:
        print("\n🐦 收集 X/Twitter 推文...")
        from collectors.twitter_collector import collect_twitter_updates
        raw_data["twitter"] = collect_twitter_updates(hours=args.hours)
        print(f"   → 收集到 {len(raw_data['twitter'])} 条")
    else:
        raw_data["twitter"] = []

    # ── 3. 收集 ArXiv 论文 ───────────────────────────────
    if not args.no_arxiv:
        print("\n📄 收集 ArXiv 论文...")
        from collectors.arxiv_collector import collect_arxiv_papers
        raw_data["papers"] = collect_arxiv_papers(hours=args.hours)
        print(f"   → 收集到 {len(raw_data['papers'])} 篇")
    else:
        raw_data["papers"] = []

    # ── 4. 收集 GitHub Trending ──────────────────────────
    if not args.no_github:
        print("\n💻 收集 GitHub Trending...")
        from collectors.github_collector import collect_github_trending
        raw_data["github"] = collect_github_trending()
        print(f"   → 收集到 {len(raw_data['github'])} 个项目")
    else:
        raw_data["github"] = []

    # ── 5. 收集 HuggingFace 更新 ─────────────────────────
    if not args.no_hf:
        print("\n🤗 收集 HuggingFace 更新...")
        from collectors.huggingface_collector import collect_huggingface_updates
        raw_data["huggingface"] = collect_huggingface_updates(hours=args.hours)
        print(f"   → 收集到 {len(raw_data['huggingface'])} 个更新")
    else:
        raw_data["huggingface"] = []

    total = sum(len(v) for v in raw_data.values())
    print(f"\n📊 共收集 {total} 条原始内容")

    # ── 6. AI 处理和分类 ─────────────────────────────────
    print("\n🤖 Claude AI 正在分析和整理内容...")
    from processors.ai_processor import process_and_categorize
    try:
        sections = process_and_categorize(raw_data)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    selected_total = sum(len(v) for v in sections.values())
    print(f"   → 精选 {selected_total} 条内容")
    for section, items in sections.items():
        if items:
            print(f"      {section}: {len(items)} 条")

    # ── 7. 格式化报告 ────────────────────────────────────
    print("\n📝 生成报告...")
    from formatters.report_formatter import format_report
    report = format_report(sections)

    # ── 8. 保存报告 ──────────────────────────────────────
    if args.output:
        output_path = Path(args.output)
    else:
        date_str = datetime.now().strftime("%Y%m%d")
        output_path = output_dir / f"rocky_daily_{date_str}.md"

    output_path.write_text(report, encoding="utf-8")
    print(f"\n✅ 报告已保存: {output_path.absolute()}")

    if args.print:
        print("\n" + "=" * 55)
        print(report)

    print("\n🎉 完成！")


if __name__ == "__main__":
    main()
