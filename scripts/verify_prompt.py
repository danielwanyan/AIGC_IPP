#!/usr/bin/env python3
"""
Aicolate Prompt 合规性检查脚本
自动检测 System Prompt 中的常见问题：
- 视觉输入变量引用（如 {{All_images}}）
- Markdown 代码块（```）
- 反引号（`）
- 粗体格式（**）
- Markdown 标题（#）
- Markdown 表格（|）
- 分隔线（---）

用法：
    python scripts/verify_prompt.py
    python scripts/verify_prompt.py --path prompts/
"""

import argparse
import re
import sys
from pathlib import Path


# 定义检查规则
RULES = [
    {
        "name": "视觉输入变量引用",
        "pattern": r"\{\{(All_images|Product_image|.*image.*)\}\}",
        "severity": "ERROR",
        "description": "System Prompt 中不能引用视觉输入变量，应移到 User Prompt 中",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "issue_type 数字格式限制",
        "pattern": r"有值（数字）|数字(?!.*还是字符串).*=.*AIGC|数字(?!.*还是字符串).*→.*AIGC",
        "severity": "ERROR",
        "description": "issue_type 判断不应限制为'数字'格式，aigc_video_id 可能是字符串格式。应使用'非 null'或'有值'代替。",
        "files": ["*prompt*.txt"],
    },
    {
        "name": "Markdown 代码块",
        "pattern": r"```",
        "severity": "ERROR",
        "description": "System Prompt 中不能有代码块，JSON 格式示例应移到 User Prompt 中",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "行内反引号",
        "pattern": r"`",
        "severity": "ERROR",
        "description": "System Prompt 中不能有反引号，应直接写文本",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "Markdown 粗体",
        "pattern": r"\*\*",
        "severity": "ERROR",
        "description": "System Prompt 中不能有粗体格式，应用大写或 emoji 强调",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "Markdown 标题",
        "pattern": r"^#",
        "severity": "ERROR",
        "description": "System Prompt 中不能有 Markdown 标题，应用纯文本标题",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "Markdown 表格",
        "pattern": r"^\|.*\|$",
        "severity": "ERROR",
        "description": "System Prompt 中不能有 Markdown 表格，应用纯文本列表",
        "files": ["*system*prompt*.txt"],
    },
    {
        "name": "Markdown 分隔线",
        "pattern": r"^---$",
        "severity": "ERROR",
        "description": "System Prompt 中不能有分隔线，应用空行分隔",
        "files": ["*system*prompt*.txt"],
    },
    # User Prompt 检查 - 确保 JSON 格式示例存在
    {
        "name": "User Prompt JSON 格式检查",
        "pattern": r"```json",
        "severity": "WARNING",
        "description": "User Prompt 中应包含 JSON 输出格式示例",
        "files": ["*user*prompt*.txt"],
        "should_exist": True,  # 这个模式应该存在
    },
]


def match_filename(filename: str, patterns: list) -> bool:
    """检查文件名是否匹配任一模式"""
    import fnmatch
    return any(fnmatch.fnmatch(filename.lower(), p.lower()) for p in patterns)


def check_file(file_path: Path) -> list:
    """检查单个文件的所有规则"""
    issues = []
    content = file_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    for rule in RULES:
        if not match_filename(file_path.name, rule["files"]):
            continue

        matches = []
        for line_num, line in enumerate(lines, 1):
            if re.search(rule["pattern"], line):
                matches.append((line_num, line.strip()))

        should_exist = rule.get("should_exist", False)

        if should_exist:
            # 这个模式应该存在，如果不存在则报错
            if not matches:
                issues.append({
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "file": str(file_path),
                    "line": None,
                    "description": rule["description"],
                    "content": None,
                })
        else:
            # 这个模式不应该存在，如果存在则报错
            for line_num, line_content in matches:
                issues.append({
                    "rule": rule["name"],
                    "severity": rule["severity"],
                    "file": str(file_path),
                    "line": line_num,
                    "description": rule["description"],
                    "content": line_content[:100],
                })

    return issues


def main():
    parser = argparse.ArgumentParser(description="Aicolate Prompt 合规性检查")
    parser.add_argument(
        "--path",
        type=str,
        default="prompts/",
        help="Prompt 文件目录路径（默认: prompts/）",
    )
    args = parser.parse_args()

    prompt_dir = Path(args.path)
    if not prompt_dir.exists():
        print(f"❌ 错误：目录不存在: {prompt_dir}")
        sys.exit(1)

    # 查找所有 .txt 文件
    txt_files = list(prompt_dir.rglob("*.txt"))
    if not txt_files:
        print(f"⚠️  警告：在 {prompt_dir} 中没有找到 .txt 文件")
        sys.exit(0)

    print(f"🔍 正在检查 {len(txt_files)} 个 Prompt 文件...\n")

    all_issues = []
    for file_path in txt_files:
        issues = check_file(file_path)
        all_issues.extend(issues)

    if not all_issues:
        print("✅ 所有 Prompt 文件通过检查！")
        return 0

    # 按严重程度分组
    errors = [i for i in all_issues if i["severity"] == "ERROR"]
    warnings = [i for i in all_issues if i["severity"] == "WARNING"]

    print(f"❌ 发现 {len(errors)} 个错误，⚠️  {len(warnings)} 个警告\n")

    # 打印错误
    if errors:
        print("=" * 80)
        print("❌ 错误（必须修复）：")
        print("=" * 80)
        for issue in errors:
            print(f"\n📄 文件: {issue['file']}")
            if issue["line"]:
                print(f"   行号: {issue['line']}")
            print(f"   规则: {issue['rule']}")
            print(f"   问题: {issue['description']}")
            if issue["content"]:
                print(f"   内容: {issue['content']}")

    # 打印警告
    if warnings:
        print("\n" + "=" * 80)
        print("⚠️  警告（建议修复）：")
        print("=" * 80)
        for issue in warnings:
            print(f"\n📄 文件: {issue['file']}")
            print(f"   规则: {issue['rule']}")
            print(f"   问题: {issue['description']}")

    print("\n" + "=" * 80)
    print(f"📖 详细规范请参考: EU-LLM_Wiki/wiki/projects/aicolate/Aicolate-Prompt-Engineering-Guide.md")
    print("=" * 80)

    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
