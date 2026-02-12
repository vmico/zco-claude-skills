function git_auto_commit() {
  ##; 1. 检查是否有 Staged (已暂存) 的改动
  if ! git diff --cached --quiet; then
    echo "检测到已暂存(staged)的代码，正在自动创建备份提交..."
    git commit -m "tm: checkout staged"
  fi

  ##; 2. 检查是否有已追踪但未提交 (Unstaged) 的改动
  ##; 注意：这里只针对 Git 已经追踪的文件，全新的 Untracked 文件不会被处理
  if ! git diff --quiet; then
    echo "检测到未暂存(unstaged)的改动，正在自动添加并备份..."
    ##; 只 add 那些已经被 Git 追踪的文件，避免把不想要的临时文件带进去
    git add -u
    git commit -m "tm: checkout unstaged"
  fi

  # 3. 处理完全未追踪 (Untracked) 的文件
  # 使用 git ls-files 检查是否有未追踪的文件（排除被 ignore 的）
  if [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "🆕 [Backup] 检测到新的未追踪文件，正在自动添加并备份..."
    git add .
    git commit -m "tm: checkout add Untracked"
  fi

  ##; 4. 执行真正的 checkout 命令
  ##; $@ 代表传递给 co 的所有参数，如 git co main
  #git checkout "$@"
}

###; 覆盖原有的 alias
##alias co='git_safe_checkout'
