#!/usr/bin/env python3
"""
%(prog)s
推荐部署环境:
  - Python 3.11 及以上版本
  - 安装依赖: `pip install -r requirements.txt`    
"""

import os
import sys
import argparse
import json
import shutil
import difflib
import subprocess
import hashlib
from datetime import datetime
from pathlib import Path

VERSION = "0.1.0"

class M_Color:
    """
    颜色打印类, 前景颜色, foreground color
    """
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


class M_ColorBg:
    """
    颜色打印类, 背景颜色, background color
    """
    GREEN = "\033[42m"
    BLUE = "\033[44m"
    RED = "\033[41m"
    YELLOW = "\033[43m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    RESET = "\033[0m"

class M_ColorLevel:
    """
    颜色打印类, 日志级别颜色, log level color
    """
    S_OK = M_Color.GREEN
    S_FAIL = M_Color.MAGENTA
    DEBUG = M_Color.CYAN
    INFO = M_Color.BLUE
    WARN = M_Color.YELLOW
    ERROR = M_Color.RED
    RESET = M_Color.RESET


def pf_color(msg: str, *ms, color_code: str = M_Color.GREEN):
    # 先判断当前是否是在终端环境
    if not sys.stdout.isatty():
        print(msg)
    elif ms:
        print(color_code, msg, M_ColorLevel.DEBUG, *ms, M_Color.RESET)
    else:
        print(color_code, msg, M_Color.RESET)


def debug(*args):
    if os.environ.get("DEBUG"):
        print(*args, M_ColorLevel.DEBUG)


def is_git_repo(path: Path) -> bool:
    """
    检查指定路径是否为 Git 仓库
    """
    git_dir = path / ".git"
    return git_dir.exists() and git_dir.is_dir()


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

def get_git_remote_map(project_dir: Path = None) -> dict:
    """获取当前 Git 仓库的远程 URL"""
    ## git rev-parse --is-inside-work-tree
    ## get remote name 
    if not os.path.isdir(project_dir):
        return None
    result = subprocess.run(
        ['git', '-C', str(project_dir), 'remote', '-v'],
        capture_output=True, text=True, check=True
    )
    lines = result.stdout.strip().splitlines()
    dmap = {}
    for line in lines:
        ps = line.split()
        if len(ps) >= 2:
            dmap[ps[0]] = ps[1]    
    return dmap

    
def get_git_remote_url(project_dir: Path = None, remote_name: str = "origin") -> str:
    """获取当前 Git 仓库的远程 URL"""
    try:
        # 执行 git remote get-url origin 命令
        if project_dir:
            result = subprocess.run(
                ['git', '-C', str(project_dir), 'remote', 'get-url', remote_name],
                capture_output=True, text=True, check=True
            )
        else:
            result = subprocess.run(
                ['git', 'remote', 'get-url', remote_name],
                capture_output=True, text=True, check=True
            )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
def cli_main():
    parser = argparse.ArgumentParser(
        description=f"{M_Color.GREEN} %(prog)s (Version: {VERSION}) {M_Color.RESET}" ,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog= f"{M_Color.CYAN} {__doc__} {M_Color.RESET}"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{VERSION}"
    )
    
    ##################################
    ##; 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    ##; 创建子命令解析器
    parser_show_remote = subparsers.add_parser('show-remote', help='显示 Git 远程仓库 URL')
    parser_show_remote.add_argument(
        'project_path',
        nargs='?',
        default=None,
        help='目标项目路径（可选，默认为当前目录）'
    )
    parser_show_remote.add_argument(
        '--remote-name',
        default='origin',
        help='远程仓库名称（可选，默认为 origin）'
    )

    ##################################
    args = parser.parse_args()
    
    if args.command == 'show-remote':
        project_path = args.project_path
        if project_path is None:
            project_path = get_git_root()
        elif not os.path.exists(project_path):
            pf_color(f"项目路径不存在:", project_path, color_code=M_ColorLevel.S_FAIL)
            return
        remote_url = get_git_remote_url(project_dir=project_path, remote_name=args.remote_name)
        if remote_url:
            pf_color(f"RemoteURL:" , remote_url, color_code=M_ColorLevel.S_OK)
        else:
            pf_color(f"未找到远程仓库:", args.remote_name, color_code=M_ColorLevel.S_FAIL)
        return
    
    
    

if __name__ == "__main__":
    cli_main()
