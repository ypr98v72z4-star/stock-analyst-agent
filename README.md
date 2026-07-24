# 股票分析助手

基于 Qoder 网页版 + Hermes 的自动化股票分析系统，每天自动生成市场日报并推送到企业微信。

## 功能特性

- **自动数据抓取**：从 Yahoo Finance 获取港股/美股行情和新闻
- **技术指标计算**：RSI、移动平均、波动率、成交量分析
- **AI 智能分析**：使用 Hermes 模型生成市场情绪判断和个股分析
- **统一日报格式**：市场总览、个股表现、风险提示、今日结论
- **企业微信推送**：手机端随时查看分析结果
- **云端自动运行**：GitHub Actions 定时触发，无需本地电脑

## 项目结构

```
stock-analyst-agent/
├── config.yaml              # 配置文件（股票池、数据源、Hermes 配置）
├── main.py                  # 主入口
├── requirements.txt         # Python 依赖
├── .env.example            # 环境变量模板
├── scripts/
│   ├── fetch_data.py       # 数据抓取模块
│   ├── calculate_indicators.py  # 技术指标计算
│   ├── hermes_client.py    # Hermes API 客户端
│   ├── generate_report.py  # 报告生成
│   └── wecom_push.py       # 企业微信推送
├── prompts/
│   ├── system_prompt.md    # Hermes 系统提示词
│   └── daily_analysis.md   # 日报分析模板
├── data/                   # 原始数据（自动生成）
└── reports/                # 日报输出（自动生成）
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/stock-analyst-agent.git
cd stock-analyst-agent
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填入实际值：

```bash
cp .env.example .env
```

编辑 `.env`：

```bash
HERMES_ENDPOINT=https://your-hermes-endpoint/v1
HERMES_API_KEY=sk-your-key-here
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-key
```

**获取方式：**
- **Hermes Endpoint**：从 Nous Research 获取云 API，或部署自托管 endpoint
- **企业微信 Webhook**：在企业微信群中添加机器人，获取 Webhook URL

### 4. 配置股票池

编辑 `config.yaml`，修改 `watchlist` 部分：

```yaml
watchlist:
  hk:  # 港股
    - symbol: "0700.HK"
      name: "腾讯控股"
    - symbol: "9988.HK"
      name: "阿里巴巴"
  us:  # 美股
    - symbol: "AAPL"
      name: "Apple"
    - symbol: "NVDA"
      name: "NVIDIA"
```

### 5. 本地运行测试

```bash
# 完整流程（抓取 + Hermes 分析 + 推送）
python main.py

# 仅抓取数据（不调用 Hermes）
python main.py --no-hermes

# 不推送企业微信
python main.py --no-push
```

## 部署到 GitHub Actions

### 1. 推送代码到 GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/stock-analyst-agent.git
git push -u origin main
```

### 2. 配置 GitHub Secrets

在仓库的 **Settings → Secrets and variables → Actions** 中添加：

- `HERMES_ENDPOINT`：Hermes API endpoint
- `HERMES_API_KEY`：Hermes API key
- `WECOM_WEBHOOK_URL`：企业微信 Webhook URL

### 3. 自动触发

GitHub Actions 会在以下时间自动运行：

- **港股收盘后**：周一至周五 16:30 HKT
- **美股收盘后**：周二至周六 04:30 HKT（对应美股交易日）

也可以手动触发：**Actions → Daily Stock Analysis → Run workflow**

## 自定义配置

### 修改分析 Prompt

编辑 `prompts/system_prompt.md` 调整 Hermes 的角色指令：

```markdown
你是一位专业的股票分析师助手。你的职责是：
1. 市场情绪归纳
2. 个股分析
3. 风险提示
4. 结论生成
```

编辑 `prompts/daily_analysis.md` 调整日报结构：

```markdown
## 一、大盘走势
## 二、个股分析
## 三、今日结论
## 四、风险提示
```

### 调整技术指标

编辑 `scripts/calculate_indicators.py`，修改指标计算逻辑。

### 更换数据源

编辑 `scripts/fetch_data.py`，替换为其他数据提供商（如 Alpha Vantage、Tushare 等）。

## 日报示例

```markdown
# 📊 股票分析日报 — 2026-07-24

---

## 一、市场总览

### 大盘走势
恒生指数今日上涨 1.2%，市场情绪偏多。科技板块领涨，腾讯、阿里涨幅超 2%。

### 个股分析
**腾讯控股 (0700.HK)**
收盘价 385.00，涨幅 2.3%。RSI 65，处于健康区间。成交量放大至 1.5 倍均量，资金流入明显。利好因素：游戏业务回暖。

**阿里巴巴 (9988.HK)**
收盘价 82.50，涨幅 1.8%。技术面突破 MA5，短期动能增强。新闻显示云业务增长超预期。

...

### 今日结论
- 整体判断：偏多
- 建议操作：科技股可继续持有，关注成交量持续性

### 风险提示
- 美联储加息预期升温，注意美股波动传导
- 部分个股 RSI 接近超买区，短期或有回调

---

*生成时间: 2026-07-24 16:35:00*
```

## 注意事项

1. **数据源限制**：yfinance 免费但有速率限制，如需更高频率建议更换付费数据源
2. **Hermes 成本**：云 API 按 token 计费，自托管需准备 GPU 资源
3. **企业微信限制**：单条消息最长 4096 字符，长报告会自动截断
4. **投资建议**：AI 生成内容仅供参考，不构成投资建议

## 故障排查

**问题：GitHub Actions 运行失败**
- 检查 Secrets 是否正确配置
- 查看 Actions 日志定位具体错误

**问题：Hermes 返回空内容**
- 检查 endpoint 和 API key 是否正确
- 确认网络连接正常

**问题：企业微信推送失败**
- 检查 Webhook URL 是否正确
- 确认企业微信群机器人未被删除

## 技术栈

- **数据源**：yfinance (Yahoo Finance)
- **AI 模型**：Hermes 3 (Nous Research)
- **推送渠道**：企业微信机器人
- **自动化**：GitHub Actions
- **语言**：Python 3.11+

## License

MIT
