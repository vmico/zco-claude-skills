# Makefile for zco_claude_init.py
# Installation targets:
#   make install - Copy zco_claude_init.py to $HOME/.local/bin
#   make link    - Create symlink to zco_claude_init.py in $HOME/.local/bin
#   make uninstall - Remove installed binary

# Configuration
SCRIPT_COMM := zco-claude
SCRIPT_NAME := zco_claude_init.py
SOURCE_FILE := $(shell realpath $(SCRIPT_NAME))
INSTALL_DIR := $(HOME)/.local/bin
INSTALL_DEST := $(INSTALL_DIR)/$(SCRIPT_COMM)
X_VERSION := $(shell python3 $(SCRIPT_NAME) --version 2>/dev/null || echo "unknown")

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
	@echo "Script:      $(SCRIPT_NAME)"
	@echo "Version:     $(X_VERSION)"
	@echo "Source:      $(SOURCE_FILE)"
	@echo "InstallDir:  $(INSTALL_DIR)"
	@echo "InstallDest: $(INSTALL_DEST)"
	@echo ""
	@echo "Available targets:"
	@echo "  make install          - Copy script to $(INSTALL_DIR)"
	@echo "  make link             - Create symlink in $(INSTALL_DIR)"
	@echo "  make link-dev         - Create symlink as $(SCRIPT_COMM)-dev"
	@echo "  make uninstall        - Remove $(INSTALL_DEST)"
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
	@mkdir -p $(INSTALL_DIR)
	@echo "$(BLUE)[check]$(RESET) Directory ready: $(INSTALL_DIR)"

# Check and update PATH
check-path:
	@if ! echo "$(PATH)" | grep -q "$(INSTALL_DIR)"; then \
		echo "$(YELLOW)[warn]$(RESET) PATH does not contain: $(INSTALL_DIR)"; \
		if [ -f "$(HOME)/.bashrc" ]; then \
			echo "export PATH=$(INSTALL_DIR):\$$PATH" >> "$(HOME)/.bashrc"; \
			echo "$(GREEN)[fixed]$(RESET) Added to ~/.bashrc"; \
		fi; \
		if [ -f "$(HOME)/.zshrc" ]; then \
			echo "export PATH=$(INSTALL_DIR):\$$PATH" >> "$(HOME)/.zshrc"; \
			echo "$(GREEN)[fixed]$(RESET) Added to ~/.zshrc"; \
		fi; \
	else \
		echo "$(BLUE)[check]$(RESET) PATH already contains: $(INSTALL_DIR)"; \
	fi

# Remove existing installation
remove-existing:
	@if [ -L "$(INSTALL_DEST)" ]; then \
		echo "$(YELLOW)[warn]$(RESET) Removing existing symlink: $(INSTALL_DEST)"; \
		rm -f "$(INSTALL_DEST)"; \
	elif [ -f "$(INSTALL_DEST)" ]; then \
		echo "$(YELLOW)[warn]$(RESET) Removing existing file: $(INSTALL_DEST)"; \
		rm -f "$(INSTALL_DEST)"; \
	fi

# Install by copying the file
install: check-source check-dir remove-existing
	@echo "$(BLUE)[install]$(RESET) Copying $(SCRIPT_NAME) to $(INSTALL_DEST)..."
	@cp "$(SCRIPT_NAME)" "$(INSTALL_DEST)"
	@chmod +x "$(INSTALL_DEST)"
	@echo "$(GREEN)[done]$(RESET) Installed: $(INSTALL_DEST)"
	@$(MAKE) check-path
	@echo ""
	@echo "$(GREEN)Installation complete!$(RESET)"
	@echo "Usage: $(SCRIPT_COMM) --help"

# Install by creating a symlink
link: check-source check-dir remove-existing
	@echo "$(BLUE)[link]$(RESET) Creating symlink: $(INSTALL_DEST) -> $(SOURCE_FILE)"
	@ln -s "$(SOURCE_FILE)" "$(INSTALL_DEST)"
	@echo "$(GREEN)[done]$(RESET) Linked: $(INSTALL_DEST)"
	@$(MAKE) check-path
	@echo ""
	@echo "$(GREEN)Linking complete!$(RESET)"
	@echo "Usage: $(SCRIPT_COMM) --help"

# Install by creating a symlink (dev version) - reuses link target
link-dev:
	@$(MAKE) link SCRIPT_COMM=$(SCRIPT_COMM)-dev INSTALL_DEST=$(INSTALL_DIR)/$(SCRIPT_COMM)-dev

# Clean build artifacts
clean:
	@echo "$(BLUE)[clean]$(RESET) Cleaning build artifacts..."
	@rm -rf build dist *.egg-info
	@echo "$(GREEN)[done]$(RESET) Clean complete"
	@rm -rf __pycache_

# Uninstall the binary
uninstall:
	@if [ -L "$(INSTALL_DEST)" ] || [ -f "$(INSTALL_DEST)" ]; then \
		echo "$(BLUE)[uninstall]$(RESET) Removing: $(INSTALL_DEST)"; \
		rm -f "$(INSTALL_DEST)"; \
		echo "$(GREEN)[done]$(RESET) Uninstalled: $(INSTALL_DEST)"; \
	else \
		echo "$(YELLOW)[warn]$(RESET) Not found: $(INSTALL_DEST)"; \
	fi
	@if python3 -c "import zco_claude_init" 2>/dev/null; then \
		python3 -m pip uninstall zco-claude -y; \
		echo "$(GREEN)[done]$(RESET) Uninstalled: zco-claude"; \
	fi

####################################################
## tag: Create git tag for current version
add-tag:
	@echo "Creating git tag v$(X_VERSION)..."
	git tag v$(X_VERSION) -m "Release version $(X_VERSION)"
	git push --tags origin v$(X_VERSION)
	@echo "Push with: git push origin v$(X_VERSION)"

del-tag:
	@echo "Deleting git tag v$(X_VERSION)..."
	git tag -d v$(X_VERSION)
	git push origin :refs/tags/v$(X_VERSION)
	@echo "Push with: git push origin :refs/tags/v$(X_VERSION)"
####################################################

# Build package for PyPI
build-dist-v0: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 setup.py sdist ..."
	python3 setup.py sdist bdist_wheel
	@echo "$(GREEN)[done]$(RESET) Build complete"

build-dist-v1: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 -m build ..."
	@python3 -m pip install build -q 2>/dev/null || true
	@if python3 -c "import build" 2>/dev/null; then \
		export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple && python3 -m build; \
	fi
	@echo "$(GREEN)[done]$(RESET) Build complete"
	
# Build package for PyPI
build-dist-v2: clean
	@echo "$(BLUE)[build]$(RESET) Building package with python3 setup.py sdist ..."
	export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple && uv build
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


####################################################
