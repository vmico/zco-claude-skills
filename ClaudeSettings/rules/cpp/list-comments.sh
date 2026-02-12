#!/bin/bash
#
# list-comments.sh - 列出 C++ 代码中所有非代码注释
#
# 使用方法:
#   ./list-comments.sh [选项] [目录]
#
# 选项:
#   -h, --help      显示帮助信息
#   -t, --todo      只显示 TODO
#   -f, --fixme     只显示 FIXME
#   -a, --all       显示所有类型的注释
#   --no-color      禁用颜色输出
#
# 示例:
#   ./list-comments.sh
#   ./list-comments.sh ./src
#   ./list-comments.sh -t
#   ./list-comments.sh -f ./core

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Color

# 配置
SHOW_TODO=0
SHOW_FIXME=0
SHOW_HACK=0
SHOW_OPTIMIZE=0
SHOW_DEPRECATED=0
SHOW_NOTE=0
SHOW_DEBUG=0
SHOW_ALL=1
USE_COLOR=1
SEARCH_DIR="."

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "List Comments Tool for C++ Projects"
            echo "Usage: $0 [options] [directory]"
            echo ""
            echo "Options:"
            echo "  -h, --help      Show this help message"
            echo "  -t, --todo      Show only TODO comments"
            echo "  -f, --fixme     Show only FIXME comments"
            echo "  -a, --hack      Show only HACK comments"
            echo "  -o, --optimize  Show only OPTIMIZE comments"
            echo "  -d, --deprecated Show only DEPRECATED comments"
            echo "  -n, --note      Show only NOTE comments"
            echo "  --debug         Show only DEBUG comments"
            echo "  --all           Show all comment types (default)"
            echo "  --no-color      Disable color output"
            echo ""
            echo "Examples:"
            echo "  $0              # List all comments in current directory"
            echo "  $0 ./src        # List all comments in ./src"
            echo "  $0 -t           # List only TODO comments"
            echo "  $0 -f ./core    # List only FIXME comments in ./core"
            exit 0
            ;;
        -t|--todo)
            SHOW_ALL=0
            SHOW_TODO=1
            shift
            ;;
        -f|--fixme)
            SHOW_ALL=0
            SHOW_FIXME=1
            shift
            ;;
        -a|--hack)
            SHOW_ALL=0
            SHOW_HACK=1
            shift
            ;;
        -o|--optimize)
            SHOW_ALL=0
            SHOW_OPTIMIZE=1
            shift
            ;;
        -d|--deprecated)
            SHOW_ALL=0
            SHOW_DEPRECATED=1
            shift
            ;;
        -n|--note)
            SHOW_ALL=0
            SHOW_NOTE=1
            shift
            ;;
        --debug)
            SHOW_ALL=0
            SHOW_DEBUG=1
            shift
            ;;
        --all)
            SHOW_ALL=1
            shift
            ;;
        --no-color)
            USE_COLOR=0
            shift
            ;;
        -*)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
        *)
            SEARCH_DIR="$1"
            shift
            ;;
    esac
done

# 禁用颜色
if [ $USE_COLOR -eq 0 ]; then
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    MAGENTA=''
    CYAN=''
    ORANGE=''
    NC=''
fi

# 检查是否是 C++ 项目
check_cpp_project() {
    local has_cpp=0
    if find "$SEARCH_DIR" -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" \) 2>/dev/null | head -1 | grep -q .; then
        has_cpp=1
    fi

    if [ $has_cpp -eq 0 ]; then
        echo "No C++ files found in '$SEARCH_DIR'"
        echo "This doesn't appear to be a C++ project."
        exit 0
    fi
}

# 搜索注释
search_comments() {
    local pattern=$1
    local exclude_dirs="-not -path '*/build/*' -not -path '*/.git/*' -not -path '*/third_party/*' -not -path '*/external/*'"

    find "$SEARCH_DIR" -type f \( -name "*.cpp" -o -name "*.h" -o -name "*.hpp" \) \
        -not -path '*/build/*' \
        -not -path '*/.git/*' \
        -not -path '*/third_party/*' \
        -not -path '*/external/*' \
        -exec grep -Hn "$pattern" {} + 2>/dev/null || true
}

