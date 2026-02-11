# Makefile for zco_claude_init.py
# Installation targets:
#   make install - Copy zco_claude_init.py to $HOME/.local/bin
#   make link    - Create symlink to zco_claude_init.py in $HOME/.local/bin
#   make uninstall - Remove installed binary

# Configuration
SCRIPT_NAME := zco_claude_init.py
SCRIPT_COMM := zco-claude
DST_DIR := $(HOME)/.local/bin
DST_PATH := $(DST_DIR)/$(SCRIPT_COMM)
SRC_PATH := $(realpath $(SCRIPT_NAME))
VERSION := $(shell python3 $(SCRIPT_NAME) --version 2>/dev/null || echo "unknown")

# Colors for output
GREEN := \033[32m
BLUE := \033[34m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Default target
.PHONY: all install link uninstall check info help twine-pypi-local twine-pypi-upload

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
	@echo "  make install          - Copy script to $(DST_DIR)"
	@echo "  make link             - Create symlink in $(DST_DIR)"
	@echo "  make link-dev         - Create symlink as $(SCRIPT_COMM)-dev"
	@echo "  make uninstall        - Remove $(DST_PATH)"
	@echo "  make twine-pypi-local - Build and check package locally"
	@echo "  make twine-pypi-upload - Upload to PyPI production server"
	@echo "  make help             - Show this help message"

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
	@echo "Usage: $(SCRIPT_COMM) --help"

# Install by creating a symlink
link: check-source check-dir remove-existing
	@echo "$(BLUE)[link]$(RESET) Creating symlink: $(DST_PATH) -> $(SRC_PATH)"
	@ln -s "$(SRC_PATH)" "$(DST_PATH)"
	@echo "$(GREEN)[done]$(RESET) Linked: $(DST_PATH)"
	@$(MAKE) check-path
	@echo ""
	@echo "$(GREEN)Linking complete!$(RESET)"
	@echo "Usage: $(SCRIPT_COMM) --help"

# Install by creating a symlink (dev version) - reuses link target
link-dev:
	@$(MAKE) link SCRIPT_COMM=$(SCRIPT_COMM)-dev DST_PATH=$(DST_DIR)/$(SCRIPT_COMM)-dev

# Clean build artifacts
clean:
	@echo "$(BLUE)[clean]$(RESET) Cleaning build artifacts..."
	@rm -rf build dist *.egg-info
	@echo "$(GREEN)[done]$(RESET) Clean complete"
	@rm -rf __pycache_


# Build package for PyPI
build-dist-v1: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 -m build ..."
	@python3 -m pip install build -q 2>/dev/null || true
	@if python3 -c "import build" 2>/dev/null; then \
		export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple && python3 -m build; \
	fi
	@echo "$(GREEN)[done]$(RESET) Build complete"
	
# Build package for PyPI
build-dist-v0: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 setup.py sdist ..."
	python3 setup.py sdist bdist_wheel; \
	@echo "$(GREEN)[done]$(RESET) Build complete"

# Build package for PyPI
build-dist-v2: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 setup.py sdist ..."
	export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple && uv build; \
	@echo "$(GREEN)[done]$(RESET) Build complete"

# Build and check package locally (without upload)
twine-pypi-local: build-dist-v2
	@echo "$(BLUE)[twine]$(RESET) Checking package with twine..."
	@python3 -m twine check dist/*
	@echo "$(GREEN)[done]$(RESET) Local check complete"

# Upload to PyPI production server
twine-pypi-upload: build-dist-v2
	@echo "$(BLUE)[twine]$(RESET) Uploading to PyPI production server..."
	@python3 -m twine upload dist/*
	@echo "$(GREEN)[done]$(RESET) Upload to production server complete"

# Uninstall the binary
uninstall:
	@if [ -L "$(DST_PATH)" ] || [ -f "$(DST_PATH)" ]; then \
		echo "$(BLUE)[uninstall]$(RESET) Removing: $(DST_PATH)"; \
		rm -f "$(DST_PATH)"; \
		echo "$(GREEN)[done]$(RESET) Uninstalled: $(DST_PATH)"; \
	else \
		echo "$(YELLOW)[warn]$(RESET) Not found: $(DST_PATH)"; \
	fi
	@if python3 -c "import zco_claude_init" 2>/dev/null; then \
		python3 -m pip uninstall zco-claude -y; \
		echo "$(GREEN)[done]$(RESET) Uninstalled: zco-claude"; \
	fi
