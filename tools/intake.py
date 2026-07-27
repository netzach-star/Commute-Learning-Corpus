#!/usr/bin/env python3
"""收稿：从下载目录认领语料 HTML，校验、编号、更新目录表、提交并推送。

日常只用这一条：

    python3 tools/intake.py --from-downloads

它会：认领 ~/Downloads 里带 corpus-domain 的稿子 → 按领域归档并分配编号 →
逐篇校验 → 更新 README 目录表 → 提交 → 推送 → 把下载原件挪进 ~/Downloads/已收稿/。

其他开关：

    --detect          只读报告有多少待收稿，不碰任何文件（SessionStart hook 用它）
    --check           校验后回滚，不提交
    --no-push         提交但不推送
    --domain <领域>   稿子缺 corpus-domain 时按此领域收（收旧稿用）
    --delete-after    推送成功后直接删掉下载原件，不留 已收稿/

校验不通过会中止并回滚，下载目录里的原件一个字都不动。
"""

from __future__ import annotations

import argparse
import hashlib
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


def repo_digests() -> set[str]:
    """仓库内所有语料文章的内容摘要。"""
    out = set()
    for domain in DOMAINS:
        folder = ROOT / "语料" / domain
        if folder.is_dir():
            for p in folder.glob("*.html"):
                out.add(hashlib.sha256(p.read_bytes()).hexdigest())
    return out


def already_collected(data: bytes, digests: set[str] | None = None) -> bool:
    """内容已在仓库里 —— 这份下载是冗余的。

    按内容比对而非文件名：收稿时会自动分配编号并重命名，
    按名字找会漏掉所有被改过名的稿子。
    """
    if digests is None:
        digests = repo_digests()
    return hashlib.sha256(data).hexdigest() in digests


def next_number(domain: str, claimed: set[Path]) -> int:
    """该领域下一个空闲编号，把本批次已占用的一并算上。"""
    folder = ROOT / "语料" / domain
    nums = [int(m.group(1)) for p in folder.glob("*.html") if (m := NAME_RE.match(p.name))]
    nums += [int(m.group(1)) for p in claimed if p.parent == folder and (m := NAME_RE.match(p.name))]
    return max(nums) + 1 if nums else 1


def resolve_target(domain: str, stem: str, claimed: set[Path]) -> tuple[Path, str | None]:
    """决定这篇稿子该落到哪个文件名。编号由这里分配，GPT 不需要管。

    stem 是去掉 " (N)" 和领域前缀后的文件名主干（不含 .html）。
    返回 (目标路径, 需要告知用户的说明)。
    """
    folder = ROOT / "语料" / domain
    m = re.match(r"^(\d{2})_(.+)$", stem)
    body = m.group(2) if m else stem

    # 已有同一篇（编号之后的部分相同）→ 视为新版本，沿用原文件名和编号
    for p in sorted(list(folder.glob("*.html")) + [q for q in claimed if q.parent == folder]):
        pm = NAME_RE.match(p.name)
        if pm and p.stem[len(pm.group(1)) + 1:] == body:
            return p, None

    if m:
        want = m.group(1)
        taken = list(folder.glob(f"{want}_*.html")) + [
            q for q in claimed if q.parent == folder and q.name.startswith(f"{want}_")
        ]
        if not taken:
            return folder / f"{want}_{body}.html", None
        n = next_number(domain, claimed)
        return folder / f"{n:02d}_{body}.html", f"编号 {want} 已被 {taken[0].name} 占用，改用 {n:02d}"

    n = next_number(domain, claimed)
    return folder / f"{n:02d}_{body}.html", f"未带编号，自动分配 {n:02d}"


def plan_from_downloads(fallback_domain: str | None = None) -> list[tuple[Path, Path | None, str]]:
    """规划 ~/Downloads 里每个语料 HTML 的去向。纯只读，不写任何文件。

    fallback_domain：文件里没有 corpus-domain 时用它兜底，供收旧稿使用。
    返回 [(下载文件, 目标路径或 None, 说明)]；目标为 None 表示不收。
    """
    plan: list[tuple[Path, Path | None, str]] = []
    if not DOWNLOADS.is_dir():
        return plan

    claimed: set[Path] = set()
    digests = repo_digests()
    for src in sorted(DOWNLOADS.glob("*.html")):
        text = src.read_text(encoding="utf-8", errors="replace")
        data = src.read_bytes()
        stem = DOMAIN_PREFIX_RE.sub("", DEDUP_RE.sub("", src.stem))

        # 先看是不是早就收过的旧下载——这一步必须在领域判断之前，
        # 否则仓库里那些没有 corpus-domain 的老文章会被反复报成"缺标签"
        if already_collected(data, digests):
            continue

        domain = detect_domain(text, DEDUP_RE.sub("", src.stem))
        looks_like_corpus = bool(re.search(r'id\s*=\s*["\']?reader-feedback', text, re.I))
        if domain is None and fallback_domain and looks_like_corpus:
            domain = fallback_domain
        if domain is None:
            # 有反馈区说明它长得像本项目的语料，只是漏了 corpus-domain
            if looks_like_corpus:
                plan.append((src, None, "缺 corpus-domain，无法判断领域；用 --domain <领域> 兜底"))
            continue  # 其余 HTML 不是本项目的，安静忽略

        dest, note = resolve_target(domain, stem, claimed)
        rel = dest.relative_to(ROOT)

        if dest.exists() and dest.read_bytes() == data:
            continue  # 内容一致，无需收

        # 目标文件有未提交改动时不覆盖：那些改动可能是手工编辑，
        # 一旦覆盖后校验失败，回滚只能退回 HEAD，改动就没了。
        if dest.exists() and git(
            "-c", "core.quotePath=false", "status", "--porcelain", "--", rel.as_posix()
        ).strip():
            plan.append((src, None, f"目标 {rel} 有未提交改动，为免覆盖已跳过"))
            continue

        claimed.add(dest)
        label = f"→ {rel}" + (f"（{note}）" if note else "")
        plan.append((src, dest, label))

    return plan