# 打印分类标题
print_category_header() {
    local icon=$1
    local color=$2
    local title=$3
    local count=$4

    echo -e "\n${color}${icon} ${title} (${count})${NC}"
    echo -e "${color}$(printf '=%.0s' $(seq 1 60))${NC}"
}

# 打印注释行
print_comment() {
    local line=$1
    local color=$2

    # 解析文件名、行号和内容
    local file=$(echo "$line" | cut -d: -f1)
    local lineno=$(echo "$line" | cut -d: -f2)
    local content=$(echo "$line" | cut -d: -f3-)

    # 提取注释内容（去掉前缀）
    local comment=$(echo "$content" | sed 's/.*\/\/;@[A-Z]*:\s*//' | sed 's/.*\/\/;\s*//')

    # 显示
    echo -e "  ${color}•${NC} ${file}:${lineno}"
    echo -e "    ${comment}"
}

# ═══════════════════════════════════════════════════════════════
# 主程序
# ═══════════════════════════════════════════════════════════════

echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  C++ Comment Extractor${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "  Searching in: ${SEARCH_DIR}"
echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"

# 检查是否是 C++ 项目
check_cpp_project

# 统计
TODO_COUNT=0
FIXME_COUNT=0
HACK_COUNT=0
OPTIMIZE_COUNT=0
DEPRECATED_COUNT=0
NOTE_COUNT=0
DEBUG_COUNT=0

# 收集结果
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_TODO -eq 1 ]; then
    TODO_LIST=$(search_comments "//;@TODO:")
    TODO_COUNT=$(echo "$TODO_LIST" | grep -c . || true)
    if [ -z "$TODO_LIST" ]; then TODO_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_FIXME -eq 1 ]; then
    FIXME_LIST=$(search_comments "//;@FIXME:")
    FIXME_COUNT=$(echo "$FIXME_LIST" | grep -c . || true)
    if [ -z "$FIXME_LIST" ]; then FIXME_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_HACK -eq 1 ]; then
    HACK_LIST=$(search_comments "//;@HACK:")
    HACK_COUNT=$(echo "$HACK_LIST" | grep -c . || true)
    if [ -z "$HACK_LIST" ]; then HACK_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_OPTIMIZE -eq 1 ]; then
    OPTIMIZE_LIST=$(search_comments "//;@OPTIMIZE:")
    OPTIMIZE_COUNT=$(echo "$OPTIMIZE_LIST" | grep -c . || true)
    if [ -z "$OPTIMIZE_LIST" ]; then OPTIMIZE_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_DEPRECATED -eq 1 ]; then
    DEPRECATED_LIST=$(search_comments "//;@DEPRECATED:")
    DEPRECATED_COUNT=$(echo "$DEPRECATED_LIST" | grep -c . || true)
    if [ -z "$DEPRECATED_LIST" ]; then DEPRECATED_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_NOTE -eq 1 ]; then
    NOTE_LIST=$(search_comments "//;@NOTE:")
    NOTE_COUNT=$(echo "$NOTE_LIST" | grep -c . || true)
    if [ -z "$NOTE_LIST" ]; then NOTE_COUNT=0; fi
fi

if [ $SHOW_ALL -eq 1 ] || [ $SHOW_DEBUG -eq 1 ]; then
    DEBUG_LIST=$(search_comments "//;@DEBUG:")
    DEBUG_COUNT=$(echo "$DEBUG_LIST" | grep -c . || true)
    if [ -z "$DEBUG_LIST" ]; then DEBUG_COUNT=0; fi
fi

# 显示 TODO
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_TODO -eq 1 ]; then
    if [ $TODO_COUNT -gt 0 ]; then
        print_category_header "📋" "$BLUE" "TODO List" "$TODO_COUNT"
        echo "$TODO_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$BLUE"
            fi
        done
    elif [ $SHOW_TODO -eq 1 ]; then
        echo -e "\n${GREEN}✓ No TODO comments found${NC}"
    fi
fi

# 显示 FIXME
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_FIXME -eq 1 ]; then
    if [ $FIXME_COUNT -gt 0 ]; then
        print_category_header "🔧" "$RED" "FIXME List" "$FIXME_COUNT"
        echo "$FIXME_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$RED"
            fi
        done
    elif [ $SHOW_FIXME -eq 1 ]; then
        echo -e "\n${GREEN}✓ No FIXME comments found${NC}"
    fi
fi

