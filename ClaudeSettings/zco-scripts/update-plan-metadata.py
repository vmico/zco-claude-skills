#!/usr/bin/env python3
"""
Plan Metadata Auto-Update Script

Updates YAML front matter in plan documents with:
- Status transitions (draft:0 → ongoing:2 → completed:3)
- Timestamp management (created_at, updated_at)
- Auto-generated tags (from Claude input)

Usage:
    echo '{"plan_path": "/path/to/plan.md", "action": "start"}' | python3 update-plan-metadata.py

Actions:
    - start: Set status to ongoing:2, initialize timestamps
    - complete: Set status to completed:3, update timestamp
    - fail: Set status to failed:4, update timestamp
    - cancel: Set status to canceled:5, update timestamp

Input (stdin JSON):
    {
        "plan_path": "/path/to/plan.md",
        "action": "start|complete|fail|cancel",
        "tags": ["feature", "backend"]  # optional
    }

Output (stdout JSON):
    Success: {"success": true, "old_status": "draft:0", "new_status": "ongoing:2", "updated_at": "2026-01-09 15:30:45"}
    Error: {"success": false, "error": "error message"}
"""

import json
import sys
import re
from datetime import datetime
from pathlib import Path
import tempfile
import shutil

try:
    import yaml
except ImportError:
    print(json.dumps({
        'success': False,
        'error': 'PyYAML not installed. Run: pip install PyYAML'
    }), file=sys.stderr)
    sys.exit(1)


