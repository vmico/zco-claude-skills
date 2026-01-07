#!/usr/bin/env python3
"""
Unit tests for update-plan-metadata.py

Tests:
1. Parse valid YAML front matter
2. Update status transitions
3. Set created_at only on first execution
4. Update updated_at on every execution
5. Merge tags without overwriting
6. Handle missing fields gracefully
7. Handle malformed YAML (error case)
8. Preserve Markdown body unchanged
9. Atomic write on success
10. Backwards compatibility with old format
"""

import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
import sys
import subprocess
import time

# Add parent dir to path to import the script
sys.path.insert(0, str(Path(__file__).parent))


class TestPlanMetadataUpdater(unittest.TestCase):
    """Test suite for plan metadata updates"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_plan(self, filename: str, content: str) -> Path:
        """Helper: Create a test plan file"""
        plan_path = self.test_dir_path / filename
        plan_path.write_text(content, encoding='utf-8')
        return plan_path

    def run_update_script(self, plan_path: Path, action: str, tags: list = None) -> dict:
        """
        Helper: Run update-plan-metadata.py script

        Args:
            plan_path: Path to plan file
            action: Action to perform (start, complete, fail, cancel)
            tags: Optional tags list

        Returns:
            dict: JSON result from script
        """
        input_data = {
            'plan_path': str(plan_path),
            'action': action
        }

        if tags is not None:
            input_data['tags'] = tags

        input_json = json.dumps(input_data)

        script_path = Path(__file__).parent / 'update-plan-metadata.py'

        result = subprocess.run(
            ['python3', str(script_path)],
            input=input_json,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return json.loads(result.stderr)

    def test_01_parse_valid_yaml(self):
        """Test 1: Parse valid YAML front matter"""
        content = """---
seq: 001
title: "Test Plan"
status: "draft:0"
priority: "p2:中:可纳入后续迭代计划"
created_at: ""
updated_at: ""
tags: []
---

# Test Plan

This is a test.
"""
        plan_path = self.create_test_plan('plan.001.test.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertTrue(result['success'])
        self.assertEqual(result['old_status'], 'draft:0')
        self.assertEqual(result['new_status'], 'ongoing:2')

    def test_02_status_transitions(self):
        """Test 2: Status transitions work correctly"""
        content = """---
seq: 002
title: "Status Test"
status: "draft:0"
---

# Status Test
"""
        plan_path = self.create_test_plan('plan.002.test.md', content)

        # Transition: draft → ongoing
        result = self.run_update_script(plan_path, 'start')
        self.assertEqual(result['new_status'], 'ongoing:2')

        # Transition: ongoing → completed
        result = self.run_update_script(plan_path, 'complete')
        self.assertEqual(result['old_status'], 'ongoing:2')
        self.assertEqual(result['new_status'], 'completed:3')

    def test_03_created_at_set_once(self):
        """Test 3: created_at set only on first execution"""
        content = """---
seq: 003
title: "Timestamp Test"
status: "draft:0"
created_at: ""
updated_at: ""
---

# Timestamp Test
"""
        plan_path = self.create_test_plan('plan.003.test.md', content)

        # First execution
        result1 = self.run_update_script(plan_path, 'start')
        created_at_1 = result1['created_at']
        updated_at_1 = result1['updated_at']

        self.assertNotEqual(created_at_1, '')
        self.assertNotEqual(updated_at_1, '')

        # Wait a moment
        time.sleep(1)

        # Second execution
        result2 = self.run_update_script(plan_path, 'complete')
        created_at_2 = result2['created_at']
        updated_at_2 = result2['updated_at']

        # created_at should not change
        self.assertEqual(created_at_1, created_at_2)

        # updated_at should change
        self.assertNotEqual(updated_at_1, updated_at_2)

    def test_04_updated_at_always_updates(self):
        """Test 4: updated_at updates on every execution"""
        content = """---
seq: 004
title: "Update Test"
status: "draft:0"
created_at: "2026-01-01 10:00:00"
updated_at: "2026-01-01 10:00:00"
---

# Update Test
"""
        plan_path = self.create_test_plan('plan.004.test.md', content)

        time.sleep(1)

        result = self.run_update_script(plan_path, 'start')

        # updated_at should be newer than the original
        self.assertNotEqual(result['updated_at'], '2026-01-01 10:00:00')

    def test_05_merge_tags(self):
        """Test 5: Merge tags without overwriting other fields"""
        content = """---
seq: 005
title: "Tag Test"
status: "draft:0"
tags: []
---

# Tag Test
"""
        plan_path = self.create_test_plan('plan.005.test.md', content)

        result = self.run_update_script(plan_path, 'start', tags=['feature', 'backend'])

        self.assertTrue(result['success'])
        self.assertIn('feature', result['tags'])
        self.assertIn('backend', result['tags'])

    def test_06_handle_missing_fields(self):
        """Test 6: Handle missing fields gracefully"""
        content = """---
seq: 006
title: "Minimal Plan"
---

# Minimal Plan
"""
        plan_path = self.create_test_plan('plan.006.test.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertTrue(result['success'])
        self.assertEqual(result['new_status'], 'ongoing:2')
        self.assertNotEqual(result['created_at'], '')

    def test_07_malformed_yaml_error(self):
        """Test 7: Handle malformed YAML with clear error"""
        content = """---
seq: 007
title: "Missing quote
status: draft:0
---

# Bad YAML
"""
        plan_path = self.create_test_plan('plan.007.test.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('YAML', result['error'])

    def test_08_preserve_markdown_body(self):
        """Test 8: Preserve Markdown body unchanged"""
        original_body = """
# Test Plan

## 🎯 Goal
Do something important

## 📋 Requirements
- Requirement 1
- Requirement 2

## ✅ Verification
- [ ] Test 1
- [ ] Test 2
"""

        content = f"""---
seq: 008
title: "Body Preservation Test"
status: "draft:0"
---
{original_body}"""

        plan_path = self.create_test_plan('plan.008.test.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertTrue(result['success'])

        # Read file and check body
        updated_content = plan_path.read_text(encoding='utf-8')
        self.assertIn('## 🎯 Goal', updated_content)
        self.assertIn('Do something important', updated_content)
        self.assertIn('- Requirement 1', updated_content)
        self.assertIn('- [ ] Test 1', updated_content)

    def test_09_backwards_compatibility(self):
        """Test 10: Backwards compatibility with old status format"""
        content = """---
seq: 010
title: "Old Format Test"
status: pending
priority: medium
created: 2026-01-01 10:00:00
updated: 2026-01-01 10:00:00
---

# Old Format Test
"""
        plan_path = self.create_test_plan('plan.010.test.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertTrue(result['success'])
        # Old 'pending' should convert to 'draft:0' first, then to 'ongoing:2'
        self.assertEqual(result['new_status'], 'ongoing:2')

    def test_10_missing_yaml_error(self):
        """Test: Handle missing YAML front matter"""
        content = """# No YAML Plan

This plan has no YAML front matter.
"""
        plan_path = self.create_test_plan('plan.999.no-yaml.md', content)

        result = self.run_update_script(plan_path, 'start')

        self.assertFalse(result['success'])
        self.assertIn('No YAML front matter', result['error'])


def run_tests():
    """Run all tests and report results"""
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPlanMetadataUpdater)

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
