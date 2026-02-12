#!/usr/bin/env python3
"""
##;调试 Hook - 打印所有接收到的数据
##;用于查看 Hook 事件的完整数据结构
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    try:
        ##;读取 stdin 输入
        input_data = json.load(sys.stdin)

        ##;准备调试输出
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "hook_event_name": input_data.get("hook_event_name"),
            "session_id": input_data.get("session_id"),
            "model": input_data.get("model"),  ##;尝试获取模型名
            "cwd": input_data.get("cwd"),
            "transcript_path": input_data.get("transcript_path"),
            "project_dir": input_data.get("project_dir"),
            "source": input_data.get("source"),
            ##;环境变量
            "env": {
                "ANTHROPIC_MODEL": os.environ.get("ANTHROPIC_MODEL"),
                "ANTHROPIC_DEFAULT_SONNET_MODEL": os.environ.get("ANTHROPIC_DEFAULT_SONNET_MODEL"),
                "ANTHROPIC_DEFAULT_OPUS_MODEL": os.environ.get("ANTHROPIC_DEFAULT_OPUS_MODEL"),
                "ANTHROPIC_DEFAULT_HAIKU_MODEL": os.environ.get("ANTHROPIC_DEFAULT_HAIKU_MODEL"),
                "CLAUDE_CODE_SUBAGENT_MODEL": os.environ.get("CLAUDE_CODE_SUBAGENT_MODEL"),
            },
            ##;完整输入数据（用于查看所有字段）
            "full_input": input_data
        }

        ##;写入调试文件
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True, text=True, check=True
            )
            git_root = Path(result.stdout.strip())
        except:
            git_root = Path.cwd()

        hist_dir = git_root / '_.zco_hist'
        hist_dir.mkdir(exist_ok=True)

        debug_file = hist_dir / f"hook_debug_{input_data.get('hook_event_name', 'unknown')}.json"

        with open(debug_file, 'w', encoding='utf-8') as f:
            json.dump(debug_info, f, indent=2, ensure_ascii=False)

        print(f"Debug info saved to: {debug_file}", file=sys.stderr)
        print(f"Model from input: {input_data.get('model', 'NOT FOUND')}", file=sys.stderr)

        sys.exit(0)

    except Exception as e:
        print(f"Debug hook error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
