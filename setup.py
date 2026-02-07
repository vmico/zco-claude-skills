#!/usr/bin/env python3
"""Setup script for zco-claude package"""

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
import os
import shutil

class CustomBuildPy(_build_py):
    """自定义 build_py 来包含 ClaudeSettings"""
    def run(self):
        # 先执行默认的 build_py
        super().run()
        
        # 复制 ClaudeSettings 到 build 目录
        if os.path.exists('ClaudeSettings'):
            target = os.path.join(self.build_lib, 'ClaudeSettings')
            if os.path.isdir('ClaudeSettings'):
                if os.path.exists(target):
                    shutil.rmtree(target)
                shutil.copytree('ClaudeSettings', target)

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'readme.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="zco-claude",
    version="0.1.0",
    author="ZCO Team",
    author_email="zco@example.com",
    description="Claude Code 配置管理工具 - 快速初始化项目的 .claude 配置目录",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zco-team/zco-claude",
    # 单文件模块
    py_modules=["zco_claude_init"],
    # 自定义命令
    cmdclass={'build_py': CustomBuildPy},
    # 包含数据文件
    include_package_data=True,
    zip_safe=False,  # 关键：不允许 zip 安装，以便访问数据文件
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Tools",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "zco-claude=zco_claude_init:main",
            "zco-claude-init=zco_claude_init:main",
        ],
    },
)