class PlanMetadataUpdater:
    """Handles parsing and updating plan document YAML front matter"""

    STATUS_ENUM = {
        'draft:0': '起稿中',
        'ready:1': '准备就绪',
        'ongoing:2': '进行中',
        'completed:3': '执行完成',
        'failed:4': '执行失败',
        'canceled:5': '已取消',
        'archived:8': '已归档'
    }

    PRIORITY_ENUM = {
        'p0:紧急:重要': '紧急且重要',
        'p1:高:当前迭代/排期内重点解决': '高优先级',
        'p2:中:可纳入后续迭代计划': '中等优先级',
        'p3:低:可记录，待后续评估': '低优先级',
        'p4:无:不影响当前迭代/排期': '无优先级'
    }

    def __init__(self, plan_path: str):
        self.plan_path = Path(plan_path)

        if not self.plan_path.exists():
            raise FileNotFoundError(f"Plan file not found: {plan_path}")

        self.content = self._read_file()
        self.yaml_data, self.yaml_start, self.yaml_end = self._parse_yaml()
        self.body = self.content[self.yaml_end:]

    def _read_file(self) -> str:
        """Read plan file content"""
        try:
            return self.plan_path.read_text(encoding='utf-8')
        except Exception as e:
            raise IOError(f"Failed to read file {self.plan_path}: {e}")

    def _parse_yaml(self) -> tuple:
        """
        Parse YAML front matter

        Returns:
            tuple: (yaml_data dict, yaml_start pos, yaml_end pos)
        """
        # Extract YAML between --- markers
        match = re.match(r'^(---\n)(.*?)(---\n)', self.content, re.DOTALL)

        if not match:
            raise ValueError(
                f"No YAML front matter found in {self.plan_path.name}. "
                "File must start with ---\\n and end YAML section with ---\\n"
            )

        yaml_start = match.start()
        yaml_end = match.end()
        yaml_text = match.group(2)

        try:
            yaml_data = yaml.safe_load(yaml_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Malformed YAML in {self.plan_path.name}: {e}")

        if not isinstance(yaml_data, dict):
            raise ValueError(f"YAML front matter must be a dictionary, got: {type(yaml_data)}")

        return yaml_data, yaml_start, yaml_end

    def normalize_status(self, status: str) -> str:
        """
        Convert old status format to new enum format

        Args:
            status: Status string (old or new format)

        Returns:
            Normalized status in enum format (e.g., "ongoing:2")
        """
        # Map old format to new format
        status_map = {
            'pending': 'draft:0',
            'in-progress': 'ongoing:2',
            'completed': 'completed:3',
            'cancelled': 'canceled:5'
        }

        if ':' in status:
            # Already new format - validate it exists
            if status in self.STATUS_ENUM:
                return status
            else:
                # Unknown enum, default to draft
                return 'draft:0'
        else:
            # Old format - convert
            return status_map.get(status.lower(), 'draft:0')

    def update_status(self, new_status: str, tags: list = None):
        """
        Update plan status and timestamps

        Args:
            new_status: Target status (ongoing:2, completed:3, etc.)
            tags: Optional tags list from Claude

        Returns:
            tuple: (old_status, new_status)
        """
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Get and normalize current status
        old_status = self.yaml_data.get('status', 'draft:0')
        old_status = self.normalize_status(old_status)

        # Validate new status
        if new_status not in self.STATUS_ENUM:
            raise ValueError(f"Invalid status: {new_status}. Must be one of: {list(self.STATUS_ENUM.keys())}")

        # Update status
        self.yaml_data['status'] = new_status

        # Update timestamps
        if not self.yaml_data.get('created_at') or self.yaml_data.get('created_at') == '':
            # First execution - set created_at
            self.yaml_data['created_at'] = now

        self.yaml_data['updated_at'] = now

        # Update tags if provided
        if tags is not None:
            if isinstance(tags, list):
                self.yaml_data['tags'] = tags
            elif isinstance(tags, str):
                # Parse comma-separated string
                self.yaml_data['tags'] = [t.strip() for t in tags.split(',') if t.strip()]

        # Ensure other required fields exist
        if 'seq' not in self.yaml_data:
            # Try to extract from filename: plan.{seq}.*.md
            match = re.match(r'plan\.(\d+)\.', self.plan_path.name)
            if match:
                self.yaml_data['seq'] = int(match.group(1))

        if 'priority' not in self.yaml_data or self.yaml_data.get('priority') == '':
            # Default priority
            self.yaml_data['priority'] = 'p2:中:可纳入后续迭代计划'

        # Write back to file
        self._write_file()

        return old_status, new_status

    def _write_file(self):
        """
        Write updated content back to file using atomic write

        Uses temp file + rename to prevent corruption
        """
        try:
            # Dump YAML with custom settings
            yaml_str = yaml.dump(
                self.yaml_data,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=1000  # Prevent line wrapping
            )

            # Reconstruct file content
            new_content = f"---\n{yaml_str}---\n{self.body}"

            # Atomic write: write to temp file, then rename
            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.md',
                prefix=f'.{self.plan_path.name}_',
                dir=self.plan_path.parent,
                text=True
            )

            try:
                with open(temp_fd, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                # Atomic rename
                shutil.move(temp_path, self.plan_path)

            except Exception as e:
                # Cleanup temp file on error
                try:
                    Path(temp_path).unlink()
                except:
                    pass
                raise

        except Exception as e:
            raise IOError(f"Failed to write file {self.plan_path}: {e}")


def main():
    """
    CLI Interface for plan metadata updates

    Reads JSON from stdin, updates plan metadata, outputs JSON result
    """
    try:
        # Read JSON input from stdin
        input_data = json.load(sys.stdin)

        # Validate required fields
        if 'plan_path' not in input_data:
            raise ValueError("Missing required field: plan_path")

        if 'action' not in input_data:
            raise ValueError("Missing required field: action")

        plan_path = input_data['plan_path']
        action = input_data['action']
        tags = input_data.get('tags', None)

        # Map action to status
        status_map = {
            'start': 'ongoing:2',
            'complete': 'completed:3',
            'fail': 'failed:4',
            'cancel': 'canceled:5'
        }

        new_status = status_map.get(action)
        if not new_status:
            raise ValueError(f"Invalid action: {action}. Must be one of: {list(status_map.keys())}")

        # Update metadata
        updater = PlanMetadataUpdater(plan_path)
        old_status, new_status = updater.update_status(new_status, tags)

        # Success response
        result = {
            'success': True,
            'plan_path': plan_path,
            'old_status': old_status,
            'new_status': new_status,
            'created_at': updater.yaml_data.get('created_at', ''),
            'updated_at': updater.yaml_data.get('updated_at', ''),
            'tags': updater.yaml_data.get('tags', [])
        }

        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)

    except json.JSONDecodeError as e:
        error_result = {
            'success': False,
            'error': f'Invalid JSON input: {e}'
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)

    except (ValueError, FileNotFoundError, IOError) as e:
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        error_result = {
            'success': False,
            'error': f'Unexpected error: {type(e).__name__}: {e}'
        }
        print(json.dumps(error_result), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