# 显示 HACK
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_HACK -eq 1 ]; then
    if [ $HACK_COUNT -gt 0 ]; then
        print_category_header "⚠️" "$ORANGE" "HACK List" "$HACK_COUNT"
        echo "$HACK_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$ORANGE"
            fi
        done
    elif [ $SHOW_HACK -eq 1 ]; then
        echo -e "\n${GREEN}✓ No HACK comments found${NC}"
    fi
fi

# 显示 OPTIMIZE
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_OPTIMIZE -eq 1 ]; then
    if [ $OPTIMIZE_COUNT -gt 0 ]; then
        print_category_header "⚡" "$CYAN" "OPTIMIZE List" "$OPTIMIZE_COUNT"
        echo "$OPTIMIZE_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$CYAN"
            fi
        done
    elif [ $SHOW_OPTIMIZE -eq 1 ]; then
        echo -e "\n${GREEN}✓ No OPTIMIZE comments found${NC}"
    fi
fi

# 显示 DEPRECATED
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_DEPRECATED -eq 1 ]; then
    if [ $DEPRECATED_COUNT -gt 0 ]; then
        print_category_header "🗑️" "$MAGENTA" "DEPRECATED List" "$DEPRECATED_COUNT"
        echo "$DEPRECATED_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$MAGENTA"
            fi
        done
    elif [ $SHOW_DEPRECATED -eq 1 ]; then
        echo -e "\n${GREEN}✓ No DEPRECATED comments found${NC}"
    fi
fi

# 显示 NOTE
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_NOTE -eq 1 ]; then
    if [ $NOTE_COUNT -gt 0 ]; then
        print_category_header "📝" "$GREEN" "NOTE List" "$NOTE_COUNT"
        echo "$NOTE_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$GREEN"
            fi
        done
    elif [ $SHOW_NOTE -eq 1 ]; then
        echo -e "\n${GREEN}✓ No NOTE comments found${NC}"
    fi
fi

# 显示 DEBUG
if [ $SHOW_ALL -eq 1 ] || [ $SHOW_DEBUG -eq 1 ]; then
    if [ $DEBUG_COUNT -gt 0 ]; then
        print_category_header "🐛" "$YELLOW" "DEBUG List" "$DEBUG_COUNT"
        echo "$DEBUG_LIST" | while IFS= read -r line; do
            if [ -n "$line" ]; then
                print_comment "$line" "$YELLOW"
            fi
        done
    elif [ $SHOW_DEBUG -eq 1 ]; then
        echo -e "\n${GREEN}✓ No DEBUG comments found${NC}"
    fi
fi

# 显示统计摘要
echo -e "\n${BLUE}══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Summary${NC}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"

TOTAL=$((TODO_COUNT + FIXME_COUNT + HACK_COUNT + OPTIMIZE_COUNT + DEPRECATED_COUNT + NOTE_COUNT + DEBUG_COUNT))

echo -e "  ${BLUE}📋 TODO:${NC}        ${TODO_COUNT}"
echo -e "  ${RED}🔧 FIXME:${NC}       ${FIXME_COUNT}"
echo -e "  ${ORANGE}⚠️  HACK:${NC}        ${HACK_COUNT}"
echo -e "  ${CYAN}⚡ OPTIMIZE:${NC}    ${OPTIMIZE_COUNT}"
echo -e "  ${MAGENTA}🗑️  DEPRECATED:${NC} ${DEPRECATED_COUNT}"
echo -e "  ${GREEN}📝 NOTE:${NC}        ${NOTE_COUNT}"
echo -e "  ${YELLOW}🐛 DEBUG:${NC}       ${DEBUG_COUNT}"
echo -e "${BLUE}──────────────────────────────────────────────────────────────${NC}"
echo -e "  ${BLUE}Total:${NC}          ${TOTAL}"
echo -e "${BLUE}══════════════════════════════════════════════════════════════${NC}"

# 建议
if [ $FIXME_COUNT -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  You have ${FIXME_COUNT} FIXME(s) that should be addressed.${NC}"
fi

if [ $HACK_COUNT -gt 0 ]; then
    echo -e "${YELLOW}⚠️  You have ${HACK_COUNT} HACK(s) that should be refactored.${NC}"
fi

if [ $TOTAL -eq 0 ]; then
    echo -e "\n${GREEN}✓ No non-code comments found. Clean codebase!${NC}"
fi

exit 0
