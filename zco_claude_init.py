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
from datetime import datetime
from pathlib import Path

VERSION = "v0.0.4.260114"
ZCO_CLAUDE_ROOT = os.path.dirname(os.path.realpath(__file__))
#ZCO_CLAUDE_TPL_DIR = os.path.join(ZCO_CLAUDE_ROOT, "ClaudeSettings")
ZCO_CLAUDE_TPL_DIR = Path(ZCO_CLAUDE_ROOT) / "ClaudeSettings"



class M_Color:
    """
    颜色打印类
    """
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

def pf_color(msg: str, color_code:str=M_Color.GREEN):
    print(f"{color_code}{msg}{M_Color.RESET}")

def debug(*args):
    """
    调试打印函数

    Args:
        *args: 要打印的内容
    """
    if os.environ.get("DEBUG"):
        print("DEBUG:", *args)

def make_default_config():
    ##; 读取示例配置
    source_dir = os.path.abspath(ZCO_CLAUDE_TPL_DIR)
    default_settings = {
    "env": {
        "ZCO_TPL_VERSION": "v2",
        "YJ_CLAUDE_CHAT_SAVE_SPEC": "0",
        "YJ_CLAUDE_CHAT_SAVE_PLAIN": "0",
        "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "3000"
    },
    "alwaysThinkingEnabled": True,
    "permissions": {
        "deny": [
            "Read(~/.ssh/**)",      ##; 防止 AI 尝试读取你的私钥
            "Read(~/.aws/**)",      ##; 云服务凭证
            "Read(**/Library/Application Support/Google/Chrome/**)",
            "Read(./.DS_Store)",    ##; 
            "Read(**/.DS_Store)",
            "Read(**/__pycache__)",
            "Read(**/__pycache__/**)",
            "Read(*._.*)",
            "Read(*.bak.*)",
            "Read(*.tmp.*)",
            "Read(_.*/**)",
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
            "Write(CLAUDE.md)",
            "Write(_.claude_hist/*)",
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
    "hooks": {
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
            ]
        }
    }
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

def make_symlink(source:Path, target:Path, description: str):
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
    print("")
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
        response = input("    是否删除并重新创建？(y/N): ")
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

    ##; 确保目标目录存在
    target.parent.mkdir(parents=True, exist_ok=True)

    ##; 创建软链接
    try:
        target.symlink_to(source)
        pf_color(f"  ✓ {description}：已创建软链接")
        # print(f"    {target} -> {source}")
        return True
    except Exception as e:
        pf_color(f"  ✗ {description}：创建失败 - {e}", M_Color.RED)
        return False



def make_links_for_subs(source_pdir, target_pdir, description, flag_file=False, flag_dir=True):
    """
    创建软链接到子目录

    Args:
        source: 源目录的绝对路径
        target: 目标目录的绝对路径
        description: 链接描述（用于日志）
        flag_file: 筛选允许创建文件软链接
        flag_dir: 筛选允许创建目录软链接
    """
    ###; 先判断目标目录是否存在
    abs_target = target_pdir.resolve()
    abs_source = source_pdir.resolve()
    n_cnt = 0
    if not target_pdir.exists():
        pf_color(f"  新建 {description}：{abs_target}, 即将对源子目录进行软链接", M_Color.BLUE)
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
        if item.name.startswith("_."):
            pass
        elif item.is_dir() and flag_dir :
            src_path = item.resolve()
            dst_path = abs_target / item.name
            make_symlink(src_path, dst_path, f"{description} - {item.name}")
            n_cnt += 1
        elif item.is_file() and flag_file and not item.name.startswith("_."):
            src_path = item.resolve()
            dst_path = abs_target / item.name
            make_symlink(src_path, dst_path, f"{description} - {item.name}")
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
        old_display = (old_line[:width-3] + '...') if len(old_line) > width else old_line.ljust(width)
        new_display = (new_line[:width-3] + '...') if len(new_line) > width else new_line.ljust(width)

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
    print("  [y] 是，更新配置, 原配置文件将备份为 settings.local.json.{NOW_TAG}")
    print("  [n] 否，保留现有配置 (默认)")
    print("  [m] 合并配置, 但优先使用模板配置, 原配置文件将备份为 settings.local.json")
    print("  [b] 合并配置, 但优先使用原有配置, 原配置文件将备份为 settings.local.json")
    print("  [e] 取消操作, 退出当前进程")
    print("=" * 80)

    while True:
        response = input("\n请选择 (y/n/m/b/e): ").lower().strip()
        if response == '' or response == 'n':
            pf_color("  已取消更新，保留现有配置", M_Color.BLUE)
            return M_ResUpdate.NO
        elif response == 'y':
            pf_color("  确认更新配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.GREEN)
            return M_ResUpdate.YES
        elif response == 'm':
            pf_color(f"  合并两者(Merge),新生成合并后的配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.BLUE)
            return M_ResUpdate.MERGE
        elif response == 'b':
            pf_color(f"  合并两者(Blend),新生成合并后的配置, 原配置文件将备份为 settings.local.{NOW_TAG}.json", M_Color.BLUE)
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
                merged_obj[key].extend(value)
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


def upsert_template_settings(fp_dst_config: Path):
    """
    生成配置文件，如果已存在则先显示 DIFF 并让用户确认, 如果修改则必须备份原配置文件

    Args:
        fp_dst_config: 目标配置文件路径

    Returns:
        bool: 是否成功生成配置
    """
    ##; 生成新配置内容
    default_settings = make_default_config()
    new_content = json.dumps(default_settings, ensure_ascii=False, indent=2)

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
            pf_color("\n📊 配置差异对比:", M_Color.BLUE)
            show_json_diff(old_content, new_content)

            ##; 让用户确认是否更新
            x_ans = confirm_update()
            if x_ans == M_ResUpdate.NO:
                pf_color(f"  ℹ️  已保留现有配置，未做任何更改", M_Color.BLUE)
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


def generate_global_settings(source_dir: Path):
    """
    生成配置文件，如果已存在则先显示 DIFF 并让用户确认

    Args:
        source_dir: 源项目目录（包含 hooks/ 目录）

    Returns:
        bool: 是否成功生成配置
    """

    home_dir = Path.home()
    global_settings = home_dir / ".claude" / "settings.json"
    upsert_template_settings(global_settings)
    pf_color(f"\n  Tips: HOME/.claude/settings.json 优先级较低, 会被项目本地配置覆盖", M_Color.BLUE)
    pf_color(
        f"""\n
        HOME/.claude/settings.json (低) >  
        PROJECT/.claude/settings.json (中) > 
        PROJECT/.claude/settings.local.json (高)
        """, M_Color.BLUE)


def generate_project_settings(target_path: Path):
    """
    为指定项目生成本地配置文件 .claude/settings.local.json

    Args:
        target_path: 目标项目路径
        source_dir: 源项目目录（ClaudeSettings 目录）

    Returns:
        bool: 是否成功生成配置
    """
    ##; 确保目标路径存在
    if not target_path.exists() or not target_path.is_dir():
        pf_color(f"  ✗ 目标路径不存在或不是目录: {target_path}", M_Color.RED)
        return False

    ##; 本地配置文件路径
    local_settings = target_path / ".claude" / "settings.local.json"
    upsert_template_settings(local_settings)
    pf_color(f"\n  Tips: PROJECT/.claude/settings.local.json 优先级最高, 不会影响其他项目配置", M_Color.BLUE)


def record_linked_project(source_dir, target_path):
    """
    记录已链接的项目

    Args:
        source_dir: 源项目目录
        target_path: 目标项目路径
    """
    record_file = source_dir /  "_.linked-projects.json"

    ##; 读取现有记录
    if record_file.exists():
        with open(record_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"linked-projects": []}

    ##; 获取目标路径的绝对路径字符串
    target_str = str(Path(target_path).resolve())

    ##; 检查是否已记录
    existing_projects = {p[0]: p for p in data["linked-projects"]}

    ##; 添加或更新记录
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    existing_projects[target_str] = [target_str, timestamp]

    ##; 更新数据
    data["linked-projects"] = list(existing_projects.values())

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
    m_ignore =  ZCO_CLAUDE_TPL_DIR / "DOT.claudeignore"

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

    ##; 如果文件存在，备份
    if output_file.exists():
        backup_name = f".claudeignore.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup = target_abs / backup_name
        shutil.copy2(output_file, backup)
        print(f"  ✓ 已备份原文件: {backup_name}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))

        print(f"  ✓ 已生成 .claudeignore:")
        print(f"    - 总规则数: {stats['total_unique']} 条（已去重）")
        print(f"    - 来自 .claudeignore: {stats['ary1_contributed']} 条")
        print(f"    - 来自 .gitignore_global: {stats['ary2_contributed']} 条")
        print(f"    - 来自 .gitignore: {stats['ary3_contributed']} 条")
        print(f"    - 文件位置: {output_file}")

        return True
    except Exception as e:
        print(f"  ✗ 写入文件失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Claude Code 配置管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式:

1. 仅生成全局默认配置（不需要参数）:
  %(prog)s

  效果: 生成或更新 $HOME/.claude/settings.json

2. 为指定项目配置 Claude（提供项目路径）:
  %(prog)s /path/to/target/project
  %(prog)s ../another-project

  效果:
    - 生成 <project>/.claude/settings.local.json（项目本地配置）
    - 软链接 ClaudeSettings/rules/* -> .claude/rules/*
    - 软链接 ClaudeSettings/hooks/* -> .claude/hooks/*
    - 软链接 ClaudeSettings/skills/* -> .claude/skills/*
    - 软链接 ClaudeSettings/commands/* -> .claude/commands/*
    - 生成 .claudeignore 文件
    - 注意: 不会重新生成配置

说明:
  - 配置: $HOME/.claude/settings.json (所有项目共享)
  - 项目配置: <project>/.claude/settings.local.json (项目特定)
  - 项目配置可以覆盖配置的特定选项
        """
    )
    parser.add_argument(
        "target_path",
        nargs='?',  ##; 参数可选
        default=None,
        help="目标项目的路径（可选，不提供则仅生成配置）"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {VERSION}"
    )

    args = parser.parse_args()

    ##; 情况 1: 没有提供项目路径，仅生成配置
    if args.target_path is None:
        pf_color("\n📋 模式: 仅生成配置", M_Color.BLUE)
        print(f"配置路径: $HOME/.claude/settings.json\n")

        ##; 生成配置
        print("生成配置...\n")
        success = generate_global_settings(ZCO_CLAUDE_TPL_DIR)

        if success:
            pf_color("\n✅ 完成！配置已生成或更新。", M_Color.GREEN)
        else:
            pf_color("\n⚠️  配置生成失败或被取消。", M_Color.YELLOW)

        return

    ##; 情况 2: 提供了项目路径，配置特定项目
    pf_color("\n📋 模式: 配置指定项目", M_Color.BLUE)

    ##; 验证路径
    target_abs, source_abs = validate_paths(args.target_path, ZCO_CLAUDE_TPL_DIR)

    print(f"\n源项目：{source_abs}")
    print(f"目标项目：{target_abs}")
    print(f"项目配置：{target_abs}/.claude/settings.local.json\n")

    ##; 生成项目本地配置
    print("生成项目本地配置...\n")
    generate_project_settings(target_abs)

    ##; 创建目标 .claude 目录
    target_claude_dir = target_abs / ".claude"
    target_claude_dir.mkdir(exist_ok=True)

    ##; 创建软链接
    print("\n开始链接配置到目标项目...\n")

    results = []

    ##; 2. rules 目录
    source_rules = ZCO_CLAUDE_TPL_DIR /  "rules"
    target_rules = target_claude_dir / "rules"
    results.append(make_links_for_subs(source_rules, target_rules, "rules 目录"))

    ##; 3. hooks 目录
    source_hooks = ZCO_CLAUDE_TPL_DIR /  "hooks"
    target_hooks = target_claude_dir / "hooks"
    results.append(make_links_for_subs(source_hooks, target_hooks, "hooks 目录"))

    ##; 3. skills 目录
    source_skills = ZCO_CLAUDE_TPL_DIR /  "skills"
    target_skills = target_claude_dir / "skills"
    results.append(make_links_for_subs(source_skills, target_skills, "skills 目录"))

    ##; 4. commands 目录
    source_commands = ZCO_CLAUDE_TPL_DIR /  "commands"
    target_commands = target_claude_dir / "commands"
    n_cnt = (make_links_for_subs(source_commands, target_commands,  "commands 目录", flag_dir=True, flag_file=True))

    ##; 4. zco-scripts 目录
    source_commands = ZCO_CLAUDE_TPL_DIR /  "zco-scripts"
    target_commands = target_claude_dir / "zco-scripts"
    make_symlink(source_commands, target_commands,  "zco-scripts 目录")

    results.append(n_cnt)
    results.append(n_cnt)

    pf_color(f"\n✅ 完成！", M_Color.GREEN)
    pf_color(f"  - 已生成项目本地配置")
    pf_color(f"  - 已生成项目本地配置 .claude/settings.local.json ")
    pf_color(f"  - 成功完成对项目的 Claude 配置扩展")
    pf_color(f"    配置扩展源: {target_abs}")
    ##; 生成 .claudeignore
    try:
        init_claudeignore(target_abs)
    except Exception as e:
        print(f"\n✗ 生成 .claudeignore 失败: {e}")
    else:
        pf_color(f"  - 已生成项目本地配置 .claude/.claudeignore ")

    pf_color(
        f"""\n建议: 
        [1] 执行 echo \"**/*.local.*\" >> .gitignore 来忽略本地配置文件
        [1] 请根据实际情况修改 .claude/settings.local.json 中的配置

        欢迎一起构建和维护健康绿色的 ClaudeSettings 模板库！
        """, M_Color.BLUE)
    
    pf_color(f"", M_Color.BLUE)
    ##; 记录链接的项目
    if any(results):
        record_linked_project(source_abs, target_abs)
    

if __name__ == "__main__":
    main()
