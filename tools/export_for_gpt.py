#!/usr/bin/env python3
"""把 6 个 SKILL 文件复制到 上传给GPT/，重命名成互不冲突的名字。

用途：ChatGPT 抓不到仓库时，改用"上传项目文件"的降级方案。
五个领域 SKILL 都叫 SKILL.md，平铺上传会撞名，所以在这里改名。

内容逐字节复制，不做任何修改——仓库里的 SKILL 始终是唯一真源。
改完 SKILL 后重跑本脚本，再把 上传给GPT/ 里的文件重新传一次。

用法：python3 tools/export_for_gpt.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "上传给GPT"

MAPPING = [
    (ROOT / "SKILL.md", "SKILL-00-主规则.md"),
    (ROOT / "语料/数学/SKILL.md", "SKILL-01-数学.md"),
    (ROOT / "语料/计算机/SKILL.md", "SKILL-02-计算机.md"),
    (ROOT / "语料/AI/SKILL.md", "SKILL-03-AI.md"),
    (ROOT / "语料/马列/SKILL.md", "SKILL-04-马列.md"),
    (ROOT / "语料/其他/SKILL.md", "SKILL-05-其他.md"),
]


def main() -> int:
    OUT.mkdir(exist_ok=True)

    missing = [str(src.relative_to(ROOT)) for src, _ in MAPPING if not src.is_file()]
    if missing:
        print("以下源文件不存在：" + "、".join(missing))
        return 1

    # 清掉上一轮的产物，避免 SKILL 改名后留下孤儿文件
    for stale in OUT.glob("SKILL-*.md"):
        stale.unlink()

    for src, name in MAPPING:
        shutil.copyfile(src, OUT / name)
        print(f"{src.relative_to(ROOT)}  →  上传给GPT/{name}  ({src.stat().st_size}B)")

    print(f"\n共 {len(MAPPING)} 个文件。把它们全部上传到 ChatGPT 项目的文件区。")
    print("注意：改完 SKILL 后要重跑本脚本并重新上传，否则 GPT 会用旧规则写作。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
