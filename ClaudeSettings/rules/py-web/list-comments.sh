#!/bin/bash

## Python 注释列表脚本
## 用于列出项目中所有的非代码注释 (##;)

## 颜色定义
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' ## No Color

echo "🔍 Python 项目注释扫描"
echo "======================="
echo ""

## 定义注释类型
TYPES=(
    "TODO:待办事项"
    "FIXME:需要修复"
    "NOTE:开发者备注"
    "HACK:临时方案"
    "OPTIMIZE:性能优化"
    "DEPRECATED:已废弃"
    "DEBUG:调试信息"
    "XXX:需要注意"
)

## 检查是否扫描特定类型
SCAN_TYPE=""
if [ -n "$1" ]; then
    SCAN_TYPE="$1"
    echo "📌 只扫描类型: $SCAN_TYPE"
    echo ""
fi

## 统计所有非代码注释
if [ -z "$SCAN_TYPE" ]; then
    echo "📊 注释统计"
    echo "-----------"
    
    TOTAL_FUNCTIONAL=$(grep -r "##;[^@]" . --include="*.py" 2>/dev/null | wc -l || echo 0)
    TOTAL_META=$(grep -r "##;@" . --include="*.py" 2>/dev/null | wc -l || echo 0)
    
    echo -e "功能注释 (##; ): ${BLUE}$TOTAL_FUNCTIONAL${NC}"
    echo -e "元信息注释 (##;@): ${YELLOW}$TOTAL_META${NC}"
    echo ""
    
    ## 按类型统计
    echo "按类型统计:"
    for type_info in "${TYPES[@]}"; do
        IFS=':' read -r type_name type_desc <<< "$type_info"
        COUNT=$(grep -r "##;@$type_name" . --include="*.py" 2>/dev/null | wc -l || echo 0)
        
        if [ "$COUNT" -gt 0 ]; then
            case "$type_name" in
                "FIXME"|"DEPRECATED")
                    echo -e "  ${RED}$type_name:${NC} $COUNT ($type_desc)"
                    ;;
                "TODO"|"HACK")
                    echo -e "  ${YELLOW}$type_name:${NC} $COUNT ($type_desc)"
                    ;;
                *)
                    echo -e "  ${GREEN}$type_name:${NC} $COUNT ($type_desc)"
                    ;;
            esac
        fi
    done
    echo ""
fi

## 显示详细列表
echo "📋 详细列表"
echo "-----------"

## 构建 grep 模式
if [ -n "$SCAN_TYPE" ]; then
    PATTERN="##;@$SCAN_TYPE"
else
    PATTERN="##;@"
fi

## 查找并格式化输出
grep -rn "$PATTERN" . --include="*.py" 2>/dev/null | while read -r line; do
    ## 解析文件名、行号和内容
    FILE=$(echo "$line" | cut -d: -f1)
    LINENO=$(echo "$line" | cut -d: -f2)
    CONTENT=$(echo "$line" | cut -d: -f3- | sed 's/^[[:space:]]*##;@[A-Z]*:[[:space:]]*//')
    TYPE=$(echo "$line" | grep -o "##;@[A-Z]*:" | sed 's/##;@//' | sed 's/://')
    
    ## 确定颜色
    case "$TYPE" in
        "FIXME"|"DEPRECATED")
            COLOR="$RED"
            ;;
        "TODO"|"HACK")
            COLOR="$YELLOW"
            ;;
        *)
            COLOR="$GREEN"
            ;;
    esac
    
    ## 输出
    echo -e "${BLUE}${FILE}:${LINENO}${NC} ${COLOR}[${TYPE}]${NC} ${CONTENT}"
done

## 如果没有找到任何注释
if [ -z "$(grep -rn "$PATTERN" . --include="*.py" 2>/dev/null)" ]; then
    echo "未找到相关注释"
fi

echo ""
echo "💡 提示:"
echo "  - 运行 './list-comments.sh FIXME' 只显示 FIXME 注释"
echo "  - 运行 './list-comments.sh TODO' 只显示 TODO 注释"
