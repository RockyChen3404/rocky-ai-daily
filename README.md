# 🤖 Rocky的大模型日报

自动收集过去24小时内 AI 行业最新动态，经 Claude AI 智能筛选和整理，以中文输出结构化日报。

参考格式：[奇绩大模型日报](https://miracleplus.com/)

---

## 📋 日报结构

| 板块 | 内容来源 |
|------|---------|
| 📰 资讯 | TechCrunch、VentureBeat、The Verge、机器之心、量子位等 RSS 源 |
| 🐦 推特 | X/Twitter 上顶级 AI 研究者和机构的最新推文 |
| 🚀 产品 | 新发布的 AI 产品和工具 |
| 🤗 HuggingFace & Github | 开源模型、数据集、热门代码库 |
| 💰 投融资 | AI 领域投资融资动态 |
| 📚 学习 | ArXiv 最新论文、技术博文、教程 |

---

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/RockyChen3404/rocky-ai-daily.git
cd rocky-ai-daily
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 Anthropic API Key
```

必填：
- `ANTHROPIC_API_KEY`：[获取地址](https://console.anthropic.com/)

可选：
- `HF_TOKEN`：HuggingFace Token，可获取更多模型数据

### 4. 运行

```bash
python main.py
```

报告将保存到 `reports/rocky_daily_YYYYMMDD.md`。

---

## 🛠️ 进阶用法

```bash
# 生成过去48小时的报告
python main.py --hours 48

# 跳过 Twitter/X 抓取（当 Nitter 不可用时）
python main.py --no-twitter

# 只收集新闻和推文（跳过其他源）
python main.py --no-arxiv --no-github --no-hf

# 自定义输出路径
python main.py --output ~/Desktop/today_ai_news.md

# 生成并打印到终端
python main.py --print
```

---

## 📂 项目结构

```
rocky-ai-daily/
├── main.py                    # 主程序入口
├── config.py                  # 配置（数据源、模型参数等）
├── collectors/                # 数据收集模块
│   ├── rss_collector.py       # RSS 新闻收集
│   ├── twitter_collector.py   # X/Twitter 推文收集
│   ├── arxiv_collector.py     # ArXiv 论文收集
│   ├── github_collector.py    # GitHub Trending 收集
│   └── huggingface_collector.py  # HuggingFace 更新收集
├── processors/
│   └── ai_processor.py        # Claude AI 筛选、分类、中文摘要
├── formatters/
│   └── report_formatter.py    # Markdown 报告格式化
├── utils/
│   └── helpers.py             # 工具函数
├── reports/                   # 生成的报告（git 忽略）
├── .env.example               # 环境变量示例
└── requirements.txt
```

---

## 🔧 自定义配置

编辑 `config.py` 可以：

- **添加/删除关注的 X 账号**：修改 `TWITTER_ACCOUNTS`
- **添加 RSS 源**：修改 `RSS_FEEDS`
- **调整 ArXiv 类别**：修改 `ARXIV_CATEGORIES`
- **调整每板块最大条数**：修改 `MAX_ITEMS_PER_SECTION`
- **调整最低相关性门槛**：修改 `MIN_RELEVANCE_SCORE`（1-10，默认6）

---

## 🤝 Twitter/X 抓取说明

本项目优先通过 **Nitter**（Twitter 开源替代前端）的 RSS 接口抓取推文，无需 Twitter API Key。

如果所有 Nitter 实例不可用，程序会自动尝试 `ntscraper` 库作为备用方案，并在两者都失败时跳过推特板块（不影响其他部分）。

如果你有 Twitter API v2 的 Bearer Token，可以在 `config.py` 中配置 `TWITTER_BEARER_TOKEN` 以获得更稳定的抓取。

---

## 📄 许可证

MIT License

---

*Rocky的大模型日报 · Powered by Claude AI*