def stage_from_downloads(fallback_domain: str | None = None) -> tuple[dict[Path, Path], list[str]]:
    """按 plan 把下载目录里的稿子复制进领域目录。

    复制而非移动——校验没过时原件还在 Downloads，不会丢稿。
    """
    staged: dict[Path, Path] = {}
    notes: list[str] = []
    for src, dest, label in plan_from_downloads(fallback_domain):
        if dest is None:
            notes.append(f"{src.name}：{label}")
            continue
        dest.write_bytes(src.read_bytes())
        staged[src] = dest.relative_to(ROOT)
        notes.append(f"{src.name}  {label}")
    return staged, notes


def redundant_downloads() -> list[Path]:
    """下载目录里与仓库内某文件逐字节相同的稿子。

    内容已经在仓库里，这份下载纯属冗余，清掉不会丢任何东西。
    """
    out: list[Path] = []
    if not DOWNLOADS.is_dir():
        return out
    digests = repo_digests()
    for src in sorted(DOWNLOADS.glob("*.html")):
        if already_collected(src.read_bytes(), digests):
            out.append(src)
    return out


def archive_downloads(staged: dict[Path, Path], delete: bool = False) -> None:
    """清理下载目录：把已安全入库的原件移进 已收稿/，或直接删除。

    只在校验通过、提交并推送之后调用——此时内容已经在 GitHub 上，
    本地这份原件没有独立价值了。
    """
    targets = list(staged) + [p for p in redundant_downloads() if p not in staged]
    if not targets:
        return

    if delete:
        for src in targets:
            src.unlink()
        print(f"已删除 {len(targets)} 个下载原件（内容已在 GitHub 上）")
        return

    ARCHIVE.mkdir(exist_ok=True)
    for src in targets:
        target = ARCHIVE / src.name
        n = 1
        while target.exists():
            target = ARCHIVE / f"{src.stem} ({n}){src.suffix}"
            n += 1
        src.rename(target)
    print(f"已把 {len(targets)} 个原件移入 {ARCHIVE}")


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


def detect(fallback_domain: str | None = None) -> int:
    """完全只读地报告有多少待收稿件。不复制、不改动任何文件。

    给 SessionStart hook 用——自动跑的东西不该碰工作区。
    """
    pending = [f"{src.name} {label}" for src, _, label in plan_from_downloads(fallback_domain)]
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
    ap.add_argument(
        "--domain", choices=DOMAINS,
        help="文件缺少 corpus-domain 时按此领域收（用于收旧稿）",
    )
    ap.add_argument(
        "--delete-after", action="store_true",
        help="推送成功后直接删除下载原件，而不是移进 已收稿/",
    )
    args = ap.parse_args()

    if args.detect:
        return detect(args.domain)

    staged: dict[Path, Path] = {}
    if args.from_downloads:
        staged, notes = stage_from_downloads(args.domain)
        for n in notes:
            print(f"  {n}")
        if notes:
            print()

    articles = changed_articles()
    if not articles:
        print("语料/ 下没有新增或改动的 HTML，无事可做。")
        # 内容已在仓库里的下载原件仍可清理（例如上次推送失败、这次补做）
        archive_downloads({}, args.delete_after)
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
        archive_downloads(staged, args.delete_after)
        return 0

    r = subprocess.run(["git", "push", "origin", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print("\n⚠️  已提交到本地，但推送失败：")
        print("   " + (r.stderr.strip().splitlines() or ["未知错误"])[-1])
        print("   下载目录里的原件保留未动——内容没上 GitHub 之前不清理。")
        print("   修好网络/代理后跑 `git push` 补推，再重跑本脚本即可清理原件。")
        return 1

    print("已推送到 origin。")
    archive_downloads(staged, args.delete_after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
