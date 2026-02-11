#!/usr/bin/env python3
"""
AI Code 对话自动保存脚本（增强版）
保存完整对话 + 工具调用 + 参考资源

Environment Variables:
- ZCO_CHAT_SAVE_SPEC: Must be "1" to enable this hook
- ZCO_CHAT_SAVE_DIR: Output directory (default: ${GIT_ROOT}/_.zco_hist)
"""
import json
import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Set


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


def extract_keywords(text: str, max_keywords: int = 3) -> str:
    """从文本中提取关键词"""
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', text)
    words = text.split()

    stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
                  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'is', 'are',
                  '请', '帮', '我要', '能否', '如何', '什么', '怎么', '吗', '呢'}

    keywords = []
    for word in words:
        word = word.strip()
        if len(word) >= 2 and word not in stop_words:
            if word not in keywords:
                keywords.append(word)
                if len(keywords) >= max_keywords:
                    break

    if not keywords:
        return "spec"

    return '_'.join(keywords[:max_keywords])


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


def format_message_content(msg_data: Any) -> str:
    """格式化消息内容（支持 AI Code 格式）"""
    # AI Code 格式：外层 message 对象包含 role 和 content
    if isinstance(msg_data, dict) and 'message' in msg_data:
        msg_data = msg_data.get('message', {})

    # 提取 content
    content = msg_data.get('content', msg_data) if isinstance(msg_data, dict) else msg_data
    if not content:
        return ''
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    parts.append(item.get('text', ''))
                elif item.get('type') == 'tool_use':
                    tool_name = item.get('name', 'unknown')
                    parts.append(f"\n[使用工具: {tool_name}]\n")
            elif isinstance(item, str):
                parts.append(item)
        return ''.join(parts)
    return str(content)


