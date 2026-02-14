#!/usr/bin/env python3
"""
zco_claude_init.py
作用:
  基于 ClaudeSettings 扩展项目的 .claude 配置目录, 快速初始化项目

步骤：
  0. 为目标项目创建 .claudeignore 文件
  1. 新建一个 $HOME/.claude/settings.json 配置, 有备份
  2. 软链接 .claude/rules/* 目录到目标项目
  3. 软链接 .claude/hooks/* 目录到目标项目
  4. 软链接 .claude/command/*  到目标项目
  5. 如果目标目录已存在, 则提示是否覆盖
  6. 记录已链接的项目到 _.linked-projects.json

Usage:
    ./zco_claude_init.py <target_project_path>

Example:
    ./zco_claude_init.py /path/to/another/project
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

VERSION = "v0.1.6.260305"
ZCO_CLAUDE_ROOT = os.path.dirname(os.path.realpath(__file__))
# ZCO_CLAUDE_TPL_DIR = os.path.join(ZCO_CLAUDE_ROOT, "ClaudeSettings")
ZCO_CLAUDE_TPL_DIR = Path(ZCO_CLAUDE_ROOT) / "ClaudeSettings"
ZCO_CLAUDE_IGNORE_FILE = ZCO_CLAUDE_TPL_DIR / "DOT.claudeignore"
ZCO_CLAUDE_RECORD_FILE = Path.home() / ".claude" / "zco-linked-projects.json"
ZCO_CLAUDE_CONFIG_FILE = Path.home() / ".claude" / "settings.json"

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


def pf_color(msg: str, color_code: str = M_Color.GREEN):
    # 先判断当前是否是在终端环境
    if not sys.stdout.isatty():
        print(msg)
    else:
        print(f"{color_code}{msg}{M_Color.RESET}")


def debug(*args):
    """
    调试打印函数

    Args:
        *args: 要打印的内容
    """
    if os.environ.get("DEBUG"):
        print("DEBUG:", *args)


def make_default_config(tpl_dir: Path = ZCO_CLAUDE_TPL_DIR, with_hooks=False):
    ##; 读取示例配置
    source_dir = os.path.abspath(tpl_dir)
    default_settings = {
        "env": {
            "ZCO_TPL_VERSION": "v3",
            "ZCO_CHAT_SAVE_SPEC": "1",
            "ZCO_CHAT_SAVE_PLAIN": "1",
            "ZCO_AUTO_GIT_COMMIT_MODE": "0",
            "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "5000",
        },
        "alwaysThinkingEnabled": True,
        "permissions": {
            "deny": [
                "Read(~/.ssh/**)",  ##; 防止 AI 尝试读取你的私钥
                "Read(~/.aws/**)",  ##; 云服务凭证
                "Read(**/Library/'Application Support'/Google/Chrome/**)",
                "Read(./.DS_Store)",  ##; 
                "Read(**/.DS_Store)",
                "Read(**/__pycache__)",
                "Read(**/__pycache__/**)",
                "Read(*._.*)",
                "Read(*.bak.*)",
                "Read(*.tmp.*)",
                "Read(*._/**)",
            ],
            "ask": [
                # 需求：读取这些配置文件前必须先询问
                "Read(**/.git/**)",
                "Read(**/app.local.conf)",
                "Read(**/*.local.conf)",
                "Read(**/config.local.yaml)",
                "Read(**/.env*)",      # 捕获 .env, .env.local 等
                "Write(**/*.conf)",    # 写入任何配置文件也要询问
                "Write(**/*.yaml)",
                "Read(**/.zshrc)",
                "Read(**/.bashrc)",
                "Read(**/.bash_profile)",
                "Read(**/*.secret.*)",
                "Write(**/docs/manual/**)"
            ],
            "allow": [
                # "Bash(echo:*)",
                # "Bash(cat:*)",
                # ... 你之前的 allow 配置
                "Read(docs/plans/*)",
                "Write(docs/plans/*)",
                "Read(docs/*)",
                "Read(readme.md)",
                "Read(README.md)",
                "Read(_.zco_hist/*)",
                "Write(CLAUDE.md)",
                "Write(_.zco_hist/*)",
                "Write(/tmp/*)",
                # 注意：不要把上面已经在 ask 里的文件又放进 allow，否则可能直接通过
                "Bash(tree -L 2 -d:*)",
                "Bash(tree:*)",
                "Bash(head:*)",
                "Bash(grep:*)",
                "Bash(xargs cat:*)",
                "Bash(xargs ls:*)",
                "Bash(find:*)",
                "Bash(wc:*)",
                "Read(docs/*)",
                "Bash(ls:*)",
                "Bash(git submodule status:*)",
                "Bash(git status:*)",
                # 允许执行本项目下的自定义命令
                "Bash(./.claude/commands/*)",
                "Bash(./.claude/zco-scripts/*)",
                f"Bash({source_dir}/commands/*)",
                f"Bash({source_dir}/zco-scripts/*)"
            ]
        },
    }
    hooks = {
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {source_dir}/hooks/save_chat_plain.py"
                        },
                        {
                            "type": "command",
                            "command": f"python3 {source_dir}/hooks/save_chat_spec.py"
                        }
                    ]
                }
            ],
            "UserPromptSubmit": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"python3 {source_dir}/hooks/git_auto_commit.py"
                        }
                    ]
                }
            ]
        }
    if with_hooks:
        default_settings["hooks"] = hooks
    return default_settings


def validate_paths(target_path, source_dir):
    """
    验证目标路径和源路径

    Args:
        target_path: 目标项目路径
        source_dir: 源项目目录（ClaudeSettings 目录）

    Returns:
        tuple: (target_abs_path, source_abs_path) 绝对路径

    Raises:
        SystemExit: 如果路径无效
    """
    ##; 转换为绝对路径
    target_abs = Path(target_path).resolve()
    source_abs = Path(source_dir).resolve()

    ##; 检查目标路径是否存在
    if not target_abs.exists():
        print(f"错误：目标路径不存在: {target_abs}")
        sys.exit(1)

    ##; 检查目标路径是否为目录
    if not target_abs.is_dir():
        print(f"错误：目标路径不是目录: {target_abs}")
        sys.exit(1)

    ##; 检查源文件/目录是否存在
    rules_dir = source_abs / "rules"
    hooks_dir = source_abs / "hooks"

    missing = []
    if not rules_dir.exists():
        missing.append(str(rules_dir))
    if not hooks_dir.exists():
        missing.append(str(hooks_dir))

    if missing:
        pf_color(f"警告：以下源文件/目录不存在，将跳过：", M_Color.YELLOW)
        for m in missing:
            pf_color(f"  - {m}", M_Color.YELLOW)

    return target_abs, source_abs


def make_symlink(source: Path, target: Path, description: str, prompt_if_add_link=False):
    """
    创建软链接

    Args:
        source: 源文件/目录的绝对路径
        target: 目标链接的绝对路径
        description: 链接描述（用于日志）

    Returns:
        bool: 是否成功创建链接
    """
    ##; 检查源是否存在
    if not source.exists():
        pf_color(f"  跳过 {description}：源不存在", M_Color.RED)
        return False

    ##; 检查目标是否已存在
    if target.exists() or target.is_symlink():
        ##; 如果已经是正确的软链接，跳过
        if target.is_symlink() and target.resolve() == source.resolve():
            pf_color(f"  ✓ {description}：已存在正确的软链接", M_Color.GREEN)
            return True

        print(f"  ! {description}：目标已存在: {target}")
        response = input("    是否删除并重新创建？(y/N/e/exit/c/copy): ")
        if response.lower() == 'e' or response.lower() == 'exit':
            sys.exit(0)
        if response.lower() != 'y':
            pf_color(f"    跳过 {description}：用户取消", M_Color.YELLOW)
            return False

        ##; 删除现有文件/链接
        if target.is_symlink():
            target.unlink()
        elif target.is_dir():
            import shutil
            shutil.rmtree(target)
        else:
            target.unlink()
    elif prompt_if_add_link:
        src_dest = source.relative_to(ZCO_CLAUDE_TPL_DIR.resolve())
        cwd_link = os.path.relpath(target, os.getcwd())
        response = input(f"    是否创建软连接 {src_dest} --> {cwd_link} {description}？(y/N/e/exit/c/copy): ")
        if response.lower() == 'e' or response.lower() == 'exit':
            sys.exit(0)
        if response.lower() != 'y':
            pf_color(f"    跳过 {description}：用户取消", M_Color.YELLOW)
            return False
    else:
        response = 'y'

    ##; 确保目标目录存在
    target.parent.mkdir(parents=True, exist_ok=True)
    if response.lower() == 'c' or response.lower() == 'copy':
        ##; 复制文件/目录
        if source.is_dir():
            import shutil
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)
        pf_color(f"  ✓ {description}：已复制文件/目录", M_Color.GREEN)
        return True

    ##; 创建软链接
    try:
        target.symlink_to(source)
        pf_color(f"  ✓ {description}：已创建软链接")
        # print(f"    {target} -> {source}")
        return True
    except Exception as e:
        pf_color(f"  ✗ {description}：创建失败 - {e}", M_Color.RED)
        return False


def make_links_for_subs(
        source_pdir,
        target_pdir,
        description,
        flag_file=False,
        flag_dir=True,
        prompt_if_add_link=False):
    """
    创建软链接到子目录

    Args:
        source: 源目录的绝对路径
        target: 目标目录的绝对路径
        description: 链接描述（用于日志）
        flag_file: 筛选允许创建文件软链接
        flag_dir: 筛选允许创建目录软链接
    """
    ##; 先判断目标目录是否存在
    abs_target = target_pdir.resolve()
    abs_source = source_pdir.resolve()
    n_cnt = 0
    if not target_pdir.exists():
        pf_color(f"  新建 {description}：{abs_target}, 即将对源子目录进行软链接", M_Color.CYAN)
        target_pdir.mkdir(parents=True, exist_ok=True)
    elif not target_pdir.is_dir():
        # print(f"  跳过 {description}：目标不是目录: {target_pdir}")
        pf_color(f"  跳过 {description}：目标不是目录: {target_pdir}", M_Color.RED)
        return False
    elif target_pdir.is_symlink() and abs_target == abs_source:
        # print(f"  跳过 {description}：已经全局软连接")
        pf_color(f"  跳过 {description}：已经全局软连接", M_Color.YELLOW)
        return False
    elif abs_target == abs_source:
        # pf_color(f"  跳过 {description}：目标目录与源目录相同", M_Color.YELLOW)
        return False
    for item in source_pdir.iterdir():
        if item.name.startswith("_.") or item.name.startswith(".") or item.name.startswith("__"):
            pass
        elif item.is_dir() and flag_dir:
            src_path = item.resolve()
            dst_path = abs_target / item.name
            make_symlink(src_path, dst_path, f"{description} - {item.name}", prompt_if_add_link)
            n_cnt += 1
        elif item.is_file() and flag_file:
            src_path = item.resolve()
            dst_path = abs_target / item.name
            make_symlink(src_path, dst_path, f"{description} - {item.name}", prompt_if_add_link)
            n_cnt += 1
    return n_cnt


def show_diff_side_by_side(old_content: str, new_content: str, width: int = 80):
    """
    显示左右对比的彩色 DIFF

    Args:
        old_content: 旧配置内容
        new_content: 新配置内容
        width: 每列的宽度
    """
    ##; 分割为行
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()

    ##; 使用 difflib 生成差异
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        lineterm='',
        fromfile='Current Config',
        tofile='New Config'
    )

    ##; 颜色定义
    ADDED = M_Color.GREEN
    REMOVED = M_Color.RED
    CHANGED = M_Color.YELLOW
    RESET = M_Color.RESET
    BLUE = M_Color.BLUE

    print("\n" + "=" * (width * 2 + 5))
    print(f"{BLUE}{'Current Config'.center(width)} | {'New Config'.center(width)}{RESET}")
    print("=" * (width * 2 + 5))

    ##; 简单的并排显示
    max_lines = max(len(old_lines), len(new_lines))

    for i in range(max_lines):
        old_line = old_lines[i] if i < len(old_lines) else ""
        new_line = new_lines[i] if i < len(new_lines) else ""

        ##; 确定颜色
        if old_line != new_line:
            if old_line and not new_line:
                ##; 删除的行
                left_color = REMOVED
                right_color = RESET
            elif not old_line and new_line:
                ##; 新增的行
                left_color = RESET
                right_color = ADDED
            else:
                ##; 修改的行
                left_color = CHANGED
                right_color = CHANGED
        else:
            ##; 相同的行
            left_color = RESET
            right_color = RESET

        ##; 截断或填充到指定宽度
        old_display = (old_line[:width - 3] + '...') if len(old_line) > width else old_line.ljust(width)
        new_display = (new_line[:width - 3] + '...') if len(new_line) > width else new_line.ljust(width)

        print(f"{left_color}{old_display}{RESET} | {right_color}{new_display}{RESET}")

    print("=" * (width * 2 + 5))


def show_json_diff(old_json_str: str, new_json_str: str):
    """
    显示 JSON 配置的差异（更智能的格式）

    Args:
        old_json_str: 旧 JSON 字符串
        new_json_str: 新 JSON 字符串
    """
    try:
        old_obj = json.loads(old_json_str)
        new_obj = json.loads(new_json_str)

        ##; 格式化输出
        old_formatted = json.dumps(old_obj, ensure_ascii=False, indent=2)
        new_formatted = json.dumps(new_obj, ensure_ascii=False, indent=2)

        show_diff_side_by_side(old_formatted, new_formatted, width=70)

    except json.JSONDecodeError as e:
        pf_color(f"  ⚠️  JSON 解析失败: {e}", M_Color.RED)
        pf_color("  将显示文本差异...", M_Color.YELLOW)
        show_diff_side_by_side(old_json_str, new_json_str, width=70)


class M_ResUpdate:
    YES = "y"
    NO = "n"
    MERGE = "m"
    BLEND = "b"
    MERGE_OLD = "f"
    EXIT = "e"


def confirm_update() -> bool:
    """
    让用户确认是否执行更新

    Returns:
        bool: True 表示确认更新，False 表示取消
    """
    print("\n" + "=" * 80)
    pf_color("是否要用新配置覆盖现有配置?", M_Color.YELLOW)
    NOW_TAG = datetime.now().strftime("%y%m%d_%H%M")
    print(f"  [y] 是，更新配置, 原配置文件将备份为 settings.local.json.{NOW_TAG}")
    print("  [n] 否，保留现有配置 (默认)")
    print(f"  [m] 合并配置, 但优先使用模板配置, 原配置文件将备份为 settings.local.json.{NOW_TAG}")
    print(f"  [b] 合并配置, 但优先使用原有配置, 原配置文件将备份为 settings.local.json.{NOW_TAG}")
    print("  [e] 取消操作, 退出当前进程")
    print("=" * 80)

    while True:
        response = input("\n请选择 (y/n/m/b/e): ").lower().strip()
        if response == '' or response == 'n':
            pf_color("  已取消更新，保留现有配置", M_Color.CYAN)
            return M_ResUpdate.NO
        elif response == 'y':
            pf_color("  确认更新配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.GREEN)
            return M_ResUpdate.YES
        elif response == 'm':
            pf_color(f"  合并两者(Merge),新生成合并后的配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.CYAN)
            return M_ResUpdate.MERGE
        elif response == 'b':
            pf_color(f"  合并两者(Blend),新生成合并后的配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.CYAN)
            return M_ResUpdate.BLEND
        elif response == 'e':
            pf_color("  准备取消操作, 退出当前进程", M_Color.RED)
            exit(0)
        else:
            pf_color(f"  无效的选项: {response}，请输入 y/n/m/e", M_Color.RED)


def merge_json(low_obj: dict, high_obj: dict) -> dict:
    """
    合并两个 JSON 对象，保留新对象中的所有字段

    Args:
        low_obj: 低优先级, 一般为旧JSON 对象
        high_obj: 新优先级, 一般为新JSON 对象

    Returns:
        dict: 合并后的 JSON 对象
    """
    merged_obj = low_obj.copy()
    for key, value in high_obj.items():
        if key in merged_obj:
            if isinstance(value, dict) and isinstance(merged_obj[key], dict):
                ##; 递归合并嵌套字典
                merged_obj[key] = merge_json(merged_obj[key], value)
            elif isinstance(value, list) and isinstance(merged_obj[key], list):
                ##; 合并列表，保留新列表中的所有元素
                ##; 对于包含字典的列表，不能使用 set() 去重
                v_ary = []
                for v in merged_obj[key]:
                    if v not in v_ary:
                        v_ary.append(v)
                for v in value:
                    if v not in v_ary:
                        v_ary.append(v)
                merged_obj[key] = v_ary
            else:
                ##; 直接覆盖值
                merged_obj[key] = value
        else:
            ##; 添加新字段
            merged_obj[key] = value
    return merged_obj


def is_json_content_equal(content1: str, content2: str) -> bool:
    """
    比较两个 JSON 内容是否相同（忽略格式差异）

    Args:
        content1: 第一个 JSON 字符串
        content2: 第二个 JSON 字符串

    Returns:
        bool: True 表示内容相同，False 表示不同
    """
    try:
        ##; 解析为 Python 对象
        obj1 = json.loads(content1)
        obj2 = json.loads(content2)

        ##; 比较对象是否相等
        return obj1 == obj2
    except json.JSONDecodeError:
        ##; JSON 解析失败，降级为字符串比较
        return content1.strip() == content2.strip()


def upsert_template_settings(fp_dst_config: Path, default_cfg: dict):
    """
    生成配置文件，如果已存在则先显示 DIFF 并让用户确认, 如果修改则必须备份原配置文件

    Args:
        fp_dst_config: 目标配置文件路径

    Returns:
        bool: 是否成功生成配置
    """
    ##; 生成新配置内容
    new_content = json.dumps(default_cfg, ensure_ascii=False, indent=2)

    ##; 检查现有配置并显示 DIFF
    if fp_dst_config.exists():
        try:
            ##; 读取现有配置
            with open(fp_dst_config, 'r', encoding='utf-8') as f:
                old_content = f.read()

            ##; 检查内容是否相同
            if is_json_content_equal(old_content, new_content):
                pf_color(f"\n✓ 配置内容一致，无需更新: {fp_dst_config}", M_Color.GREEN)
                return True

            ##; 内容不同，显示 DIFF
            pf_color(f"\n⚠️  检测到现有配置: {fp_dst_config}", M_Color.YELLOW)
            pf_color("\n📊 配置差异对比:", M_Color.CYAN)
            show_json_diff(old_content, new_content)

            ##; 让用户确认是否更新
            x_ans = confirm_update()
            if x_ans == M_ResUpdate.NO:
                pf_color(f"  ℹ️  已保留现有配置，未做任何更改", M_Color.CYAN)
                return False
            elif x_ans == M_ResUpdate.MERGE:
                ##; 用户确认后，合并配置
                old_obj = json.loads(old_content)
                new_obj = json.loads(new_content)
                merged_obj = merge_json(old_obj, new_obj)
                new_content = json.dumps(merged_obj, ensure_ascii=False, indent=2)
            elif x_ans == M_ResUpdate.BLEND:
                ##; 用户确认后，合并配置
                old_obj = json.loads(old_content)
                new_obj = json.loads(new_content)
                merged_obj = merge_json(new_obj, old_obj)
                new_content = json.dumps(merged_obj, ensure_ascii=False, indent=2)

            ##; 用户确认后，备份现有配置
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = fp_dst_config.parent / f"settings.json.bak.{timestamp}"
            shutil.copy2(fp_dst_config, backup_file)
            os.chmod(backup_file, 0o444)
            pf_color(f"\n  📦 已备份现有配置到: {backup_file}", M_Color.YELLOW)

        except Exception as e:
            pf_color(f"  ⚠️  读取现有配置失败: {e}", M_Color.RED)
            pf_color(f"  将直接覆盖...", M_Color.YELLOW)

    ##; 确保目标目录存在
    fp_dst_config.parent.mkdir(parents=True, exist_ok=True)

    ##; 写入配置
    try:
        with open(fp_dst_config, 'w', encoding='utf-8') as f:
            f.write(new_content)

        pf_color(f"\n  ✅ 已生成配置: {fp_dst_config}", M_Color.GREEN)
        return True
    except Exception as e:
        pf_color(f"\n  ✗ 写入配置失败: {e}", M_Color.RED)
        return False


def generate_global_settings(tpl_dir=ZCO_CLAUDE_TPL_DIR):
    """
    生成配置文件，如果已存在则先显示 DIFF 并让用户确认

    Args:
        source_dir: 源项目目录（包含 hooks/ 目录）

    Returns:
        bool: 是否成功生成配置
    """

    default_cfg = make_default_config(tpl_dir=tpl_dir, with_hooks=True)
    upsert_template_settings(ZCO_CLAUDE_CONFIG_FILE, default_cfg)
    pf_color(f"\n  Tips: HOME/.claude/settings.json 优先级较低, 会被项目本地配置覆盖", M_Color.CYAN)
    pf_color(
        f"""\n
        HOME/.claude/settings.json (低) >
        PROJECT/.claude/settings.json (中) >
        PROJECT/.claude/settings.local.json (高)

        注意: 如果 hooks 存在多个, 则会合并所有 hooks 配置, 会导致 hooks 重复执行
        """, M_Color.CYAN)


def generate_project_settings(target_path: Path):
    """
    为指定项目生成本地配置文件 .claude/settings.local.json

    Args:
        target_path: 目标项目路径
        source_dir: 源模板配置目录（ClaudeSettings 目录）

    Returns:
        bool: 是否成功生成配置
    """
    ##; 确保目标路径存在
    if not target_path.exists() or not target_path.is_dir():
        pf_color(f"  ✗ 目标路径不存在或不是目录: {target_path}", M_Color.RED)
        return False

    ##; 本地配置文件路径
    local_settings = target_path / ".claude" / "settings.local.json"
    default_cfg = make_default_config(with_hooks=False)
    
    upsert_template_settings(local_settings, default_cfg)
    pf_color(f"\n  Tips: PROJECT/.claude/settings.local.json 优先级最高, 不会影响其他项目配置", M_Color.CYAN)


class RecordItem:
    """
    记录项目链接信息的数据类

    Attributes:
        tpl_src_dir: 模板源目录
        target_path: 目标项目路径
        linked_time: 链接时间
        check_time: 最新检查时间
        check_status: 检查状态 (exist/not-found)
        IsGitRepo: 是否为Git仓库
    """

    def __init__(self, tpl_src_dir, target_path, linked_time,
                 check_time=None, check_status=None, IsGitRepo=None):
        self.tpl_src_dir = tpl_src_dir
        self.target_path = target_path
        self.linked_time = linked_time
        self.check_time = check_time
        self.check_status = check_status
        self.IsGitRepo = IsGitRepo

    def to_dict(self):
        """转换为字典格式，只包含非 None 的字段"""
        result = dict(
            target_path=self.target_path,
            linked_time=self.linked_time,
            zco_hist_home=make_hist_home(self.target_path),
            git_remote_map=get_git_remote_map(self.target_path),
        )
        if not self.linked_time:
            result["linked_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.check_time is not None:
            result["check_time"] = self.check_time
        if self.check_status is not None:
            result["check_status"] = self.check_status
        if self.IsGitRepo is not None:
            result["IsGitRepo"] = self.IsGitRepo
        return result

    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建 RecordItem"""
        return cls(
            tpl_src_dir=data.get("tpl_src_dir", ""),
            target_path=data.get("target_path", ""),
            linked_time=data.get("linked_time", ""),
            check_time=data.get("check_time"),
            check_status=data.get("check_status"),
            IsGitRepo=data.get("IsGitRepo"),
        )

    @classmethod
    def from_tuple(cls, target_path, linked_time, *args):
        """从元组创建 RecordItem（兼容旧格式）"""
        return cls(
            tpl_src_dir="",
            target_path=target_path,
            linked_time=linked_time,
        )

    @classmethod
    def from_any(cls, data):
        """从任意格式创建 RecordItem"""
        if isinstance(data, dict):
            return cls.from_dict(data)
        elif isinstance(data, (list, tuple)):
            return cls.from_tuple(*data)
        else:
            raise ValueError(f"Unknown data type: {type(data)}")


