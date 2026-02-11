#!/usr/bin/env python3
"""
AI Code 对话保存脚本（简单版）
直接从 transcript 提取纯文本，保留 AiCode 的原始输出格式

Environment Variables:
- ZCO_CHAT_SAVE_PLAIN: Must be "1" to enable this hook
- ZCO_CHAT_SAVE_DIR: Output directory (default: _.zco_hist)
"""
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path


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


def extract_text_from_message(msg: dict) -> str:
    """从消息中提取纯文本"""
    msg_type = msg.get('type', '')
    if msg_type not in ['user', 'assistant']:
        return ''

    inner_msg = msg.get('message', {})
    content = inner_msg.get('content', '')

    # 用户消息通常是字符串
    if isinstance(content, str):
        return content

    # Assistant 消息是列表
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
        return '\n'.join(text_parts)

    return ''


def save_simple_conversation(transcript_path: str, project_dir: str, session_id: str):
    """保存对话为简单的纯文本格式"""
    try:
        # 解析 transcript
        messages = []
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                    if msg.get('type') in ['user', 'assistant']:
                        messages.append(msg)
                except BaseException:
                    continue

        if not messages:
            print("No messages to save", file=sys.stderr)
            return

        # 生成文件名
        timestamp = datetime.now().strftime('%y%m%d_%H%M%S')
        filename = f"log_{timestamp}_plain.md"
        hist_dir = get_hist_dir(project_dir)
        output_file = hist_dir / filename

        # 生成简单的 Markdown
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# AI Code Conversation\n\n")
            f.write(f"**Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Session ID**: {session_id}\n\n")
            f.write("---\n\n")

            for msg in messages:
                msg_type = msg.get('type', '')
                text = extract_text_from_message(msg)

                if not text.strip():
                    continue

                if msg_type == 'user':
                    f.write(f"**User**:\n{text}\n\n")
                elif msg_type == 'assistant':
                    f.write(f"**AiCode**:\n{text}\n\n")

            f.write(f"\n---\n*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        print(f"Simple conversation saved to: {output_file}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)


def main():
    try:
        # Check if this hook is enabled via environment variable
        if os.environ.get('ZCO_CHAT_SAVE_PLAIN') != '1':
            # Silently exit if not enabled
            sys.exit(0)

        input_data = json.load(sys.stdin)
        hook_event = input_data.get('hook_event_name', '')

        if hook_event == 'Stop':
            transcript_path = input_data.get('transcript_path', '')
            cwd = input_data.get('cwd', '')
            session_id = input_data.get('session_id', '{session_id}')

            if transcript_path and cwd:
                save_simple_conversation(transcript_path, cwd, session_id)

        sys.exit(0)
    except Exception as e:
        print(f"Hook error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
