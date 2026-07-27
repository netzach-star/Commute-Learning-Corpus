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

DOWNLOADS = Path.home() / "Downloads"
ARCHIVE = DOWNLOADS / "已收稿"
# 浏览器重复下载会加 " (1)" 后缀，收稿时去掉
DEDUP_RE = re.compile(r"\s*\((\d+)\)$")
DOMAIN_PREFIX_RE = re.compile(r"^(数学|计算机|AI|马列|其他)[-_]\s*")
META_RE = re.compile(r"<meta\b[^>]*>", re.I)
ATTR_RE = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"|(\w[\w-]*)\s*=\s*\'([^\']*)\'')

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


def detect_domain(text: str, filename: str) -> str | None:
    """判断文章属于哪个领域：优先 <meta name="corpus-domain">，其次文件名前缀。"""
    for tag in META_RE.findall(text[:4000]):
        attrs = {}
        for m in ATTR_RE.finditer(tag):
            key = (m.group(1) or m.group(3) or "").lower()
            attrs[key] = m.group(2) if m.group(2) is not None else m.group(4)
        if attrs.get("name", "").lower() == "corpus-domain":
            value = (attrs.get("content") or "").strip()
            if value in DOMAINS:
                return value

    m = DOMAIN_PREFIX_RE.match(filename)
    if m:
        return m.group(1)
    return None


def already_collected(clean: str, data: bytes) -> bool:
    """同名同内容的文件已在某个领域目录里 —— 这份下载是旧的，安静跳过。"""
    for domain in DOMAINS:
        p = ROOT / "语料" / domain / clean
        if p.is_file() and p.read_bytes() == data:
            return True
    return False


def stage_from_downloads() -> tuple[dict[Path, Path], list[str]]:
    """把 ~/Downloads 里的语料 HTML 复制进对应领域目录。

    返回 ({下载文件: 仓库内路径}, 跳过说明)。复制而非移动——校验没过时
    原件还在 Downloads，不会丢稿。
    """
    staged: dict[Path, Path] = {}
    notes: list[str] = []

    if not DOWNLOADS.is_dir():
        return staged, [f"找不到下载目录 {DOWNLOADS}"]

    for src in sorted(DOWNLOADS.glob("*.html")):
        text = src.read_text(encoding="utf-8", errors="replace")
        stem = DEDUP_RE.sub("", src.stem)
        clean = DOMAIN_PREFIX_RE.sub("", stem) + ".html"

        if not NAME_RE.match(clean):
            continue  # 不是语料文件，安静跳过

        data = src.read_bytes()
        if already_collected(clean, data):
            continue  # 同名同内容已在仓库里，是旧下载

        domain = detect_domain(text, stem)
        if domain is None:
            notes.append(f"{src.name}：判断不出领域（缺 corpus-domain 且文件名无领域前缀），已跳过")
            continue

        dest = ROOT / "语料" / domain / clean
        rel = dest.relative_to(ROOT)
        if dest.exists() and dest.read_bytes() == src.read_bytes():
            notes.append(f"{src.name}：与仓库内现有文件完全相同，已跳过")
            continue

        # 目标文件有未提交改动时不覆盖：那些改动可能是手工编辑，
        # 一旦覆盖后校验失败，回滚只能退回 HEAD，改动就没了。
        if dest.exists() and git(
            "-c", "core.quotePath=false", "status", "--porcelain", "--", rel.as_posix()
        ).strip():
            notes.append(f"{src.name}：目标 {rel} 有未提交改动，为免覆盖已跳过")
            continue

        dest.write_bytes(src.read_bytes())
        staged[src] = dest.relative_to(ROOT)
        notes.append(f"{src.name}  →  语料/{domain}/{clean}")

    return staged, notes


def archive_downloads(staged: dict[Path, Path]) -> None:
    """收稿成功后把下载目录里的原件挪进 已收稿/，避免下次重复扫描。"""
    if not staged:
        return
    ARCHIVE.mkdir(exist_ok=True)
    for src in staged:
        target = ARCHIVE / src.name
        n = 1
        while target.exists():
            target = ARCHIVE / f"{src.stem} ({n}){src.suffix}"
            n += 1
        src.rename(target)
    print(f"已把 {len(staged)} 个原件移入 {ARCHIVE}")


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


def rollback(staged: dict[Path, Path]) -> None:
    """校验失败时撤掉刚复制进来的文件，让仓库回到干净状态。"""
    for dest in staged.values():
        full = ROOT / dest
        r = subprocess.run(
            ["git", "cat-file", "-e", f"HEAD:{dest.as_posix()}"],
            cwd=ROOT, capture_output=True,
        )
        if r.returncode == 0:
            git("checkout", "HEAD", "--", dest.as_posix())  # 原有文件：还原
        elif full.exists():
            full.unlink()  # 新文件：删掉
    if staged:
        print(f"已撤回 {len(staged)} 个文件，仓库未被改动（下载目录里的原件都还在）。")


def detect() -> int:
    """完全只读地报告有多少待收稿件。不复制、不改动任何文件。

    给 SessionStart hook 用——自动跑的东西不该碰工作区。
    """
    pending: list[str] = []

    if DOWNLOADS.is_dir():
        for src in sorted(DOWNLOADS.glob("*.html")):
            text = src.read_text(encoding="utf-8", errors="replace")
            stem = DEDUP_RE.sub("", src.stem)
            clean = DOMAIN_PREFIX_RE.sub("", stem) + ".html"
            if not NAME_RE.match(clean):
                continue
            if already_collected(clean, src.read_bytes()):
                continue

            domain = detect_domain(text, stem)
            if domain is None:
                pending.append(f"{src.name}（判断不出领域，需人工指定）")
                continue
            dest = ROOT / "语料" / domain / clean
            if dest.exists() and dest.read_bytes() == src.read_bytes():
                continue
            pending.append(f"{src.name} → 语料/{domain}/{clean}")

    in_repo = [f"{s} {p}" for s, p in changed_articles()]

    if not pending and not in_repo:
        return 0

    print("【待收稿件】")
    for p in pending:
        print(f"  下载目录：{p}")
    for p in in_repo:
        print(f"  仓库内未提交：{p}")
    print("跑 `python3 tools/intake.py --from-downloads` 完成收稿（校验 → 更新目录 → 提交推送）。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--detect", action="store_true", help="只读报告待收稿件，不改动任何文件")
    ap.add_argument("--check", action="store_true", help="只校验，不改动仓库")
    ap.add_argument("--no-push", action="store_true", help="提交但不推送")
    ap.add_argument(
        "--from-downloads", action="store_true",
        help=f"先把 {DOWNLOADS} 里的语料 HTML 收进对应领域目录",
    )
    args = ap.parse_args()

    if args.detect:
        return detect()

    staged: dict[Path, Path] = {}
    if args.from_downloads:
        staged, notes = stage_from_downloads()
        for n in notes:
            print(f"  {n}")
        if notes:
            print()

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
        rollback(staged)
        print("修好上面的问题后重跑；确认是误报的话，用 git 手动提交。")
        return 1

    if args.check:
        rollback(staged)
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
        archive_downloads(staged)
        return 0

    git("push", "origin", "HEAD")
    print("已推送到 origin。")
    archive_downloads(staged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
