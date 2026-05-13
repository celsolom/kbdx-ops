#!/usr/bin/env python3
"""Replace the ZSH completion with a properly formatted version."""

with open('kbdx-ops.py', 'r') as f:
    content = f.read()

# Find the ZSH completion section
zsh_start = content.find("_ZSH_COMPLETION = '''")
zsh_end = content.find("'''", content.find("'''", zsh_start + 20) + 3)
zsh_end = zsh_end + 3  # include the closing '''

# Build new ZSH completion as a simple heredoc-style string
new_zsh = """_ZSH_COMPLETION = '''\\
#compdef kbdx-ops

_kbdx_ops() {
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \\
        '--version[Show version]' \\
        '--help[Show help]' \\
        '1: :->cmds' \\
        '*: :->args' && return

    case $state in
        cmds)
            _describe 'command' '(
                "merge:Merge entries from src into dest, skipping duplicates"
                "diff:Show differences between two databases"
                "dedup:Find and remove duplicate entries within a database"
                "completions:Generate shell completion scripts"
            )'
            ;;
        args)
            case $words[1] in
                merge)
                    _arguments \\
                        '--apply[Actually save changes]' \\
                        '--similar[Detect near-duplicate entries]' \\
                        '--similarity-threshold=[Similarity threshold (0-1)]' \\
                        '--interactive[Review each similar entry one by one]' \\
                        '-i[Review each similar entry one by one]' \\
                        '--no-pager[Print report to stdout]' \\
                        '--auto-skip-similar[Skip all similar entries automatically]' \\
                        '--min-score=[Minimum score filter]' \\
                        '--max-score=[Maximum score filter]' \\
                        '--dest-password=[Destination database password]' \\
                        '--src-password=[Source database password]' \\
                        '--dest-keyfile=[Destination key file]:file:_files' \\
                        '--src-keyfile=[Source key file]:file:_files' \\
                        '*:kdbx file:_files -g "*.kdbx"'
                    ;;
                diff)
                    _arguments \\
                        '-o[Output kdbx file]:output:_files' \\
                        '--output=[Output kdbx file]:output:_files' \\
                        '--apply[Actually create the output file]' \\
                        '--similarity-threshold=[Threshold for pairing entries (0-1)]' \\
                        '--no-pager[Print report to stdout]' \\
                        '--min-score=[Minimum score filter]' \\
                        '--max-score=[Maximum score filter]' \\
                        '--password-a=[Password for first database]' \\
                        '--password-b=[Password for second database]' \\
                        '--output-password=[Password for output database]' \\
                        '--keyfile-a=[Key file for first database]:file:_files' \\
                        '--keyfile-b=[Key file for second database]:file:_files' \\
                        '--output-keyfile=[Key file for output]:file:_files' \\
                        '*:kdbx file:_files -g "*.kdbx"'
                    ;;
                dedup)
                    _arguments \\
                        '--apply[Actually remove duplicates]' \\
                        '--interactive[Review groups one by one]' \\
                        '-i[Review groups one by one]' \\
                        '--similarity-threshold=[Threshold to consider duplicate (0-1)]' \\
                        '--min-score=[Minimum score filter]' \\
                        '--max-score=[Maximum score filter]' \\
                        '--no-pager[Print report to stdout]' \\
                        '--keep=[Which entry to keep when removing duplicates]:(first most-complete)' \\
                        '--password=[Database password]' \\
                        '--keyfile=[Key file]:file:_files' \\
                        '*:kdbx file:_files -g "*.kdbx"'
                    ;;
                completions)
                    _arguments '1:shell:(bash zsh)'
                    ;;
            esac
            ;;
    esac
} &&
compdef _kbdx_ops kbdx-ops
'''

"""

new_content = content[:zsh_start] + new_zsh + content[zsh_end:]

with open('kbdx-ops.py', 'w') as f:
    f.write(new_content)

print("Done")