def extract_tool_calls(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """提取所有工具调用（支持 AI Code 格式）"""
    tool_calls = []

    for msg in messages:
        # AI Code 格式：type 在外层
        msg_type = msg.get('type', '')
        if msg_type != 'assistant':
            continue

        # 内层 message 对象
        inner_msg = msg.get('message', {})
        content = inner_msg.get('content', [])
        if not isinstance(content, list):
            continue

        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_use':
                tool_calls.append({
                    'name': item.get('name', 'unknown'),
                    'input': item.get('input', {}),
                    'id': item.get('id', '')
                })

    return tool_calls


def extract_tool_results(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """提取工具返回结果（支持 AI Code 格式）"""
    tool_results = {}

    for msg in messages:
        # AI Code 格式：检查外层 type
        msg_type = msg.get('type', '')
        if msg_type != 'user':
            continue

        # 检查是否有 toolUseResult
        tool_result = msg.get('toolUseResult')
        if tool_result and isinstance(tool_result, dict):
            tool_id = tool_result.get('tool_use_id', '')
            result_content = tool_result.get('content', '')

            # 解析结果内容
            if isinstance(result_content, list):
                text_parts = []
                for part in result_content:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text_parts.append(part.get('text', ''))
                result_content = '\n'.join(text_parts)

            tool_results[tool_id] = result_content

        # 也检查内层 message 中的 content
        inner_msg = msg.get('message', {})
        content = inner_msg.get('content', [])
        if not isinstance(content, list):
            continue

        for item in content:
            if isinstance(item, dict) and item.get('type') == 'tool_result':
                tool_id = item.get('tool_use_id', '')
                result_content = item.get('content', '')

                # 解析结果内容
                if isinstance(result_content, list):
                    text_parts = []
                    for part in result_content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            text_parts.append(part.get('text', ''))
                    result_content = '\n'.join(text_parts)

                tool_results[tool_id] = result_content

    return tool_results


def extract_references(tool_calls: List[Dict], tool_results: Dict) -> Set[str]:
    """提取参考资源（URLs、文件路径等）"""
    references = set()

    # 从工具调用中提取
    for call in tool_calls:
        tool_name = call.get('name', '')
        tool_input = call.get('input', {})

        # WebFetch 工具
        if tool_name == 'WebFetch' or tool_name == 'WebSearch':
            url = tool_input.get('url', '')
            if url:
                references.add(f"🌐 {url}")

        # Read 工具
        elif tool_name == 'Read':
            file_path = tool_input.get('file_path', '')
            if file_path:
                references.add(f"📄 {file_path}")

        # Task 工具（Agent 调用）
        elif tool_name == 'Task':
            agent_type = tool_input.get('subagent_type', '')
            if agent_type:
                references.add(f"🤖 Agent: {agent_type}")

    # 从工具结果中提取 URLs
    for result in tool_results.values():
        if isinstance(result, str):
            # 提取 http/https URLs
            urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', result)
            for url in urls:
                references.add(f"🌐 {url}")

    return references


def parse_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """解析 AI Code 的会话文件（JSONL 格式）"""
    messages = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    # 只保留 user 和 assistant 类型的消息
                    if msg and msg.get('type') in ['user', 'assistant']:
                        messages.append(msg)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
        return []

    return messages


def generate_markdown(messages: List[Dict[str, Any]],
                      tool_calls: List[Dict],
                      references: Set[str],
                      session_id: str) -> str:
    """将消息列表转换为 Markdown 格式（增强版）"""
    if not messages:
        return "# 对话记录\n\n无对话内容。\n"

    lines = []
    lines.append("# AI Code 对话记录\n")
    lines.append(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**会话 ID**: {session_id}\n")

    # 添加参考资源部分
    if references:
        lines.append("\n## 📚 参考资源\n")
        for ref in sorted(references):
            lines.append(f"- {ref}\n")

    # 添加工具使用统计
    if tool_calls:
        lines.append(f"\n**使用工具**: {len(tool_calls)} 次\n")
        tool_counts = {}
        for call in tool_calls:
            name = call.get('name', 'unknown')
            tool_counts[name] = tool_counts.get(name, 0) + 1
        for name, count in sorted(tool_counts.items()):
            lines.append(f"  - {name}: {count} 次\n")

    lines.append("\n---\n")

    # 对话内容
    for idx, msg in enumerate(messages, 1):
        msg_type = msg.get('type', 'unknown')
        text = format_message_content(msg)
        if text.strip() == '':
            continue

        if msg_type == 'user':
            lines.append(f"\n## 👤 用户提问 #{idx}\n")
            lines.append(f"{text}\n")
        elif msg_type == 'assistant':
            lines.append(f"\n## 🤖 AiCode 回答 #{idx}\n")
            lines.append(f"{text}\n")

    lines.append("\n---\n")

    # 附录：详细的工具调用记录
    if tool_calls:
        lines.append("\n## 📋 附录：工具调用详情\n")
        for idx, call in enumerate(tool_calls, 1):
            lines.append(f"\n### 工具 {idx}: {call.get('name', 'unknown')}\n")
            lines.append("```json\n")
            lines.append(json.dumps(call, indent=2, ensure_ascii=False, default=str))
            lines.append("\n```\n")

    lines.append(f"\n---\n")
    lines.append(f"*自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    return '\n'.join(lines)


def save_resources(references: Set[str], output_dir: Path, base_filename: str):
    """保存参考资源列表到单独文件"""
    if not references:
        return

    resources_file = output_dir / f"{base_filename}_resources.txt"

    try:
        with open(resources_file, 'w', encoding='utf-8') as f:
            f.write(f"# 参考资源\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# 对话文件: {base_filename}.md\n\n")

            for ref in sorted(references):
                f.write(f"{ref}\n")

        print(f"Resources saved to: {resources_file}", file=sys.stderr)
    except Exception as e:
        print(f"Error saving resources: {e}", file=sys.stderr)


def save_conversation(transcript_path: str, project_dir: str, session_id: str):
    """保存对话到 Markdown 文件（增强版）"""
    try:
        # 解析会话文件
        messages = parse_transcript(transcript_path)
        if not messages:
            print("No messages to save", file=sys.stderr)
            return

        # 提取工具调用和结果
        tool_calls = extract_tool_calls(messages)
        tool_results = extract_tool_results(messages)
        references = extract_references(tool_calls, tool_results)

        # 提取第一个用户提问作为关键词来源
        first_user_msg = ""
        for msg in messages:
            if msg.get('type') == 'user':
                first_user_msg = format_message_content(msg)
                if first_user_msg:
                    break

        # 提取关键词
        keywords = extract_keywords(first_user_msg)

        # 生成文件名: YYmmddHH_{关键词}
        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
        base_filename = f"AiCode_log_{timestamp}_{keywords}"
        filename = f"{base_filename}.md"

        # 使用环境变量指定的目录，默认 _.zco_hist
        hist_dir = get_hist_dir(project_dir)

        # 生成 Markdown 内容
        markdown_content = generate_markdown(messages, tool_calls, references, session_id)

        # 保存主文件
        output_file = hist_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"Conversation saved to: {output_file}", file=sys.stderr)

        # 保存参考资源列表
        save_resources(references, hist_dir, base_filename)

    except Exception as e:
        print(f"Error saving conversation: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def main():
    """主函数"""
    try:
        # Check if this hook is enabled via environment variable
        if os.environ.get('ZCO_CHAT_SAVE_SPEC') != '1':
            # Silently exit if not enabled
            sys.exit(0)

        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')

        if hook_event == 'Stop':
            transcript_path = input_data.get('transcript_path', '')
            cwd = input_data.get('cwd', '')
            session_id = input_data.get('session_id', 'unknown')

            if transcript_path and cwd:
                save_conversation(transcript_path, cwd, session_id)
            else:
                print(f"Missing required data: transcript_path={transcript_path}, cwd={cwd}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
