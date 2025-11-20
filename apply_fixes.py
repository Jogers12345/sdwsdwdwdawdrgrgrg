#!/usr/bin/env python3
"""Apply smart fixes to remaining critical files."""

import re
import os

def apply_bracket_fixes(file_path):
    """Fix common bracket and quote issues."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        original_content = content

        # Fix unmatched quotes in dictionaries and lists
        content = re.sub(r"""''''", "'", content)  # '''' -> '
        content = re.sub(r"}''", "}", content)  # }''' -> }
        content = re.sub(r"]''", "]", content)  # ]''' -> ]

        # Fix unmatched parentheses in function definitions
        content = re.sub(r'\)\s*\)\s*\)', ')', content)  # ))) -> )
        content = re.sub(r'\]\s*\]\s*\]', ']', content)  # ]]] -> ]
        content = re.sub(r'}\s*}\s*}', '}', content)   # }}} -> }

        # Fix unclosed parentheses in function calls
        content = re.sub(r'(\w+)\s*\(\s*[^)]*$', r'\1()', content, flags=re.MULTILINE)

        # Fix docstring issues
        content = content.replace('""""', '"""')  # """" -> """

        # Fix common quote issues in dictionaries
        content = re.sub(r""'\['''\s*,\s*'''""', "'", content)
        content = re.sub(r"""\],\s*''\]"", "]", content)
        content = re.sub(r"""},\s*''\}"", "}", content)

        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f'✅ Applied fixes to {file_path}')
            return True
        else:
            print(f'ℹ️  No fixes needed for {file_path}')
            return False

    except Exception as e:
        print(f'❌ Error fixing {file_path}: {e}')
        return False

# Files with bracket/quote issues
critical_files = [
    'bsee/caching/operation_cache.py',
    'bsee/config/validator.py',
    'bsee/cost/cost_model.py',
    'bsee/engine/pipeline.py',
    'bsee/engine/state.py',
    'bsee/metrics/metrics_registry.py'
]

if __name__ == '__main__':
    print('=== Applying Smart Bracket Fixes ===')
    fixed_count = 0
    for file_path in critical_files:
        if apply_bracket_fixes(file_path):
            fixed_count += 1

    print(f'\n✅ Applied fixes to {fixed_count}/{len(critical_files)} files')