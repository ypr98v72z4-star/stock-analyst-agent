"""
企业微信 Webhook 推送模块
"""
import os
import requests


def send_wecom(config: dict, content: str) -> dict:
    """
    推送 Markdown 消息到企业微信机器人
    content: Markdown 格式的报告内容
    """
    webhook_url = config["report"]["wecom_webhook"]
    webhook_url = os.environ.get("WECOM_WEBHOOK_URL", webhook_url)

    if webhook_url.startswith("${"):
        webhook_url = os.environ.get(webhook_url[2:-1], "")

    if not webhook_url:
        return {"errcode": -1, "errmsg": "Webhook URL not configured"}

    # 企业微信 Markdown 消息有长度限制, 截断到 4096 字符
    if len(content) > 4096:
        content = content[:4090] + "\n\n..."

    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    resp = requests.post(webhook_url, json=payload, timeout=10)
    return resp.json()


def send_summary(config: dict, summary: str) -> dict:
    """
    推送精简摘要 (适合手机端快速浏览)
    只发送"今日结论"和"风险提示"
    """
    # 提取关键部分
    lines = summary.split("\n")
    key_lines = []
    capture = False
    for line in lines:
        if "今日结论" in line or "风险提示" in line:
            capture = True
        if capture:
            key_lines.append(line)
            if line.strip() == "" and len(key_lines) > 2:
                capture = False

    key_content = "\n".join(key_lines) if key_lines else summary[:1000]
    return send_wecom(config, key_content)
