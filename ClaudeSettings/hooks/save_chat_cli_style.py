#!/usr/bin/env python3
"""
AI Code 对话保存脚本（CLI 样式版）
模拟终端显示效果，包含工具调用折叠、代码块等

Environment Variables:
- ZCO_CHAT_SAVE_CLI: Must be "1" to enable this hook
- ZCO_CHAT_SAVE_DIR: Output directory (default: ${GIT_ROOT}/_.zco_hist)
"""
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def get_git_root(project_dir: Path = None) -> Path:
    """##;获取 Git 仓库根目录"""
    try:
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


def get_hist_dir(project_dir: Path = None) -> Path:
    """##;获取历史记录目录"""
    hist_dir_name = os.environ.get('ZCO_CHAT_SAVE_DIR', None)
    git_root = get_git_root(project_dir)
    if not hist_dir_name:
        hist_dir = git_root / '_.zco_hist'
    else:
        hist_dir = os.path.abspath(os.path.join(str(git_root), hist_dir_name))
    hist_dir.mkdir(exist_ok=True)
    return hist_dir


class MessageFormatter:
    """##;消息格式化器，模拟 CLI 样式"""

    ##;图标定义
    ICONS = {
        'user': '❯',           ##;用户提示符
        'assistant': '⬢',      ##;Claude 图标
        'tool_call': '◖',      ##;工具调用
        'tool_result': '◗',    ##;工具结果
        'read': '📄',
        'write': '✏️',
        'edit': '✏️',
        'bash': '⚡',
        'task': '🔧',
        'glob': '📁',
        'grep': '🔍',
        'webfetch': '🌐',
        'websearch': '🔎',
    }

    @classmethod
    def format_tool_call(cls, tool_name: str, tool_input: dict) -> str:
        """##;格式化工具调用（可折叠样式）"""
        icon = cls.ICONS.get(tool_name.lower(), '🔧')

        ##;提取关键参数显示
        summary = ""
        if tool_name == "Read":
            summary = tool_input.get("file_path", "")
        elif tool_name == "Write":
            summary = tool_input.get("file_path", "")
        elif tool_name == "Edit":
            summary = tool_input.get("file_path", "")
        elif tool_name == "Bash":
            cmd = tool_input.get("command", "")
            summary = cmd[:60] + "..." if len(cmd) > 60 else cmd
        elif tool_name == "Task":
            summary = f"Agent: {tool_input.get('subagent_type', 'unknown')}"
        else:
            summary = str(tool_input)[:60]

        lines = [
            f"\n<details>",
            f"<summary>{icon} <b>{tool_name}</b> {summary}</summary>",
            "",
            "```json",
            json.dumps(tool_input, indent=2, ensure_ascii=False),
            "```",
            "</details>",
        ]
        return "\n".join(lines)

    @classmethod
    def format_tool_result(cls, tool_name: str, result: str) -> str:
        """##;格式化工具结果"""
        icon = cls.ICONS.get('tool_result')

        ##;截断过长的结果
        max_len = 500
        if len(result) > max_len:
            display_result = result[:max_len] + f"\n\n... ({len(result) - max_len} 字符已省略)"
        else:
            display_result = result

        lines = [
            f"<details>",
            f"<summary>{icon} <b>{tool_name}</b> 结果</summary>",
            "",
            "```",
            display_result,
            "```",
            "</details>\n",
        ]
        return "\n".join(lines)

    @classmethod
    def format_content_item(cls, item: dict, tool_results: dict) -> str:
        """##;格式化单个内容项"""
        item_type = item.get("type")

        if item_type == "text":
            return item.get("text", "")

        elif item_type == "tool_use":
            tool_name = item.get("name", "unknown")
            tool_id = item.get("id", "")
            tool_input = item.get("input", {})

            output = [cls.format_tool_call(tool_name, tool_input)]

            ##;如果有结果，立即跟随显示
            if tool_id in tool_results:
                output.append(cls.format_tool_result(tool_name, tool_results[tool_id]))

            return "\n".join(output)

        return str(item)

    @classmethod
    def format_message(cls, msg: dict, tool_results: dict) -> str:
        """##;格式化完整消息"""
        msg_type = msg.get("type", "unknown")
        inner_msg = msg.get("message", {})
        content = inner_msg.get("content", "")

        lines = []

        ##;消息头部
        if msg_type == "user":
            lines.append(f"\n### {cls.ICONS['user']} **User**\n")
        else:
            lines.append(f"\n### {cls.ICONS['assistant']} **Claude**\n")

        ##;内容处理
        if isinstance(content, str):
            lines.append(content)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    lines.append(cls.format_content_item(item, tool_results))
                else:
                    lines.append(str(item))

        return "\n".join(lines)


