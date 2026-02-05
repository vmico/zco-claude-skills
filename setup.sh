#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# M_ALIAS=${1:-"zco-claude"}
M_ALIAS=zco-claude
M_branch=$(git branch --show-current)

##; 判断当前分支名是否包含 zco
if [[ ${M_branch} == *nico* ]]; then
  M_ALIAS=yja-claude
fi

_G_CUR_DIR=$(realpath ${SCRIPT_DIR})
_G_CUR_SCRIPT=${_G_CUR_DIR}/zco_claude_init.py
_G_DST_PDIR=$HOME/.local/bin
_G_DST_LINK=${_G_DST_PDIR}/${M_ALIAS}

M_version=$(python3 ${_G_CUR_SCRIPT} --version)

function pipe_green() {
  # echo -e "\033[32m$1\033[0m"
  # 从标准输入读取数据, 并将其转换为绿色文本输出
  while IFS= read -r line; do
    echo -e "\033[32m$line\033[0m"
  done
}

function pipe_blue() {
  # echo -e "\033[34m$1\033[0m"
  # 从标准输入读取数据, 并将其转换为蓝色文本输出
  while IFS= read -r line; do
    echo -e "\033[34m$line\033[0m"
  done
}

function prompt_confirm() {
  ##; yellow
  read -p $'\033[33m'"$1 [y/n]:  "$'\033[0m' response
  case $response in
  [yY]) return 0 ;;
  *) return 1 ;;
  esac
}

function check_install_bin() {
  local x_orig_bin=$1
  local x_dst_path=$2
  local x_dst_pdir=$(dirname ${x_dst_path})
  if [[ -n ${x_orig_bin} ]]; then
    # echo "[checked] 安装源已存在: ${x_orig_bin}"
    echo "[checked] 安装源检查完成"
  else
    echo "[error] 安装源不存在, 无法继续安装 !!!"
    exit 1
  fi

  if [[ -L ${x_dst_path} ]]; then
    if [[ $(readlink ${x_dst_path}) == ${x_orig_bin} ]]; then
      echo "已完成安装: ${x_dst_path}"
      return 0
    else
      if prompt_confirm "是否删除已存在的链接 ${x_dst_path}?"; then
        rm ${x_dst_path}
      else
        echo "保留原版本: ${x_dst_path}: $(${x_dst_path} --version)"
        echo "当前版本: $(${x_orig_bin} --version)"
        exit 0
      fi
    fi
  else
    ##; 检查目标路径是否为文件
    if [[ -f ${x_dst_path} ]]; then
      # echo "已存在: ${x_dst_path}"
      if prompt_confirm "是否删除已存在的文件 ${x_dst_path}?"; then
        rm ${x_dst_path}
      else
        echo "保留原版本: ${x_dst_path}: $(${x_dst_path} --version)"
        echo "当前版本: $(${x_orig_bin} --version)"
        exit 0
      fi
    fi
  fi

  ln -s ${x_orig_bin} ${x_dst_path}
  echo "[checked] 安装成功: (linked ${x_dst_path} -> ${x_orig_bin})"
  ##; 配置 PATH 环境变量
  ##; 判断 是否已经配置过 PATH 环境变量
  #echo "export PATH=${x_dst_pdir}:$PATH:$_G_CUR_DIR/ClaudeSettings/commands" >>$HOME/.bashrc
  if [[ $PATH != *${x_dst_pdir}:* ]]; then
    echo "[warn] PATH 环境变量未包含: ${x_dst_pdir}"
    if [[ -f $HOME/.bashrc ]]; then
      echo "export PATH=${x_dst_pdir}:$PATH" >>$HOME/.bashrc
    fi
    if [[ -f $HOME/.zshrc ]]; then
      echo "export PATH=${x_dst_pdir}:$PATH" >>$HOME/.zshrc
    fi
  else
    echo "[checked] PATH 环境变量已包含: ${x_dst_pdir}"
  fi
}

####################################################
cat <<EOF | pipe_green
-------------------------
usage: 
  当前仓库是一个 ClaudeSettings 扩展配置安装包
  指定项目路径, 基于模板仓库的 ClaudeSettings 扩展项目的 .claude 配置目录
  快速初始化项目: ${M_ALIAS} <target_project_dir>

安装源:  $(realpath ${_G_CUR_SCRIPT} --relative-to=${_G_CUR_DIR})
分支: ${M_branch}
版本: ${M_version}
目标安装位置: ${_G_DST_LINK}
-------------------------
EOF

prompt_confirm "是否继续安装?" || exit 0

check_install_bin ${_G_CUR_SCRIPT} ${_G_DST_LINK}

cat <<EOF | pipe_blue

[Installed]: ${M_ALIAS} 安装完成 
------------------------------------------------
  source: $(realpath ${_G_CUR_SCRIPT} --relative-to=${_G_CUR_DIR})
  branch: ${M_branch}
  version: ${M_version}
------------------------------------------------

usage: 
  指定项目路径, 基于模板仓库的 ClaudeSettings 扩展项目的 .claude 配置目录
  快速初始化项目: ${M_ALIAS} <target_project_dir>
  如果想查看更多帮助信息, 请执行: ${M_ALIAS} --help

note: 
  <target_project_dir>: 目标项目目录, 可以是绝对路径, 也可以是相对路径

EOF
