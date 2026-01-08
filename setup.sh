#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
X_CUR_DIR=$(realpath ${SCRIPT_DIR})

#ln -s /home/lane/workspace/minieye-services/YJ-ANNO-SG-Y2025/_.ai-claude/link-to-project.py ~/.local/bin/yja-claude
if [[ -L $HOME/.local/bin/yja-claude ]]; then
	rm $HOME/.local/bin/yja-claude
fi
if [[ -f $HOME/.local/bin/yja-claude ]]; then
	rm $HOME/.local/bin/yja-claude
fi

ln -s ${X_CUR_DIR}/zco_claude_init.py $HOME/.local/bin/yja-claude

## 配置 PATH 环境变量
## 判断 是否已经配置过 PATH 环境变量
if [[ $PATH != *$HOME/.local/bin:* ]]; then
	if [[ -f $HOME/.bashrc ]]; then
		echo "export PATH=$HOME/.local/bin:$PATH:$X_CUR_DIR/ClaudeSettings/commands" >>$HOME/.bashrc
	fi
	if [[ -f $HOME/.zshrc ]]; then
		echo "export PATH=$HOME/.local/bin:$PATH:$X_CUR_DIR/ClaudeSettings/commands" >>$HOME/.zshrc
	fi
fi

export PATH=$HOME/.local/bin:$PATH:$X_CUR_DIR/ClaudeSettings/commands
x_version=$(zco-git-tag $X_CUR_DIR)

cat <<EOF
------------------------------------------------
	yja-claude: 佑驾内部对项目目录初始化Claude配置的脚本
	version: ${x_version}
------------------------------------------------

usage: 
	指定项目路径, 初始化项目的 ClaudeSettings 目录

example:
[1] 指定项目路径
$>	yja-claude  <target_project_dir>

[2] cd 到项目目录, 再执行初始化
$>	cd <target_project_dir>
$>	yja-claude .

EOF
