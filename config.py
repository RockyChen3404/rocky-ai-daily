"""
Rocky的大模型日报 - 配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
HF_TOKEN = os.getenv("HF_TOKEN", "")

# 输出目录
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./reports")

# 日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ────────────────────────────────────────────────
# X / Twitter 账号列表（关注这些账号获取最新AI动态）
# ────────────────────────────────────────────────
TWITTER_ACCOUNTS = [
    "OpenAI",
    "AnthropicAI",
    "GoogleDeepMind",
    "ylecun",          # Yann LeCun
    "karpathy",        # Andrej Karpathy
    "sama",            # Sam Altman
    "ilyasut",         # Ilya Sutskever
    "demishassabis",   # Demis Hassabis
    "emollick",        # Ethan Mollick
    "simonw",          # Simon Willison
    "lvwerra",         # Leandro von Werra (HuggingFace)
    "hardmaru",        # Ha David
    "AravSrinivas",    # Perplexity CEO
    "gdb",             # Greg Brockman
    "soumithchintala", # Soumith Chintala (Meta AI)
    "natfriedman",     # Nat Friedman
    "ID_AA_Carmack",   # John Carmack
    "drjimfan",        # Jim Fan (NVIDIA)
    "tobi",            # Tobi Lutke (Shopify)
    "jeremyphoward",   # Jeremy Howard
]

# Nitter 实例列表（按优先级排序，用于抓取X推文）
NITTER_INSTANCES = [
    "nitter.privacydev.net",
    "nitter.poast.org",
    "nitter.1d4.us",
    "nitter.unixfox.eu",
    "nitter.cz",
    "nitter.nl",
    "nitter.weiler.rocks",
]

# ────────────────────────────────────────────────
# RSS 订阅源
# ────────────────────────────────────────────────
RSS_FEEDS = {
    # 英文科技媒体
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Wired AI": "https://www.wired.com/feed/tag/ai/latest/rss",
    "MIT Tech Review AI": "https://www.technologyreview.com/feed/",
    "Ars Technica AI": "https://feeds.arstechnica.com/arstechnica/index",
    # AI专业媒体
    "The Gradient": "https://thegradient.pub/rss/",
    "Import AI": "https://jack-clark.net/feed/",
    # 中文AI资讯
    "机器之心": "https://www.jiqizhixin.com/rss",
    "量子位": "https://www.qbitai.com/feed",
}

# ────────────────────────────────────────────────
# ArXiv 配置
# ────────────────────────────────────────────────
ARXIV_CATEGORIES = [
    "cs.AI",   # Artificial Intelligence
    "cs.LG",   # Machine Learning
    "cs.CL",   # Computation and Language (NLP)
    "cs.CV",   # Computer Vision
    "cs.RO",   # Robotics
]
ARXIV_MAX_RESULTS = 30   # 每个类别最多获取数量
ARXIV_KEYWORDS = [
    "large language model", "LLM", "foundation model", "multimodal",
    "transformer", "diffusion model", "reinforcement learning from human feedback",
    "RLHF", "instruction tuning", "chain of thought", "agent", "RAG",
    "retrieval augmented generation", "vision language model", "VLM",
]

# ────────────────────────────────────────────────
# GitHub Trending 配置
# ────────────────────────────────────────────────
GITHUB_TRENDING_LANGUAGES = ["python", "jupyter-notebook", ""]  # "" = 全语言
GITHUB_TRENDING_SINCE = "daily"  # daily, weekly, monthly

# ────────────────────────────────────────────────
# HuggingFace 配置
# ────────────────────────────────────────────────
HF_MAX_MODELS = 20
HF_MODEL_TAGS = ["text-generation", "text-to-image", "multimodal", "reinforcement-learning"]

# ────────────────────────────────────────────────
# AI 处理配置
# ────────────────────────────────────────────────
CLAUDE_MODEL = "claude-haiku-4-5-20251001"      # 快速处理用
CLAUDE_MODEL_STRONG = "claude-sonnet-4-6"        # 最终报告生成用
MAX_ITEMS_PER_SECTION = 6                         # 每个板块最多条目数
MIN_RELEVANCE_SCORE = 6                           # 最低相关性分数 (1-10)

# 报告板块定义
REPORT_SECTIONS = ["资讯", "推特", "产品", "HuggingFace&Github", "投融资", "学习"]
