"""
Hermes 客户端 — 通过 OpenAI 兼容 API 调用 Hermes 模型
"""
import os
import json
from openai import OpenAI


def get_client(config: dict) -> OpenAI:
    """创建 OpenAI 兼容客户端 (Hermes endpoint)"""
    endpoint = config["hermes"]["endpoint"]
    api_key = config["hermes"]["api_key"]

    # 支持环境变量覆盖
    endpoint = os.environ.get("HERMES_ENDPOINT", endpoint)
    api_key = os.environ.get("HERMES_API_KEY", api_key)

    # 替换 ${VAR} 占位符
    if endpoint.startswith("${"):
        endpoint = os.environ.get(endpoint[2:-1], "")
    if api_key.startswith("${"):
        api_key = os.environ.get(api_key[2:-1], "")

    return OpenAI(base_url=endpoint, api_key=api_key)


def analyze(config: dict, system_prompt: str, user_prompt: str) -> str:
    """
    调用 Hermes 进行分析
    system_prompt: 角色/指令
    user_prompt: 包含数据的分析请求
    返回: 模型生成的分析文本
    """
    client = get_client(config)

    response = client.chat.completions.create(
        model=config["hermes"]["model"],
        temperature=config["hermes"]["temperature"],
        max_tokens=config["hermes"]["max_tokens"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.choices[0].message.content


def load_prompt(filename: str) -> str:
    """从 prompts/ 目录加载 prompt 模板"""
    path = os.path.join(os.path.dirname(__file__), "..", "prompts", filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