def is_git_repo(path: Path) -> bool:
    """
    检查指定路径是否为 Git 仓库

    Args:
        path: 要检查的路径

    Returns:
        bool: True 如果是 Git 仓库
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
    

def record_linked_project(source_dir, target_path, record_file=ZCO_CLAUDE_RECORD_FILE,
                          record_key="linked-projects", check_time=None, check_status=None):
    """
    记录已链接的项目

    Args:
        source_dir: 源项目目录
        target_path: 目标项目路径
        record_file: 记录文件路径
        record_key: 记录键名
        check_time: 检查时间（可选）
        check_status: 检查状态（可选）
    """
    ##; 读取现有记录
    if record_file.exists():
        try:
            with open(record_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            ##; 文件损坏，重新创建
            data = dict(
                VERSION=VERSION,
                ZCO_CLAUDE_ROOT=str(ZCO_CLAUDE_ROOT),
                ZCO_CLAUDE_TPL_DIR=str(ZCO_CLAUDE_TPL_DIR),
            )
            data[record_key] = []
    else:
        data = dict(
            VERSION=VERSION,
            ZCO_CLAUDE_ROOT=str(ZCO_CLAUDE_ROOT),
            ZCO_CLAUDE_TPL_DIR=str(ZCO_CLAUDE_TPL_DIR),
        )
        data[record_key] = []

    ##; 获取目标路径的绝对路径字符串
    target_str = str(Path(target_path).resolve())
    target_path_obj = Path(target_path)
    if check_status is None:
        check_status = "exist" if target_path_obj.exists() else "not-found"

    ##; 检查是否为 Git 仓库
    is_git = is_git_repo(target_path_obj) if target_path_obj.exists() else None

    ##; 添加或更新记录
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record_items = data.get(record_key, [])

    flag_found = False
    for i, item in enumerate(record_items):
        if isinstance(item, dict) and item.get("target_path") == target_str:
            ##; 更新现有记录
            linked_time = item.get("linked_time", timestamp)
            record_items[i] = {
                "tpl_src_dir": str(source_dir),
                "target_path": target_str,
                "linked_time": linked_time,
                "check_time": check_time if check_time else timestamp,
                "check_status": check_status,
                "IsGitRepo": is_git}
            flag_found = True
            break
        elif isinstance(item, (list, tuple)) and len(item) >= 1 and item[0] == target_str:
            ##; 兼容旧格式，转换为新格式
            record_items[i] = {
                "tpl_src_dir": str(source_dir),
                "target_path": target_str,
                "linked_time": timestamp,
                "check_time": check_time if check_time else timestamp,
                "check_status": check_status,
                "IsGitRepo": is_git}
            flag_found = True
            break

    if not flag_found:
        ##; 添加新记录
        record_items.append({
            "tpl_src_dir": str(source_dir),
            "target_path": target_str,
            "linked_time": timestamp,
            "check_time": check_time if check_time else timestamp,
            "check_status": check_status if check_status else ("exist" if target_path_obj.exists() else "not-found"),
            "IsGitRepo": is_git
        })

    ##; 更新数据
    data[record_key] = record_items

    ##; 确保目录存在
    record_file.parent.mkdir(parents=True, exist_ok=True)

    ##; 写入文件
    with open(record_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n已记录到：{record_file}")


def read_ignore_file(file_path):
    """
    读取 ignore 文件并返回有效规则列表（忽略空行和注释）

    Args:
        file_path: ignore 文件路径（Path 对象）

    Returns:
        list: 有效的 ignore 规则列表
    """
    if not file_path.exists():
        return []

    valid_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.rstrip()
                ##; 跳过空行和注释行
                if line and not line.startswith('#'):
                    valid_lines.append(line)
    except Exception as e:
        print(f"  ! 读取文件失败 {file_path}: {e}")
        return []

    return valid_lines


def merge_unique(ary1, ary2, ary3):
    """
    合并三个数组并去重，保持首次出现的顺序

    Args:
        ary1, ary2, ary3: 要合并的列表

    Returns:
        tuple: (merged_list, stats_dict) 合并后的列表和统计信息
    """
    seen = set()
    merged = []

    stats = {
        'ary1_contributed': 0,
        'ary2_contributed': 0,
        'ary3_contributed': 0,
        'total_unique': 0
    }

    ##; 合并 ary1
    for line in ary1:
        if line not in seen:
            seen.add(line)
            merged.append(line)
            stats['ary1_contributed'] += 1

    ##; 合并 ary2
    for line in ary2:
        if line not in seen:
            seen.add(line)
            merged.append(line)
            stats['ary2_contributed'] += 1

    ##; 合并 ary3
    for line in ary3:
        if line not in seen:
            seen.add(line)
            merged.append(line)
            stats['ary3_contributed'] += 1

    stats['total_unique'] = len(merged)

    return merged, stats


def init_claudeignore(target_path):
    """
    为目标项目创建 .claudeignore 文件

    合并以下文件的内容（去重，保持顺序，忽略空行和注释）：
    1. 目标项目现有的 .claudeignore
    2. $HOME/.gitignore_global
    3. 目标项目的 .gitignore

    Args:
        target_path: 目标项目路径（Path 对象）

    Returns:
        bool: 是否成功创建/更新文件
    """
    target_abs = Path(target_path).resolve()

    print("\n生成 .claudeignore...")

    ##; 1. 读取三个来源
    claudeignore_orig = target_abs / ".claudeignore"
    gitignore_global = Path.home() / ".gitignore_global"
    gitignore_local = target_abs / ".gitignore"
    m_ignore = ZCO_CLAUDE_IGNORE_FILE

    ary1 = read_ignore_file(claudeignore_orig)
    ary2 = read_ignore_file(gitignore_global)
    ary3 = read_ignore_file(gitignore_local)
    ary4 = read_ignore_file(m_ignore)

    print(f"  读取源文件:")
    print(f"    - .claudeignore: {len(ary1)} 条规则")
    print(f"    - $HOME/.gitignore_global: {len(ary2)} 条规则")
    print(f"    - .gitignore: {len(ary3)} 条规则")
    if len(ary2) == 0:
        ary2 = ary4

    ##; 2. 合并去重
    merged, stats = merge_unique(ary1, ary2, ary3)

    if not merged:
        print("  ! 没有找到任何 ignore 规则，跳过生成")
        return False

    ##; 3. 生成新内容
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content_lines = []
    content_lines.append(f"###; update@{timestamp}")
    content_lines.append("")

    if stats['ary1_contributed'] > 0:
        content_lines.append("#######; merged from origin .claudeignore")
        ##; 只输出来自 ary1 的规则
        for line in merged[:stats['ary1_contributed']]:
            content_lines.append(line)
        content_lines.append("")

    ary2_start = stats['ary1_contributed']
    ary2_end = ary2_start + stats['ary2_contributed']
    if stats['ary2_contributed'] > 0:
        content_lines.append("#######; merged from $HOME/.gitignore_global")
        for line in merged[ary2_start:ary2_end]:
            content_lines.append(line)
        content_lines.append("")

    ary3_start = ary2_end
    if stats['ary3_contributed'] > 0:
        content_lines.append("#######; merged from .gitignore")
        for line in merged[ary3_start:]:
            content_lines.append(line)
        content_lines.append("")

    ##; 4. 写入文件
    output_file = target_abs / ".claudeignore"
    output_fn = os.path.relpath(output_file.absolute(), os.getcwd())

    ##; 如果文件存在，备份
    if output_file.exists():
        backup_name = f".claudeignore.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup = target_abs / backup_name
        shutil.copy2(output_file, backup)
        print(f"  ✓ 已备份原文件: {backup_name}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))

        print(f"  ✓ 已生成 .claudeignore: {output_fn}")
        print(f"    - 总规则数: {stats['total_unique']} 条（已去重）")
        print(f"    - 来自 .claudeignore: {stats['ary1_contributed']} 条")
        print(f"    - 来自 .gitignore_global: {stats['ary2_contributed']} 条")
        print(f"    - 来自 .gitignore: {stats['ary3_contributed']} 条")
        print(f"    - 文件位置: {output_file}")

        return True
    except Exception as e:
        print(f"  ✗ 写入文件失败: {e}")
        return False


def is_valid_symlink(link_path: Path, expected_source: Path) -> bool:
    """
    检查软链接是否有效

    Args:
        link_path: 软链接路径
        expected_source: 期望的源路径

    Returns:
        bool: True 表示有效，False 表示无效
    """
    if not link_path.exists():
        return False

    if not link_path.is_symlink():
        return False

    ##; 检查软链接是否指向正确的源
    actual_source = link_path.resolve()
    return actual_source == expected_source.resolve()


def cmd_init_global(tpl_dir=None):
    """
    子命令: init-global - 初始化全局 .claudeignore 文件

    Args:
        tpl_dir: 模板目录路径，默认为 ZCO_CLAUDE_TPL_DIR
    """
    ##; 确定模板目录
    if tpl_dir is None:
        source_abs = ZCO_CLAUDE_TPL_DIR.resolve()
    else:
        source_abs = Path(tpl_dir).resolve()
        if not source_abs.exists():
            pf_color(f"错误：模板目录不存在: {source_abs}", M_Color.RED)
            sys.exit(1)
    ##; 没有子命令: 仅生成全局配置
    pf_color("\n📋 模式: 生成默认的全局配置", M_Color.CYAN)
    pf_color(f"配置路径: $HOME/.claude/settings.json\n", M_Color.CYAN)
    success = generate_global_settings(ZCO_CLAUDE_TPL_DIR)

    if success:
        pf_color("\n✅ 完成！配置已生成或更新。", M_Color.GREEN)
    else:
        pf_color("\n⚠️  配置生成失败或被取消。", M_Color.YELLOW)


def make_hist_dir(project_dir: Path = None, enable_symlink: bool = True) -> Path:
    """获取历史记录目录"""
    hist_dir_name = os.environ.get('ZCO_CHAT_SAVE_DIR', None)
    git_root = get_git_root(project_dir)
    if not hist_dir_name:
        hist_dir = git_root / '_.zco_hist'
    else:
        hist_dir = os.path.abspath(os.path.join(str(git_root), hist_dir_name))
    hist_home = make_hist_home(project_dir)
    if not hist_dir.exists():
        if not enable_symlink:
            hist_dir.mkdir(exist_ok=True)
        else:
            hist_dir.symlink_to(hist_home)
    else:
        if enable_symlink:
            if hist_dir.resolve() != hist_home.resolve():
                ## mv old symlink to old_hist
                hist_dir.rename(hist_dir.with_suffix('.bak'))
                hist_dir.symlink_to(hist_home)
    return hist_dir


def make_hist_home(project_dir: Path = None) -> Path:
    """获取历史记录目录"""
    git_root = get_git_root(project_dir)
    git_root_hash = hashlib.md5(str(git_root).encode()).hexdigest()[:8]
    git_name = git_root.name + '.' + git_root_hash
    base_dir = Path.home() / ".claude" / 'zco_hist' / git_name
    # base_dir.mkdir(exist_ok=True)
    os.makedirs(str(base_dir), exist_ok=True)
    return base_dir


def cmd_init_project(target_path=None, tpl_dir=None, flag_git_root=False):
    """
    子命令: init - 初始化项目的 .claude/ 配置

    Args:
        target_path: 目标项目路径，默认为当前目录
        tpl_dir: 模板目录路径，默认为 ZCO_CLAUDE_TPL_DIR
    """
    ##; 确定目标路径
    if target_path is None:
        target_path = Path(os.getcwd())
    else:
        target_path = Path(target_path)

    if flag_git_root:
        target_path = get_git_root(target_path)
        print(f"Git 根目录: {target_path}")

    ##; 确定模板目录
    if tpl_dir is None:
        source_abs = ZCO_CLAUDE_TPL_DIR.resolve()
    else:
        source_abs = Path(tpl_dir).resolve()
        if not source_abs.exists():
            pf_color(f"错误：模板目录不存在: {source_abs}", M_Color.RED)
            sys.exit(1)

    pf_color("\n📋 模式: 初始化项目", M_Color.CYAN)
    print(f"目标项目：{target_path}")
    print(f"模板目录：{source_abs}")
    print(f"项目配置：{target_path}/.claude/settings.local.json \n")

    ##; 验证目标目录
    if not target_path.exists() or not target_path.is_dir():
        pf_color(f"错误：目标目录无效: {target_path}", M_Color.RED)
        sys.exit(1)

    if not ZCO_CLAUDE_CONFIG_FILE.exists():
        pf_color(f"  ⚠️  全局配置文件不存在: {ZCO_CLAUDE_CONFIG_FILE}", M_Color.YELLOW)
        generate_global_settings(ZCO_CLAUDE_TPL_DIR)
    else:
        pf_color(f"  ✔️  全局配置文件存在: {ZCO_CLAUDE_CONFIG_FILE}", M_Color.GREEN)
        
    ##; 生成项目本地配置
    print("生成项目本地配置...\n")
    generate_project_settings(target_path)

    
    make_hist_dir(target_path)
    ##; 生成项目本地配置
    print("生成 ZCO_HIST 目录...\n")
    
    ##; 创建目标 .claude 目录
    target_claude_dir = target_path / ".claude"
    target_claude_dir.mkdir(exist_ok=True)

    ##; 创建软链接
    print("\n开始链接配置到目标项目...\n")

    results = []

    ##; rules 目录
    source_rules = ZCO_CLAUDE_TPL_DIR / "rules"
    target_rules = target_claude_dir / "rules"
    results.append(make_links_for_subs(source_rules, target_rules, "rules 目录", prompt_if_add_link=True))

    ##; hooks 目录
    source_hooks = ZCO_CLAUDE_TPL_DIR / "hooks"
    target_hooks = target_claude_dir / "hooks"
    results.append(make_links_for_subs(source_hooks, target_hooks, "hooks 目录", flag_dir=True, flag_file=True))

    ##; skills 目录
    source_skills = ZCO_CLAUDE_TPL_DIR / "skills"
    target_skills = target_claude_dir / "skills"
    results.append(make_links_for_subs(source_skills, target_skills, "skills 目录", prompt_if_add_link=False))

    ##; commands 目录
    source_commands = ZCO_CLAUDE_TPL_DIR / "commands"
    target_commands = target_claude_dir / "commands"
    n_cnt = make_links_for_subs(source_commands, target_commands, "commands 目录", flag_dir=True, flag_file=True)

    ##; zco-scripts 目录
    source_scripts = ZCO_CLAUDE_TPL_DIR / "zco-scripts"
    target_scripts = target_claude_dir / "zco-scripts"
    make_symlink(source_scripts, target_scripts, "zco-scripts 目录")

    results.append(n_cnt)

    pf_color(f"\n✅ 完成！", M_Color.GREEN)
    pf_color(f"  - 已生成项目本地配置")
    pf_color(f"  - 已生成项目本地配置 .claude/settings.local.json ")
    pf_color(f"  - 成功完成对项目的 Claude 配置扩展")
    pf_color(f"    配置扩展源: {target_path}")

    ##; 生成 .claudeignore
    try:
        init_claudeignore(target_path)
    except Exception as e:
        print(f"\n✗ 生成 .claudeignore 失败: {e}")
    else:
        pf_color(f"  - 已生成项目本地配置  ")

    pf_color(
        f"""\n建议:
        [1] 执行 echo \"**/*.local.*\" >> .gitignore 来忽略本地配置文件
        [1] 请根据实际情况修改 .claude/settings.local.json 中的配置

        欢迎一起构建和维护健康绿色的 ClaudeSettings 模板库！
        """, M_Color.CYAN)

    ##; 记录链接的项目
    if any(results):
        record_linked_project(source_abs, target_path)


def cmd_list_linked_repos(record_file=None):
    """
    子命令: list-linked-repos - 列出所有已链接的项目

    Args:
        record_file: 记录文件路径，默认为 ZCO_CLAUDE_RECORD_FILE
    """
    ##; 确定记录文件路径
    if record_file is None:
        record_file = ZCO_CLAUDE_RECORD_FILE
    else:
        record_file = Path(record_file)

    pf_color("\n📋 已链接项目列表\n", M_Color.CYAN)
    pf_color(f"记录文件： {record_file}\n", M_Color.GREEN)

    ##; 读取记录文件
    if not record_file.exists():
        print("无已链接项目")
        return

    try:
        with open(record_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        pf_color(f"错误：无法解析记录文件 - {e}", M_Color.RED)
        return
    except Exception as e:
        pf_color(f"错误：读取记录文件失败 - {e}", M_Color.RED)
        return

    record_key = "linked-projects"
    record_items = data.get(record_key, [])

    if not record_items:
        print("无已链接项目")
        return

    ##; 格式化输出
    pf_color(f"{'链接时间':<22} {'项目路径'}", M_Color.CYAN)
    pf_color("-" * 80, M_Color.CYAN)

    for i, item in enumerate(record_items):
        if isinstance(item, dict):
            linked_time = item.get("linked_time", "未知")
            target_path = item.get("target_path", "未知")
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            ##; 兼容旧格式 (target_path, linked_time, ...)
            target_path = item[0]
            linked_time = item[1]
        else:
            continue

        pf_color(f"[{i:03d}] [{linked_time}] {target_path}", M_Color.CYAN)

    pf_color(f"\n总计: {len(record_items)} 个项目")


def cmd_fix_linked_repos(record_file=None, remove_not_found=False):
    """
    子命令: fix-linked-repos - 修复已链接项目的软链接

    Args:
        record_file: 记录文件路径，默认为 ZCO_CLAUDE_RECORD_FILE
        remove_not_found: 是否删除不存在的项目记录
    """
    ##; 确定记录文件路径
    if record_file is None:
        record_file = ZCO_CLAUDE_RECORD_FILE
    else:
        record_file = Path(record_file)

    pf_color("\n🔧 修复已链接项目的软链接\n", M_Color.CYAN)
    print(f"记录文件：{record_file}\n")

    ##; 读取记录文件
    if not record_file.exists():
        print("无已链接项目")
        return
    
    ##; 备份记录文件
    backup_file = record_file.with_suffix(record_file.suffix + ".bak")
    shutil.copy(record_file, backup_file)
    pf_color(f"已备份记录文件到: {backup_file}", M_Color.YELLOW)

    try:
        with open(record_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        pf_color(f"错误：无法解析记录文件 - {e}", M_Color.RED)
        return
    except Exception as e:
        pf_color(f"错误：读取记录文件失败 - {e}", M_Color.RED)
        return

    record_key = "linked-projects"
    record_items = data.get(record_key, [])

    if not record_items:
        print("无已链接项目")
        return

    source_abs = ZCO_CLAUDE_TPL_DIR.resolve()
    total_checked = 0
    cnt_link_fixed = 0
    cnt_link_valid = 0
    cnt_link_removed = 0
    cnt_file_copied = 0
    total_projects = 0
    cnt_prj_removed = 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ##; 需要检查的子目录
    subdirs = ['rules', 'hooks', 'skills', 'commands']

    ##; 创建新的记录列表（用于过滤已删除的项目）
    new_record_items = []

    for item in record_items:
        ##; 解析记录项
        record_item = RecordItem.from_any(item)
        target_path = Path(record_item.target_path)

        ##; 检查项目是否存在
        if not target_path.exists():
            check_status = "not-found"
            is_git = None

            if remove_not_found:
                pf_color(f"⚠️  项目不存在，已从记录中移除: {target_path}", M_Color.YELLOW)
                cnt_prj_removed += 1
                continue  ##; 跳过添加到新列表
            else:
                pf_color(f"⚠️  项目不存在: {target_path}", M_Color.YELLOW)
                ##; 更新记录字段
                record_item.check_time = timestamp
                record_item.check_status = check_status
                record_item.IsGitRepo = is_git
                new_record_items.append(record_item.to_dict())
                continue

        ##; 项目存在，进行修复检查
        total_projects += 1
        check_status = "exist"
        is_git = is_git_repo(target_path)
        print(f"\n检查项目: {target_path} (Git: {is_git})")

        target_claude_dir = target_path / ".claude"
        if not target_claude_dir.exists():
            pf_color(f"  跳过: .claude 目录不存在", M_Color.YELLOW)
            ##; 仍然更新记录字段
            record_item.check_time = timestamp
            record_item.check_status = check_status
            record_item.IsGitRepo = is_git
            new_record_items.append(record_item.to_dict())
            continue

        project_checked = 0
        project_fixed = 0
        project_valid = 0

        ##; 检查每个子目录的软链接
        for subdir in subdirs:
            source_subdir = source_abs / subdir
            target_subdir = target_claude_dir / subdir

            if not target_subdir.exists():
                continue

            if not source_subdir.exists():
                pf_color(f"  跳过 {subdir}: 源目录不存在", M_Color.YELLOW)
                continue

            for item_path in target_subdir.iterdir():
                project_checked += 1
                total_checked += 1

                ##; 确定期望的源路径
                source_item = source_subdir / item_path.name
                if not item_path.is_symlink():
                    cnt_file_copied += 1
                    if item_path.exists():
                        pf_color(f"  ¶ {subdir}/{item_path.name} → 不是软链接，且存在, 自行跳过", M_Color.GREEN)
                        continue
                    elif not source_item.exists():
                        pf_color(f"  x {subdir}/{item_path.name} → 不是软链接，且不存在同名的配置模板", M_Color.RED)
                        continue
                    elif source_item.exists():
                        pf_color(f"  ∆ {subdir}/{item_path.name} → 不是软链接，且存在同名的配置模板, 可能存在自定义配置, 请自行检查", M_Color.CYAN)
                        continue
                elif is_valid_symlink(item_path, source_item):
                    project_valid += 1
                    cnt_link_valid += 1
                    print(f"  ✓ {subdir}/{item_path.name} →  模板链接有效")
                else:
                    ##; 删除失效链接
                    try:
                        if item_path.is_symlink() or item_path.exists():
                            item_path.unlink()

                        ##; 重新创建
                        if source_item.exists():
                            item_path.symlink_to(source_item)
                            project_fixed += 1
                            cnt_link_fixed += 1
                            pf_color(f"  † {subdir}/{item_path.name} → 失效，已修复", M_Color.YELLOW)
                        else:
                            pf_color(f"  ✗ {subdir}/{item_path.name} → 失效，源不存在, 现移除", M_Color.RED)
                            os.remove(item_path)
                            cnt_link_removed += 1
                    except Exception as e:
                        pf_color(f"  ✗ {subdir}/{item_path.name} → 修复失败: {e}", M_Color.RED)

        ##; 显示项目修复摘要
        if project_checked > 0:
            if project_fixed == 0:
                print(f"  ✓ 所有软链接有效 ({project_valid}/{project_checked})")
            else:
                print(f"  修复: {project_fixed}, 有效: {project_valid}, 总计: {project_checked}")

        ##; 更新记录字段
        record_item.check_time = timestamp
        record_item.check_status = check_status
        record_item.IsGitRepo = is_git
        new_record_items.append(record_item.to_dict())

    ##; 更新记录文件
    data[record_key] = new_record_items
    data.update(
        VERSION=VERSION,
        ZCO_CLAUDE_ROOT=str(ZCO_CLAUDE_ROOT),
        ZCO_CLAUDE_TPL_DIR=str(ZCO_CLAUDE_TPL_DIR),
    )
    
    try:
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n{M_Color.GREEN}✓ 记录文件已更新{M_Color.RESET}")
    except Exception as e:
        pf_color(f"\n⚠️  更新记录文件失败: {e}", M_Color.YELLOW)

    ##; 显示总体摘要
    print(f"\n{'='*60}")
    pf_color("修复完成：", M_Color.GREEN)
    print(f"  - 项目个数: {total_projects}")
    print(f"  - 配置总项数: {total_checked}")
    print(f"    - 自定义配置: {cnt_file_copied}")
    print(f"    - 有效软链接: {cnt_link_valid}")
    print(f"    - 修复软链接: {cnt_link_fixed}")
    print(f"    - 移除不存在项目: {cnt_link_removed}")
    if remove_not_found:
        print(f"  - 移除不存在项目: {cnt_prj_removed}")


def cmd_fix(project_path=None, tpl_dir=None, record_file=None):
    """
    子命令: fix - 修复指定项目的软链接并更新记录

    Args:
        project_path: 目标项目路径，默认为当前目录
        tpl_dir: 模板目录路径，默认为 ZCO_CLAUDE_TPL_DIR
        record_file: 记录文件路径，默认为 ZCO_CLAUDE_RECORD_FILE
    """
    ##; 确定目标路径
    if project_path is None:
        target_path = Path(os.getcwd())
    else:
        target_path = Path(project_path)

    ##; 确定模板目录
    if tpl_dir is None:
        source_abs = ZCO_CLAUDE_TPL_DIR.resolve()
    else:
        source_abs = Path(tpl_dir).resolve()
        if not source_abs.exists():
            pf_color(f"错误：模板目录不存在: {source_abs}", M_Color.RED)
            sys.exit(1)

    ##; 确定记录文件
    if record_file is None:
        record_file = ZCO_CLAUDE_RECORD_FILE
    else:
        record_file = Path(record_file)

    pf_color("\n🔧 修复项目软链接\n", M_Color.CYAN)
    print(f"目标项目：{target_path}")
    print(f"模板目录：{source_abs}\n")

    ##; 检查项目是否存在
    if not target_path.exists():
        pf_color(f"错误：项目不存在: {target_path}", M_Color.RED)
        ##; 仍然更新记录
        record_linked_project(source_abs, target_path, record_file=record_file,
                              check_status="not-found")
        return

    ##; 检查是否为 Git 仓库
    is_git = is_git_repo(target_path)

    target_claude_dir = target_path / ".claude"
    if not target_claude_dir.exists():
        pf_color(f"警告：.claude 目录不存在，创建中...", M_Color.YELLOW)
        target_claude_dir.mkdir(parents=True, exist_ok=True)

    ##; 需要检查的子目录
    subdirs = ['rules', 'hooks', 'skills', 'commands']
    total_checked = 0
    total_fixed = 0
    total_valid = 0

    print("开始检查和修复软链接...\n")

    for subdir in subdirs:
        source_subdir = source_abs / subdir
        target_subdir = target_claude_dir / subdir

        if not source_subdir.exists():
            pf_color(f"  跳过 {subdir}: 源目录不存在", M_Color.YELLOW)
            continue

        ##; 确保目标子目录存在
        if not target_subdir.exists():
            target_subdir.mkdir(parents=True, exist_ok=True)

        for item in source_subdir.iterdir():
            if item.name.startswith("_."):
                continue

            target_item = target_subdir / item.name
            total_checked += 1

            if is_valid_symlink(target_item, item):
                total_valid += 1
                print(f"  ✓ {subdir}/{item.name} → 有效")
            else:
                ##; 删除失效链接或文件
                try:
                    if target_item.exists() or target_item.is_symlink():
                        target_item.unlink()
                    ##; 重新创建
                    target_item.symlink_to(item)
                    total_fixed += 1
                    pf_color(f"  † {subdir}/{item.name} → 已修复", M_Color.YELLOW)
                except Exception as e:
                    pf_color(f"  ✗ {subdir}/{item.name} → 修复失败: {e}", M_Color.RED)

    ##; 处理 zco-scripts 目录
    source_scripts = source_abs / "zco-scripts"
    target_scripts = target_claude_dir / "zco-scripts"
    if source_scripts.exists():
        if is_valid_symlink(target_scripts, source_scripts):
            print(f"  ✓ zco-scripts → 有效")
        else:
            try:
                if target_scripts.exists() or target_scripts.is_symlink():
                    target_scripts.unlink()
                target_scripts.symlink_to(source_scripts)
                pf_color(f"  † zco-scripts → 已修复", M_Color.YELLOW)
            except Exception as e:
                pf_color(f"  ✗ zco-scripts → 修复失败: {e}", M_Color.RED)

    ##; 更新记录
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record_linked_project(source_abs, target_path, record_file=record_file,
                          check_time=timestamp, check_status="exist")

    ##; 显示摘要
    print(f"\n{'='*60}")
    pf_color("修复完成：", M_Color.GREEN)
    print(f"  - 检查软链接数: {total_checked}")
    print(f"  - 有效软链接: {total_valid}")
    print(f"  - 修复软链接: {total_fixed}")
    print(f"  - Git 仓库: {is_git}")
    print(f"  - 记录已更新")


def main():
    """主函数"""
    ##; 向后兼容：检查第一个参数是否是子命令或路径
    import sys
    argv = sys.argv[1:]

    ##; 定义有效的子命令
    valid_commands = {'init', 'list-linked-repos', 'fix-linked-repos', 'fix'}

    ##; 处理帮助请求（在手动检查之前）
    if '--help' in argv or '-h' in argv:
        ##; 如果有子命令的帮助请求，让 argparse 处理
        ##; 如果只是 --help / -h，显示主帮助
        if not argv or (len(argv) == 1 and argv[0] in ('--help', '-h')):
            pass  ##; 继续执行到 parser.print_help()
        ##; 否则让 argparse 正常处理子命令帮助
    elif not argv:
        cmd_init_global(tpl_dir=ZCO_CLAUDE_TPL_DIR)
        sys.exit(0)
    elif argv[0] not in valid_commands:
        pf_color(f"错误：无效命令: {argv[0]}, 请输入有效命令", M_Color.RED)
        pf_color(f"提示：参考命令: {valid_commands}", M_Color.YELLOW)
        pf_color(f"更多帮助: {sys.argv[0]} --help", M_Color.GREEN)
        sys.exit(0)

    ##; 创建主解析器
    parser = argparse.ArgumentParser(
        description=f"Claude Code 配置管理工具 (Version: {VERSION})" ,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
常用使用示例:
1. 初始化全局配置:
   %(prog)s init

2. 初始化当前项目:
   %(prog)s init . [--tpl TPL_DIR] [--git-root]

3. 列出已链接项目:
   %(prog)s list-linked-repos [--record-file RECORD_FILE]

4. 修复已链接项目的软链接:
   %(prog)s fix-linked-repos [--record-file RECORD_FILE]

5. 修复项目配置:
   %(prog)s fix /path/to/target/project [--tpl TPL_DIR]

说明:
  - init . : 在当前目录初始化 .claude/ 配置
  - list-linked-repos: 显示所有已初始化的项目列表
  - fix-linked-repos: 检查并修复所有软链接
  - 当前版本: %(prog)s {VERSION}
  - 默认模板(TPL_DIR): {ZCO_CLAUDE_TPL_DIR}
  - 默认汇总(RECORD_FILE): {ZCO_CLAUDE_RECORD_FILE}
  - 更多帮助请参考: %(prog)s <command> --help
    eg: %(prog)s init --help
        """
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{VERSION}"
    )

    ##; 创建子命令解析器
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    ##; 子命令: init
    parser_init = subparsers.add_parser(
        'init',
        help='初始化项目的 .claude/ 配置',
        description='创建 .claude/ 目录和软链接'
    )
    parser_init.add_argument(
        'project_path',
        nargs='?',
        default=None,
        help='目标项目路径（可选）, 如果为空则初始化全局的 $HOME/.claude/settings.json, 支持相对路径'
    )
    parser_init.add_argument(
        '--tpl',
        default=None,
        help=f"模板目录路径（可选，默认为 ${ZCO_CLAUDE_TPL_DIR}）"
    )
    parser_init.add_argument(
        '--git-root',
        action='store_true',
        default=False,
        help='如果设置，将在 Git 仓库根目录初始化配置'
    )

    ##; 子命令: list-linked-repos
    parser_list = subparsers.add_parser(
        'list-linked-repos',
        help='列出所有已链接的项目',
        description='读取记录文件并显示所有已初始化项目'
    )
    parser_list.add_argument(
        '--record-file',
        default=None,
        help='记录文件路径（可选，默认为 ~/.claude/zco-linked-projects.json）'
    )

    ##; 子命令: fix-linked-repos
    parser_fix_repos = subparsers.add_parser(
        'fix-linked-repos',
        help='修复已链接项目的软链接',
        description='检查所有已链接项目的软链接，删除失效链接并重新创建'
    )
    parser_fix_repos.add_argument(
        '--record-file',
        default=None,
        help='记录文件路径（可选，默认为 ~/.claude/zco-linked-projects.json）'
    )
    parser_fix_repos.add_argument(
        '--remove-not-found',
        action='store_true',
        default=False,
        help='删除不存在的项目记录'
    )

    ##; 子命令: fix - 修复单个项目的软链接
    parser_fix = subparsers.add_parser(
        'fix',
        help='修复指定项目的软链接',
        description='修复指定项目的软链接并更新记录'
    )
    parser_fix.add_argument(
        'project_path',
        nargs='?',
        default=None,
        help='目标项目路径（可选，默认为当前目录）'
    )
    parser_fix.add_argument(
        '--tpl',
        default=None,
        help='模板目录路径（可选，默认为 ClaudeSettings）'
    )
    parser_fix.add_argument(
        '--record-file',
        default=None,
        help='记录文件路径（可选，默认为 ~/.claude/zco-linked-projects.json）'
    )

    ##; 解析参数
    args = parser.parse_args()

    ##; 处理子命令
    if args.command == 'init':
        if args.project_path is None:
            cmd_init_global(tpl_dir=args.tpl)
        else:
            cmd_init_project(target_path=args.project_path, tpl_dir=args.tpl, flag_git_root=args.git_root)
        return

    elif args.command == 'list-linked-repos':
        cmd_list_linked_repos(record_file=args.record_file)
        return

    elif args.command == 'fix-linked-repos':
        cmd_fix_linked_repos(record_file=args.record_file, remove_not_found=args.remove_not_found)
        return

    elif args.command == 'fix':
        cmd_fix(project_path=args.project_path, tpl_dir=args.tpl, record_file=args.record_file)
        return
    else:
        # print help
        parser.print_help()


if __name__ == "__main__":
    main()
