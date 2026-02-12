#!/usr/bin/env python3
"""
##;zco-hist-smy: 对话历史汇总工具
##;用法: zco-hist-smy [-d days]
##;  -d 1   当天 (默认)
##;  -d 7   近 7 天
##;  -d 0   所有历史
"""

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_hist_dir(project_dir: Path = None) -> Path:
    """获取历史记录目录"""
    hist_dir_name = os.environ.get('ZCO_CHAT_SAVE_DIR', None)
    git_root = get_git_root(project_dir)
    if not hist_dir_name:
        hist_dir = git_root / '_.zco_hist'
    else:
        hist_dir = os.path.abspath(os.path.join(str(git_root), hist_dir_name))
    hist_dir.mkdir(exist_ok=True)
    return hist_dir


def get_git_root(project_dir: Path = None) -> Path:
    """获取当前 Git 仓库根目录"""
    try:
        # 执行 git rev-parse --show-toplevel 命令
        if project_dir:
            result = subprocess.run(
                ['git', '-C', str(project_dir), 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def parse_args():
    """##;解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="汇总 _.zco_hist 目录下的对话历史记录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  zco-hist-smy        # 汇总当天
  zco-hist-smy -d 1   # 汇总当天（显式）
  zco-hist-smy -d 7   # 汇总近 7 天
  zco-hist-smy -d 0   # 汇总所有历史记录
        """,
    )
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        default=1,
        help="天数范围 (默认: 1, 0 表示不限)",
    )
    return parser.parse_args()


def calculate_date_range(days: int) -> Tuple[Optional[datetime], datetime]:
    """##;计算日期范围
    ##;Args:
    ##;    days: 天数，0 表示不限
    ##;Returns:
    ##;    (start_date, end_date)，start_date 可能为 None
    """
    end_date = datetime.now()
    if days == 0:
        return None, end_date
    start_date = end_date - timedelta(days=days - 1)
    ##;重置为当天开始
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return start_date, end_date


def get_hist_files(
    hist_dir: Path, start_date: Optional[datetime], end_date: datetime
) -> List[Path]:
    """##;获取符合条件的对话文件"""
    if not hist_dir.exists():
        return []

    files = []
    for f in hist_dir.glob("*.md"):
        ##;跳过 debug 文件和汇总文件
        if "debug" in f.name or "smy" in f.name:
            continue

        ##;获取文件修改时间
        mtime = datetime.fromtimestamp(f.stat().st_mtime)

        ##;检查是否在日期范围内
        if start_date is None:
            files.append(f)
        elif start_date <= mtime <= end_date:
            files.append(f)

    ##;按修改时间排序
    files.sort(key=lambda x: x.stat().st_mtime)
    return files


def extract_tools_from_content(content: str) -> List[str]:
    """##;从内容中提取工具名称"""
    tools = []

    ##;匹配折叠面板中的工具名 <summary>📄 <b>Read</b>
    pattern1 = r"<summary>.*?<b>(\w+)</b>"
    tools.extend(re.findall(pattern1, content))

    ##;匹配工具使用统计行
    pattern2 = r"-\s+(\w+):\s*\d+"
    tools.extend(re.findall(pattern2, content))

    return tools


def extract_files_from_content(content: str) -> List[str]:
    """##;从内容中提取文件路径"""
    files = []

    ##;匹配 📄 文件路径
    pattern = r"📄\s+`?([^`\n]+)`?"
    matches = re.findall(pattern, content)
    files.extend(matches)

    ##;匹配代码块中的 file_path
    pattern2 = r'"file_path":\s*"([^"]+)"'
    matches = re.findall(pattern2, content)
    files.extend(matches)

    return list(set(files))


def extract_urls_from_content(content: str) -> List[str]:
    """##;从内容中提取 URLs"""
    urls = []

    ##;匹配 🌐 URL
    pattern = r"🌐\s+(https?://[^\s\n]+)"
    matches = re.findall(pattern, content)
    urls.extend(matches)

    return list(set(urls))