def extract_tool_results(messages: List[Dict]) -> Dict[str, str]:
    """##;提取所有工具结果"""
    results = {}
    for msg in messages:
        ##;外层 toolUseResult
        tool_result = msg.get("toolUseResult")
        if tool_result:
            tool_id = tool_result.get("tool_use_id", "")
            result_content = tool_result.get("content", "")

            if isinstance(result_content, list):
                text_parts = []
                for part in result_content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                results[tool_id] = "\n".join(text_parts)
            else:
                results[tool_id] = str(result_content)

        ##;内层 content 中的 tool_result
        inner_msg = msg.get("message", {})
        content = inner_msg.get("content", [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "tool_result":
                    tool_id = item.get("tool_use_id", "")
                    result_content = item.get("content", "")

                    if isinstance(result_content, list):
                        text_parts = []
                        for part in result_content:
                            if isinstance(part, dict) and part.get("type") == "text":
                                text_parts.append(part.get("text", ""))
                        results[tool_id] = "\n".join(text_parts)
                    else:
                        results[tool_id] = str(result_content)

    return results


def parse_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """##;解析 transcript 文件"""
    messages = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    if msg and msg.get("type") in ["user", "assistant"]:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)

    return messages


def generate_cli_style_markdown(messages: List[Dict], session_id: str, model: str = None) -> str:
    """##;生成 CLI 风格的 Markdown"""
    lines = [
        "# AI Code 会话记录",
        "",
        f"<div align='right'>",
        f"",
        f"**会话 ID**: `{session_id}`  ",
    ]

    ##;添加模型信息（如果有）
    if model:
        lines.append(f"**模型**: `{model}`  ")

    lines.extend([
        f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"</div>",
        "",
        "---",
    ])

    ##;提取工具结果
    tool_results = extract_tool_results(messages)

    ##;格式化每条消息
    formatter = MessageFormatter()
    for msg in messages:
        formatted = formatter.format_message(msg, tool_results)
        lines.append(formatted)

    lines.extend([
        "",
        "---",
        f"*生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
    ])

    return "\n".join(lines)


def save_conversation(transcript_path: str, project_dir: str, session_id: str, model: str = None):
    """##;保存对话"""
    try:
        messages = parse_transcript(transcript_path)
        if not messages:
            print("No messages to save", file=sys.stderr)
            return

        ##;生成 CLI 样式的 Markdown
        markdown_content = generate_cli_style_markdown(messages, session_id, model)

        ##;文件名
        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
        filename = f"log_{timestamp}_cli_style.md"

        hist_dir = get_hist_dir(project_dir)
        output_file = hist_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"CLI style conversation saved to: {output_file}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def main():
    try:
        if os.environ.get('ZCO_CHAT_SAVE_CLI') != '1':
            sys.exit(0)

        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')

        if hook_event == 'Stop':
            transcript_path = input_data.get('transcript_path', '')
            cwd = input_data.get('cwd', '')
            session_id = input_data.get('session_id', 'unknown')
            model = input_data.get('model')  ##;尝试获取模型名

            if transcript_path and cwd:
                save_conversation(transcript_path, cwd, session_id, model)

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
