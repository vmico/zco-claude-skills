#!/bin/bash

# 获取所有 yj3d-prod.v25* tags，按时间倒序
tags=$(git tag -l "yj3d-prod.v25*" --sort=-version:refname)

# 转换为数组
tag_array=($tags)

echo "找到 ${#tag_array[@]} 个 tags"

# 输出前 5 个 tag 的信息
for i in {0..4}; do
    if [ $i -ge ${#tag_array[@]} ]; then
        break
    fi
    
    current_tag="${tag_array[$i]}"
    
    # 提取版本号 (去掉 yj3d-prod.v 前缀)
    version="${current_tag#yj3d-prod.v}"
    
    # 格式化版本号为 YY.MM.DD
    formatted_version="${version:0:2}.${version:2:2}.${version:4:2}"
    
    echo ""
    echo "## v${formatted_version}"
    
    # 获取到前一个 tag 的 commits
    if [ $((i+1)) -lt ${#tag_array[@]} ]; then
        prev_tag="${tag_array[$((i+1))]}"
        
        # 获取 commits，按类型分组
        commits=$(git log ${prev_tag}..${current_tag} --oneline --no-merges --format="%s")
        
        # 分类处理
        echo "$commits" | grep -i "^feat:" | sed 's/^feat: */- **feat**: /'
        echo "$commits" | grep -i "^fix:" | sed 's/^fix: */- **fix**: /'
        echo "$commits" | grep -i "^fixed:" | sed 's/^fixed: */- **fix**: /'
        echo "$commits" | grep -i "^tofix:" | sed 's/^tofix: */- **fix**: /'
        echo "$commits" | grep -i "^api:" | sed 's/^api: */- **api**: /'
        echo "$commits" | grep -i "^chore:" | sed 's/^chore: */- **chore**: /'
        echo "$commits" | grep -i "^dbm:" | sed 's/^dbm: */- **dbm**: /'
        echo "$commits" | grep -i "^ci:" | sed 's/^ci: */- **ci**: /'
        echo "$commits" | grep -i "^doc:" | sed 's/^doc: */- **doc**: /'
        
        # 其他未分类的
        echo "$commits" | grep -iv "^feat:\|^fix:\|^fixed:\|^tofix:\|^api:\|^chore:\|^dbm:\|^ci:\|^doc:" | sed 's/^/- /'
    fi
done
