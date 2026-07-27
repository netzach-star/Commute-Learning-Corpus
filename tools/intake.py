#!/usr/bin/env python3
"""收稿：校验新增/改动的语料 HTML，更新 README 目录表，提交并推送。

把 GPT 生成的 HTML 放进 语料/<领域>/ 之后，跑这一条命令即可：

    python3 tools/intake.py           # 校验 → 更新目录 → 提交 → 推送
    python3 tools/intake.py --check   # 只校验，不改动仓库
    python3 tools/intake.py --no-push # 校验并提交，但不推送

校验不通过会中止，不会提交。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAINS = ["数学", "计算机", "AI", "马列", "其他"]
NAME_RE = re.compile(r"^(\d{2})_.+\.html$")
FULL_NAME_RE = re.compile(r"^\d{2}_[^_]+_.+\.html$")

# 会让平板离线打开时失效的外部资源引用
EXTERNAL_PATTERNS = [
    (re.compile(r"<link[^>]+href\s*=\s*[\"']?https?://", re.I), "外部样式表 <link>"),
    (re.compile(r"<script[^>]+src\s*=\s*[\"']?https?://", re.I), "外部脚本 <script src>"),
    (re.compile(r"<img[^>]+src\s*=\s*[\"']?https?://", re.I), "外链图片 <img>"),
    (re.compile(r"<(?:iframe|video|audio|source|embed)[^>]+(?:src|href)\s*=\s*[\"']?https?://", re.I), "外部嵌入资源"),
    (re.compile(r"@import\s+(?:url\()?\s*[\"']?https?://", re.I), "CSS @import 外部地址"),
    (re.compile(r"url\(\s*[\"']?https?://", re.I), "CSS url() 外部地址"),
]

# 未转换的 LaTeX 定界符（扫描前会剔除 annotation/script/style/pre/code）
LATEX_PATTERNS = [
    (re.compile(r"\$\$"), r"$$"),
    (re.compile(r"\\\("), r"\("),
    (re.compile(r"\\\)"), r"\)"),
    (re.compile(r"\\\["), r"\["),
    (re.compile(r"\\\]"), r"\]"),
    (re.compile(r"\\begin\{"), r"\begin{"),
]

STRIP_RE = re.compile(
    r"<annotation\b.*?</annotation>|<script\b.*?</script>|<style\b.*?</style>"
    r"|<pre\b.*?</pre>|<code\b.*?</code>",
    re.S | re.I,
)


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f"git {' '.join(args)} 失败：\n{r.stderr.strip()}")
    return r.stdout


def changed_articles() -> list[tuple[str, Path]]:
    """返回 [(状态, 路径)]，状态为 新增 / 改动。"""
    # core.quotePath=false：否则中文路径会被转义成 \350\257\255... 无法解析
    out = git(
        "-c", "core.quotePath=false",
        "status", "--porcelain", "--untracked-files=all", "--", "语料",
    )
    found = []
    for line in out.splitlines():
        if not line.strip():
            continue
        code, _, name = line[:2], line[2], line[3:]
        path = Path(name.strip().strip('"'))
        if path.suffix.lower() != ".html":
            continue
        state = "新增" if "?" in code or "A" in code else "改动"
        found.append((state, path))
    return sorted(found, key=lambda t: str(t[1]))


def previous_size(path: Path) -> int | None:
    """该文件在 HEAD 中的字节数；文件是新增的则返回 None。"""
    r = subprocess.run(
        ["git", "show", f"HEAD:{path.as_posix()}"],
        cwd=ROOT, capture_output=True,
    )
    return len(r.stdout) if r.returncode == 0 else None


def check_article(path: Path) -> tuple[list[str], list[str]]:
    """返回 (阻断提交的问题, 仅提示的警告)。"""
    full = ROOT / path
    problems: list[str] = []
    warnings: list[str] = []

    # 追加反馈时 GPT 要重新吐出整篇 HTML，中途截断会让正文悄悄少一大块。
    # 新版明显短于旧版一律拦下——正常的"追加反馈"只会变长。
    old = previous_size(path)
    if old is not None:
        new = full.stat().st_size
        if new < old * 0.9:
            problems.append(
                f"比 HEAD 版本短了 {(1 - new / old) * 100:.0f}%"
                f"（{old} → {new} 字节），疑似重新生成时截断"
            )
        elif new < old:
            warnings.append(f"比 HEAD 版本略短（{old} → {new} 字节），确认不是删了内容")

    domain = path.parent.name
    if domain not in DOMAINS:
        problems.append(f"不在五个领域目录里（当前在 {path.parent}）")
        return problems, warnings

    m = NAME_RE.match(path.name)
    if not m:
        problems.append("文件名缺少两位数字编号前缀，应为 NN_主题系列_文章短标题.html")
    else:
        if not FULL_NAME_RE.match(path.name):
            warnings.append("文件名只有 NN_标题，缺少中间的主题系列段")
        no = m.group(1)
        siblings = [
            p for p in (ROOT / "语料" / domain).glob(f"{no}_*.html") if p.name != path.name
        ]
        if siblings:
            problems.append(f"编号 {no} 已被占用：{siblings[0].name}")

    text = full.read_text(encoding="utf-8", errors="replace")

    if len(text) < 8000:
        problems.append(f"正文过短（{len(text)} 字符），疑似截断")
    if not re.search(r"<!doctype\s+html", text, re.I):
        problems.append("缺少 <!doctype html>")
    if not re.search(r'<html[^>]+lang\s*=\s*["\']?zh', text, re.I):
        problems.append('缺少 <html lang="zh-CN">')
    if not re.search(r'<meta[^>]+charset\s*=\s*["\']?utf-8', text, re.I):
        problems.append("缺少 <meta charset=utf-8>")
    if not re.search(r'<meta[^>]+name\s*=\s*["\']?viewport', text, re.I):
        problems.append("缺少 viewport meta")
    if not re.search(r"<title\b[^>]*>\s*\S", text, re.I):
        problems.append("缺少非空 <title>")
    if not re.search(r'id\s*=\s*["\']?reader-feedback', text, re.I):
        problems.append("缺少 id=reader-feedback 反馈区")

    for pattern, label in EXTERNAL_PATTERNS:
        if pattern.search(text):
            problems.append(f"含{label}——平板离线打开会失效")

    body = STRIP_RE.sub(" ", text)
    for pattern, label in LATEX_PATTERNS:
        if pattern.search(body):
            problems.append(f"正文残留未转换的 LaTeX 定界符 {label}")

    if domain == "数学" and not re.search(r"<math\b", text, re.I):
        warnings.append("数学领域文章不含 <math> 标签，确认公式真的用了 MathML")

    return problems, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验，不改动仓库")
    ap.add_argument("--no-push", action="store_true", help="提交但不推送")
    args = ap.parse_args()

    articles = changed_articles()
    if not articles:
        print("语料/ 下没有新增或改动的 HTML，无事可做。")
        return 0

    print(f"发现 {len(articles)} 个待收文件：\n")
    failed = False
    for state, path in articles:
        problems, warnings = check_article(path)
        mark = "❌" if problems else ("⚠️ " if warnings else "✅")
        print(f"{mark} [{state}] {path}")
        for p in problems:
            print(f"     ✗ {p}")
            failed = True
        for w in warnings:
            print(f"     · {w}（仅提示，不阻断）")
    print()

    if failed:
        print("校验未通过，已中止，未提交任何内容。")
        print("修好上面的问题后重跑；确认是误报的话，用 git 手动提交。")
        return 1

    if args.check:
        print("校验通过（--check 模式，未改动仓库）。")
        return 0

    subprocess.run([sys.executable, str(ROOT / "tools/build_index.py")], cwd=ROOT, check=True)

    git("add", "-A", "--", "语料", "README.md")
    added = sum(1 for s, _ in articles if s == "新增")
    edited = len(articles) - added
    bits = ([f"新增 {added} 篇"] if added else []) + ([f"更新 {edited} 篇"] if edited else [])
    subject = "收稿：" + "、".join(bits)
    body = "\n".join(f"- [{s}] {p}" for s, p in articles)
    git("commit", "-m", subject, "-m", body)
    print(f"\n已提交：{subject}")

    if args.no_push:
        print("--no-push，未推送。")
        return 0

    git("push", "origin", "HEAD")
    print("已推送到 origin。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
