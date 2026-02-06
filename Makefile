# Makefile for zco_claude_init.py
# Installation targets:
#   make install - Copy zco_claude_init.py to $HOME/.local/bin
#   make link    - Create symlink to zco_claude_init.py in $HOME/.local/bin
#   make uninstall - Remove installed binary

# Configuration
SCRIPT_NAME := zco_claude_init.py
SCRIPT_ALIAS := zco-claude
DST_DIR := $(HOME)/.local/bin
DST_PATH := $(DST_DIR)/$(SCRIPT_ALIAS)
SRC_PATH := $(realpath $(SCRIPT_NAME))
VERSION := $(shell python3 $(SCRIPT_NAME) --version 2>/dev/null || echo "unknown")

# Colors for output
GREEN := \033[32m
BLUE := \033[34m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
.PHONY: all install link uninstall check info help

all: info

info:
	@echo "$(GREEN)zco_claude_init.py Installation Makefile$(RESET)"
	@echo ""
	@echo "Source:      $(SRC_PATH)"
	@echo "Version:     $(VERSION)"
	@echo "Install dir: $(DST_DIR)"
	@echo "Target:      $(DST_PATH)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install   - Copy script to $(DST_DIR)"
	@echo "  make link      - Create symlink in $(DST_DIR)"
	@echo "  make uninstall - Remove $(DST_PATH)"
	@echo "  make help      - Show this help message"

help: info

# Check if source exists
check-source:
	@if [ ! -f "$(SCRIPT_NAME)" ]; then \
		echo "$(RED)Error: $(SCRIPT_NAME) not found!$(RESET)"; \
		exit 1; \
	fi

# Create destination directory if needed
check-dir:
	@mkdir -p $(DST_DIR)
	@echo "$(BLUE)[check]$(RESET) Directory ready: $(DST_DIR)"

# Check and update PATH
check-path:
	@if ! echo "$(PATH)" | grep -q "$(DST_DIR)"; then \
		echo "$(YELLOW)[warn]$(RESET) PATH does not contain: $(DST_DIR)"; \
		if [ -f "$(HOME)/.bashrc" ]; then \
			echo "export PATH=$(DST_DIR):\$$PATH" >> "$(HOME)/.bashrc"; \
			echo "$(GREEN)[fixed]$(RESET) Added to ~/.bashrc"; \
		fi; \
		if [ -f "$(HOME)/.zshrc" ]; then \
			echo "export PATH=$(DST_DIR):\$$PATH" >> "$(HOME)/.zshrc"; \
			echo "$(GREEN)[fixed]$(RESET) Added to ~/.zshrc"; \
		fi; \
	else \
		echo "$(BLUE)[check]$(RESET) PATH already contains: $(DST_DIR)"; \
	fi

# Remove existing installation
remove-existing:
	@if [ -L "$(DST_PATH)" ]; then \
		echo "$(YELLOW)[warn]$(RESET) Removing existing symlink: $(DST_PATH)"; \
		rm -f "$(DST_PATH)"; \
	elif [ -f "$(DST_PATH)" ]; then \
		echo "$(YELLOW)[warn]$(RESET) Removing existing file: $(DST_PATH)"; \
		rm -f "$(DST_PATH)"; \
	fi

# Install by copying the file
install: check-source check-dir remove-existing
	@echo "$(BLUE)[install]$(RESET) Copying $(SCRIPT_NAME) to $(DST_PATH)..."
	@cp "$(SCRIPT_NAME)" "$(DST_PATH)"
	@chmod +x "$(DST_PATH)"
	@echo "$(GREEN)[done]$(RESET) Installed: $(DST_PATH)"
	@$(MAKE) check-path
	@echo ""
	@echo "$(GREEN)Installation complete!$(RESET)"
	@echo "Usage: $(SCRIPT_ALIAS) --help"

# Install by creating a symlink
link: check-source check-dir remove-existing
	@echo "$(BLUE)[link]$(RESET) Creating symlink: $(DST_PATH) -> $(SRC_PATH)"
	@ln -s "$(SRC_PATH)" "$(DST_PATH)"
	@echo "$(GREEN)[done]$(RESET) Linked: $(DST_PATH)"
	@$(MAKE) check-path
	@echo ""
	@echo "$(GREEN)Linking complete!$(RESET)"
	@echo "Usage: $(SCRIPT_ALIAS) --help"

# Uninstall the binary
uninstall:
	@if [ -L "$(DST_PATH)" ] || [ -f "$(DST_PATH)" ]; then \
		echo "$(BLUE)[uninstall]$(RESET) Removing: $(DST_PATH)"; \
		rm -f "$(DST_PATH)"; \
		echo "$(GREEN)[done]$(RESET) Uninstalled: $(DST_PATH)"; \
	else \
		echo "$(YELLOW)[warn]$(RESET) Not found: $(DST_PATH)"; \
	fi
