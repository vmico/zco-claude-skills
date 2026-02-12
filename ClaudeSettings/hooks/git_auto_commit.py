#!/usr/bin/env python3
"""
##; Git Auto Commit Hook for UserPromptSubmit
##;
##; 功能: 在用户提交消息时，自动检查并提交工作区的代码变更
##; 触发: UserPromptSubmit - 每次用户发送消息时
##;
##; 环境变量:
##;   ZCO_AUTO_GIT_COMMIT_MODE=0   禁用自动提交(默认)
##;   ZCO_AUTO_GIT_COMMIT_MODE=1   只提交 staged 改动
##;   ZCO_AUTO_GIT_COMMIT_MODE=2   增量提交 unstaged 改动 (推荐)
##;   ZCO_AUTO_GIT_COMMIT_MODE=3   增量提交 untracked 文件
##;
##; 提交消息:
##;   staged    → "tm: auto commit staged"
##;   unstaged  → "tm: auto commit unstaged"
##;   untracked → "tm: auto commit untracked"
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_git_command(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """##; 执行 git 命令并返回结果"""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def has_staged_changes(cwd: str) -> bool:
    """##; 检查是否有已暂存(staged)的改动"""
    returncode, _, _ = run_git_command(["git", "diff", "--cached", "--quiet"], cwd)
    return returncode != 0


def has_unstaged_changes(cwd: str) -> bool:
    """##; 检查是否有未暂存(unstaged)的改动"""
    returncode, _, _ = run_git_command(["git", "diff", "--quiet"], cwd)
    return returncode != 0


def has_untracked_files(cwd: str) -> bool:
    """##; 检查是否有未追踪(untracked)的文件"""
    returncode, stdout, _ = run_git_command(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd
    )
    return returncode == 0 and stdout.strip() != ""


def git_commit(cwd: str, message: str) -> bool:
    """##; 执行 git commit"""
    returncode, _, stderr = run_git_command(
        ["git", "commit", "-m", message],
        cwd
    )
    if returncode != 0:
        print(f"##; 提交失败: {stderr}", file=sys.stderr)
        return False
    return True


def git_add(cwd: str, files: str = ".") -> bool:
    """##; 执行 git add"""
    returncode, _, stderr = run_git_command(["git", "add", files], cwd)
    if returncode != 0:
        print(f"##; git add 失败: {stderr}", file=sys.stderr)
        return False
    return True


def git_add_updated(cwd: str) -> bool:
    """##; 执行 git add -u (只添加已追踪的修改文件)"""
    returncode, _, stderr = run_git_command(["git", "add", "-u"], cwd)
    if returncode != 0:
        print(f"##; git add -u 失败: {stderr}", file=sys.stderr)
        return False
    return True


def is_git_repository(cwd: str) -> bool:
    """##; 检查当前目录是否是 git 仓库"""
    returncode, _, _ = run_git_command(
        ["git", "rev-parse", "--git-dir"],
        cwd
    )
    return returncode == 0


def auto_commit(cwd: str) -> list[str]:
    """
    ##; 自动提交工作区变更
    ##; 返回提交的 commit message 列表
    """
    committed_messages = []

    ##; 1. 检查是否有已暂存(staged)的改动
    if has_staged_changes(cwd):
        print("##; 检测到已暂存(staged)的代码，正在自动创建备份提交...", file=sys.stderr)
        if git_commit(cwd, "tm: auto commit staged"):
            committed_messages.append("staged")

    ##; 2. 检查是否有未暂存(unstaged)的改动
    ##; 只针对 Git 已经追踪的文件，全新的 Untracked 文件不会被处理
    if has_unstaged_changes(cwd):
        print("##; 检测到未暂存(unstaged)的改动，正在自动添加并备份...", file=sys.stderr)
        if git_add_updated(cwd):
            if git_commit(cwd, "tm: auto commit unstaged"):
                committed_messages.append("unstaged")

    ##; 3. 处理完全未追踪(Untracked)的文件
    if has_untracked_files(cwd):
        print("##; 检测到新的未追踪文件，正在自动添加并备份...", file=sys.stderr)
        if git_add(cwd, "."):
            if git_commit(cwd, "tm: auto commit untracked"):
                committed_messages.append("untracked")

    return committed_messages


def main():
    """##; Hook 主入口"""
    ##; 读取环境变量
    mode_str = os.environ.get("ZCO_AUTO_GIT_COMMIT_MODE", "0")
    try:
        mode = int(mode_str)
    except ValueError:
        print(f"##; 无效的 ZCO_AUTO_GIT_COMMIT_MODE 值: {mode_str}，默认禁用", file=sys.stderr)
        mode = 0

    ##; mode=0 或未设置时禁用
    if mode == 0:
        sys.exit(0)

    ##; 读取 stdin 输入的 Hook 事件数据
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"##; 解析输入数据失败: {e}", file=sys.stderr)
        sys.exit(0)

    ##; 获取当前工作目录
    cwd = input_data.get("cwd", ".")

    ##; 检查是否是 git 仓库
    if not is_git_repository(cwd):
        print("##; 当前目录不是 git 仓库，跳过自动提交", file=sys.stderr)
        sys.exit(0)

    ##; 根据模式执行对应的提交
    committed_messages = []

    if mode >= 1 and has_staged_changes(cwd):
        ##; 模式 1: 只提交 staged
        print("##; [mode=1] 检测到已暂存(staged)的代码，正在自动创建备份提交...", file=sys.stderr)
        if git_commit(cwd, "tm: auto commit staged"):
            committed_messages.append("staged")

    elif mode >= 2 and has_unstaged_changes(cwd):
        ##; 模式 2: 增量提交 unstaged
        print("##; [mode=2] 检测到未暂存(unstaged)的改动，正在自动添加并备份...", file=sys.stderr)
        if git_add_updated(cwd):
            if git_commit(cwd, "tm: auto commit unstaged"):
                committed_messages.append("unstaged")

    elif mode >= 3 and has_untracked_files(cwd):
        ##; 模式 3: 增量提交 untracked
        print("##; [mode=3] 检测到新的未追踪文件，正在自动添加并备份...", file=sys.stderr)
        if git_add(cwd, "."):
            if git_commit(cwd, "tm: auto commit untracked"):
                committed_messages.append("untracked")

    if committed_messages:
        print(f"##; 自动提交完成: {', '.join(committed_messages)}", file=sys.stderr)
    else:
        print("##; 没有需要提交的变更", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
