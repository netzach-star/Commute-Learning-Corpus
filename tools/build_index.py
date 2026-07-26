#!/usr/bin/env python3
"""重新生成 README.md 中 <!-- INDEX:START --> 与 <!-- INDEX:END --> 之间的语料目录表。

用法：python3 tools/build_index.py
只扫描 语料/ 下的五个领域目录，忽略其他内容。
"""

from __future__ import annotations

import datetime
import html
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "语料"
README = ROOT / "README.md"
DOMAINS = ["数学", "计算机", "AI", "马列", "其他"]

START = "<!-- INDEX:START -->"
END = "<!-- INDEX:END -->"

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
NUM_RE = re.compile(r"^(\d+)_")


def read_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    m = TITLE_RE.search(text)
    if not m:
        return "（缺少 title）"
    return " ".join(html.unescape(m.group(1)).split())


def build() -> str:
    today = datetime.date.today().isoformat()
    out = [
        START,
        "",
        f"**最后更新：{today}**　"
        "新增文章后请更新本表；编号取所在领域当前最大值加一。",
        "",
    ]

    for domain in DOMAINS:
        folder = CORPUS / domain
        files = sorted(folder.glob("*.html")) if folder.is_dir() else []

        numbers = [int(m.group(1)) for f in files if (m := NUM_RE.match(f.name))]
        next_no = (max(numbers) + 1) if numbers else 1

        out.append(f"### 语料/{domain}/　—　共 {len(files)} 篇，下一篇编号 `{next_no:02d}`")
        out.append("")

        if not files:
            out.append("_（暂无文章）_")
            out.append("")
            continue

        out.append("| 编号 | 标题 | 文件 |")
        out.append("| --- | --- | --- |")
        for f in files:
            m = NUM_RE.match(f.name)
            no = m.group(1) if m else "—"
            href = urllib.parse.quote(f"语料/{domain}/{f.name}")
            title = read_title(f).replace("|", "\\|")
            name = f.name.replace("|", "\\|")
            out.append(f"| {no} | {title} | [{name}]({href}) |")
        out.append("")

    out.append(END)
    return "\n".join(out)


def main() -> int:
    if not README.exists():
        print(f"找不到 {README}", file=sys.stderr)
        return 1

    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print(f"README.md 缺少 {START} / {END} 标记", file=sys.stderr)
        return 1

    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    README.write_text(head + build() + tail, encoding="utf-8")
    print("README.md 目录表已更新")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