def parse_chat_file(file_path: Path) -> Dict:
    """##;解析单个对话文件"""
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "filename": file_path.name,
            "error": str(e),
            "mtime": datetime.fromtimestamp(file_path.stat().st_mtime),
        }

    ##;提取基本信息
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)

    ##;尝试提取标题（第一个 # 标题）
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem

    ##;提取时间（从文件内容或文件名）
    time_match = re.search(r"\*\*时间\*\*[:：]\s*(.+)", content)
    if time_match:
        try:
            chat_time = datetime.strptime(time_match.group(1).strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            chat_time = mtime
    else:
        chat_time = mtime

    ##;提取工具
    tools = extract_tools_from_content(content)
    tool_counts = Counter(tools)

    ##;提取文件
    files = extract_files_from_content(content)

    ##;提取 URLs
    urls = extract_urls_from_content(content)

    return {
        "filename": file_path.name,
        "title": title,
        "mtime": mtime,
        "chat_time": chat_time,
        "tools": tool_counts,
        "files": files,
        "urls": urls,
        "content_preview": content[:500] if content else "",
    }


def generate_summary(
    files: List[Path], start_date: Optional[datetime], end_date: datetime
) -> Tuple[str, Dict]:
    """##;生成汇总报告
    ##;Returns:
    ##;    (markdown_content, stats_dict)
    """
    ##;解析所有文件
    parsed_files = [parse_chat_file(f) for f in files]
    parsed_files = [p for p in parsed_files if "error" not in p]

    if not parsed_files:
        return "# 对话历史汇总报告\n\n没有找到符合条件的对话记录。\n", {}

    ##;统计数据
    total_chats = len(parsed_files)
    all_tools = Counter()
    all_files = set()
    all_urls = set()

    for p in parsed_files:
        all_tools.update(p["tools"])
        all_files.update(p["files"])
        all_urls.update(p["urls"])

    total_tools = sum(all_tools.values())

    ##;生成 Markdown
    lines = []
    lines.append("# 对话历史汇总报告")
    lines.append("")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    ##;日期范围
    if start_date:
        lines.append(
            f"**统计周期**: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        )
    else:
        lines.append("**统计周期**: 全部历史")

    lines.append(f"**总对话数**: {total_chats}")
    lines.append("")
    lines.append("---")
    lines.append("")

    ##;统计概览
    lines.append("## 📊 统计概览")
    lines.append("")
    lines.append("| 指标 | 数值 |")
    lines.append("|------|------|")
    lines.append(f"| 总对话数 | {total_chats} |")
    lines.append(f"| 使用工具次数 | {total_tools} |")
    lines.append(f"| 涉及文件数 | {len(all_files)} |")
    lines.append(f"| 访问 URLs | {len(all_urls)} |")
    lines.append("")

    ##;工具使用分布
    if all_tools:
        lines.append("### 工具使用分布")
        lines.append("")
        lines.append("| 工具 | 次数 | 占比 |")
        lines.append("|------|------|------|")

        for tool, count in all_tools.most_common():
            percentage = (count / total_tools * 100) if total_tools > 0 else 0
            lines.append(f"| {tool} | {count} | {percentage:.1f}% |")

        lines.append("")

    ##;对话列表
    lines.append("---")
    lines.append("")
    lines.append("## 📝 对话列表")
    lines.append("")

    for idx, p in enumerate(parsed_files, 1):
        lines.append(f"### {idx}. {p['filename']}")
        lines.append("")
        lines.append(f"- **标题**: {p['title']}")
        lines.append(f"- **时间**: {p['chat_time'].strftime('%Y-%m-%d %H:%M:%S')}")

        if p["tools"]:
            tool_str = ", ".join([f"{t}×{c}" for t, c in p["tools"].most_common()])
            lines.append(f"- **工具**: {tool_str}")

        if p["files"]:
            lines.append(f"- **文件**: {', '.join(p['files'][:3])}")
            if len(p["files"]) > 3:
                lines.append(f"  - ... 等 {len(p['files'])} 个文件")

        lines.append("")

    ##;涉及文件汇总
    if all_files:
        lines.append("---")
        lines.append("")
        lines.append("## 📁 涉及文件汇总")
        lines.append("")

        for f in sorted(all_files)[:50]:  # ;最多显示 50 个
            lines.append(f"- `{f}`")

        if len(all_files) > 50:
            lines.append(f"- ... 等共 {len(all_files)} 个文件")

        lines.append("")

    ##;参考资源汇总
    if all_urls:
        lines.append("---")
        lines.append("")
        lines.append("## 🔗 参考资源汇总")
        lines.append("")

        for url in sorted(all_urls):
            lines.append(f"- [{url}]({url})")

        lines.append("")

    ##;页脚
    lines.append("---")
    lines.append("")
    lines.append(f"*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")

    ##;统计字典
    stats = {
        "total_chats": total_chats,
        "total_tools": total_tools,
        "tool_distribution": dict(all_tools),
        "files_count": len(all_files),
        "urls_count": len(all_urls),
    }

    return "\n".join(lines), stats


def main():
    args = parse_args()

    ##;计算日期范围
    start_date, end_date = calculate_date_range(args.days)

    ##;获取项目根目录
    git_root = get_git_root()

    ##;查找 _.zco_hist 目录
    ## hist_dir = git_root / "_.zco_hist"
    hist_dir = get_hist_dir(git_root)
    if not hist_dir.exists():
        print(f"##;@ERROR: 未找到对话目录: {hist_dir}")
        print("请先启用对话保存功能并执行一些对话。")
        return 1

    ##;获取文件列表
    files = get_hist_files(hist_dir, start_date, end_date)

    if not files:
        date_range = (
            f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
            if start_date
            else "全部历史"
        )
        print(f"##;@NOTE: 在 {date_range} 范围内没有找到对话记录")
        return 0

    print(f"##;找到 {len(files)} 个对话文件")

    ##;生成汇总
    markdown_content, stats = generate_summary(files, start_date, end_date)

    ##;确定输出目录
    output_dir = Path(os.environ.get("AICO_DOCS", git_root / "AICO_DOCS"))
    output_dir.mkdir(parents=True, exist_ok=True)

    ##;生成文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    output_file = output_dir / f"zco_hist_smy_{timestamp}.md"

    ##;写入文件
    try:
        output_file.write_text(markdown_content, encoding="utf-8")
        print(f"##;汇总报告已保存: {output_file}")
        print(f"##;统计: {stats.get('total_chats', 0)} 个对话, {stats.get('total_tools', 0)} 次工具调用")
    except Exception as e:
        print(f"##;@ERROR: 保存文件失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
