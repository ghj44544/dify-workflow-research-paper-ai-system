import re


THINK_BLOCK_PATTERN = re.compile(r"<think\b[^>]*>.*?</think>", re.IGNORECASE | re.DOTALL)
UNCLOSED_THINK_PATTERN = re.compile(r"<think\b[^>]*>.*$", re.IGNORECASE | re.DOTALL)


def strip_think_blocks(text: object) -> str:
    """移除模型输出中的思考过程，避免展示给前端用户。"""
    if text is None:
        return ""

    content = str(text)
    content = THINK_BLOCK_PATTERN.sub("", content)
    content = UNCLOSED_THINK_PATTERN.sub("", content)
    return content.strip()
