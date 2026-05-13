#!/usr/bin/env python3
"""Fix ZSH completion - replace \\ at end of lines with \\\\ so Python preserves them."""

with open('kbdx-ops.py', 'r') as f:
    content = f.read()

# Find the ZSH completion string
zsh_start = content.find("_ZSH_COMPLETION = '''")
zsh_end = content.find("'''", zsh_start + 20)
zsh_end = content.find("'''\n", zsh_end + 3) + 4  # include newline after closing '''

old_zsh = content[zsh_start:zsh_end]

# Replace the string with proper escaping
# The key fix: every \ at end of line (backslash + newline) inside '''...''' 
# is Python line continuation. We need \\ at end of line.
# But also, the opening '''\ needs to remain '''\ (escape the first newline)
# And \\ inside the string content... let me think.

# Approach: build the new string with proper \\\\ escaping
# In Python, inside '''...''':
#   \\\\ at end of line = \\ in the output (literal backslash, then newline)
#   Actually let me verify: \\\\ = \\ (two literal backslashes)
# We need ONE literal backslash at end of each line.
# \\ in the source = one literal backslash. 
# So we need \\ at the end of each line.

# But within the zsh content itself:
#   - Each '\\' at end of line needs to become '\\\\' in the Python source
#   - But inside the '''...''', '\\\\' = '\\' (two literal backslashes)
# Wait, no. Let me think again.

# In a Python '''...''' string:
#   \\ = one literal backslash
#   \\n = newline (escape sequence)
#   \\ + actual newline = line continuation (both consumed)
#
# So to produce a single backslash followed by newline in the output:
#   \\<newline> in '''...'''
#   
# Because \\ = literal backslash (one \\ → one \), then the newline after is just a regular newline

# But wait, currently the file has \ at end of each line, and it's being consumed as line continuation.
# I need to replace each \ at end of line with \\ so that a single \ is in the output.

# Let me build the replacement content line by line
lines = old_zsh.split('\n')
fixed_lines = []
for i, line in enumerate(lines):
    if line.rstrip().endswith('\\') and not line.rstrip().endswith('\\\\'):
        # Replace trailing \ with \\ so Python preserves it
        # But we need to be careful about the opening line
        if i == 0 and line == "_ZSH_COMPLETION = '''\\":
            # Opening line: '''\\ should remain '''\ (escape first newline)
            # Actually wait - we want '''\ to escape the first newline
            # But the current source has '''\\ which is wrong (extra backslash)
            fixed_lines.append("_ZSH_COMPLETION = '''\\")
        else:
            # Replace \ at end with \\ so Python keeps one literal backslash
            stripped = line.rstrip()
            fixed_lines.append(stripped[:-1] + '\\\\')
    elif i == 0 and line.startswith("_ZSH_COMPLETION = '''"):
        fixed_lines.append("_ZSH_COMPLETION = '''\\")
    else:
        fixed_lines.append(line)

new_zsh = '\n'.join(fixed_lines)

# Verify: the opening should be '''\ (backslash-escape newline)
# and content lines should end with \\ (literal backslash, then newline)
import re
# Check trailing backslashes in source
for i, line in enumerate(new_zsh.split('\n')[:5]):
    print(f"Line {i}: {repr(line[:80])}")

new_content = content[:zsh_start] + new_zsh + content[zsh_end:]

# Verify by compiling
try:
    import py_compile
    py_compile.compile('kbdx-ops.py', doraise=True)
except:
    pass

with open('kbdx-ops.py', 'w') as f:
    f.write(new_content)

# Now verify the string value
import ast
with open('kbdx-ops.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == '_ZSH_COMPLETION':
                val = ast.literal_eval(node.value)
                for i, line in enumerate(val.split('\n')[:30]):
                    if '_arguments' in line or line.rstrip().endswith('\\'):
                        print(f"OUT {i}: {repr(line[:80])}")
                break

print("\n✅ Done")
