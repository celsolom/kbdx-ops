#!/usr/bin/env python3
"""
KeePass operations: merge and diff .kdbx files.

Usage:
    kdbx_ops.py merge <dest_db> <src_db> [options]
    kdbx_ops.py diff <file_a> <file_b> [options]

Licensed under the Apache License, Version 2.0.
SPDX-License-Identifier: Apache-2.0
"""

__version__ = "1.0"

# ── Shell completion scripts ──────────────────────────────────────────
_BASH_COMPLETION = '''\
# kbdx-ops bash completion

_kbdx_ops_completions() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local cword=$COMP_CWORD
    local subcmd="${COMP_WORDS[1]}"

    local commands="merge diff completions dedup"
    local merge_opts="--apply --similar --similarity-threshold --interactive -i --no-pager --auto-skip-similar --min-score --max-score --dest-password --src-password --dest-keyfile --src-keyfile"
    local diff_opts="-o --output --apply --similarity-threshold --no-pager --min-score --max-score --password-a --password-b --output-password --keyfile-a --keyfile-b --output-keyfile"
    local dedup_opts="--apply --interactive -i --similarity-threshold --min-score --max-score --no-pager --keep --password --keyfile"

    # Top-level: subcommands
    if [[ -z "$subcmd" || $cword -eq 0 ]]; then
        COMPREPLY=($(compgen -W "$commands" -- "$cur"))
        return
    fi

    case "$subcmd" in
        merge|diff)
            # merge/diff: 2 .kdbx files + flags; para de oferecer arquivo após 2
            COMPREPLY=()
            local kdbx_count=0
            for w in "${COMP_WORDS[@]}"; do
                [[ "$w" == *.kdbx ]] && ((kdbx_count++))
            done
            if [[ $kdbx_count -lt 2 ]]; then
                COMPREPLY+=($(compgen -f -X '!*.kdbx' -- "$cur"))
            fi
            local opts="$merge_opts"
            [[ "$subcmd" == "diff" ]] && opts="$diff_opts"
            COMPREPLY+=($(compgen -W "$opts" -- "$cur"))
            ;;
        dedup)
            # dedup: 1 .kdbx file + flags; para de oferecer arquivo após 1
            COMPREPLY=()
            local has_kdbx=""
            for w in "${COMP_WORDS[@]}"; do
                [[ "$w" == *.kdbx ]] && has_kdbx=1
            done
            if [[ -z "$has_kdbx" ]]; then
                COMPREPLY+=($(compgen -f -X '!*.kdbx' -- "$cur"))
            fi
            COMPREPLY+=($(compgen -W "$dedup_opts" -- "$cur"))
            ;;
        completions)
            COMPREPLY=($(compgen -W "bash zsh" -- "$cur"))
            ;;
        *)
            # Unknown subcommand: show all subcommands anyway
            COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            ;;
    esac
} &&
complete -F _kbdx_ops_completions kbdx-ops
'''

_ZSH_COMPLETION = '''\
#compdef kbdx-ops

_kbdx_ops() {
    local curcontext="$curcontext" state line
    typeset -A opt_args

    _arguments -C \\
        '--version[Show version]' \\
        '--help[Show help]' \\
        '1: :->cmds' \\
        '*: :->args'

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
            local subcmd="${words[2]}"
            case "$subcmd" in
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
                        '1:dest kdbx:_files -g "*.kdbx"' \\
                        '2:src kdbx:_files -g "*.kdbx"'
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
                        '--output-keyfile=[Key file for output database]:file:_files' \\
                        '1:file a:_files -g "*.kdbx"' \\
                        '2:file b:_files -g "*.kdbx"'
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
                        '1:database:_files -g "*.kdbx"'
                    ;;
                completions)
                    _arguments '1:shell:(bash zsh)'
                    ;;
                *)
                    # Subcommand ainda nao digitado: completar com nomes dos comandos
                    _describe 'command' '(
                        "merge:Merge entries from src into dest"
                        "diff:Show differences between two databases"
                        "dedup:Find and remove duplicates within a database"
                        "completions:Generate shell completion scripts"
                    )'
                    ;;
            esac
            ;;
    esac
} &&
compdef _kbdx_ops kbdx-ops
'''

import argparse
import sys
import os
import subprocess
import getpass
import signal
import atexit
import shutil
from pathlib import Path
from difflib import SequenceMatcher
from contextlib import contextmanager

try:
    from pykeepass import PyKeePass
    from pykeepass.exceptions import CredentialsError
except ImportError:
    print("ERROR: pykeepass is required. Install with: pip install pykeepass", file=sys.stderr)
    sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
#  Terminal raw mode management
# ═══════════════════════════════════════════════════════════════════════════════

_TERMIOS_SAVED = None
_TERMIOS_FD = None

def _save_terminal_state():
    global _TERMIOS_SAVED, _TERMIOS_FD
    if not sys.stdin.isatty():
        return
    try:
        import termios
        _TERMIOS_FD = sys.stdin.fileno()
        _TERMIOS_SAVED = termios.tcgetattr(_TERMIOS_FD)
    except Exception:
        pass

def _restore_terminal():
    if _TERMIOS_SAVED is None or _TERMIOS_FD is None:
        return
    try:
        import termios
        termios.tcsetattr(_TERMIOS_FD, termios.TCSADRAIN, _TERMIOS_SAVED)
    except Exception:
        pass

_save_terminal_state()
atexit.register(_restore_terminal)

def _sigtstp_handler(signum, frame):
    _restore_terminal()
    signal.signal(signal.SIGTSTP, signal.SIG_DFL)
    os.kill(os.getpid(), signal.SIGTSTP)

signal.signal(signal.SIGTSTP, _sigtstp_handler)

def _sigint_handler(signum, frame):
    _restore_terminal()
    print("\n\n  Operação cancelada pelo usuário (Ctrl+C).")
    sys.exit(130)

signal.signal(signal.SIGINT, _sigint_handler)

@contextmanager
def raw_terminal():
    if not sys.stdin.isatty():
        yield
        return
    import tty
    import termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        yield
    finally:
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        except Exception:
            pass

def getch() -> str:
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read(1).lower()
        except Exception:
            return ""
    with raw_terminal():
        ch = sys.stdin.read(1)
    if not ch:
        return ""
    return ch.lower()

def prompt_key(options: dict) -> str:
    labels = "  [ " + "  |  ".join(f"{k}={v}" for k, v in options.items()) + "  ]"
    print(labels, flush=True)
    while True:
        ch = getch()
        if ch in options:
            print(flush=True)
            return ch
        if ch == "\x03":
            print("\n\n  Operação cancelada pelo usuário (Ctrl+C).", flush=True)
            _restore_terminal()
            sys.exit(130)
        display = ch if ch.isprintable() else f"0x{ord(ch):02x}"
        print(f"\r  Tecla inválida: '{display}'  ", end="", flush=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  Assinatura / comparação de entradas
# ═══════════════════════════════════════════════════════════════════════════════

SENSITIVE_FIELDS = {"password"}

def entry_signature(entry) -> dict:
    sig = {
        "title": (entry.title or "").strip(),
        "username": (entry.username or "").strip(),
        "password": (entry.password or "").strip(),
        "url": (entry.url or "").strip(),
        "notes": (entry.notes or "").strip(),
    }
    custom = {}
    for key in entry.custom_properties:
        val = (entry.get_custom_property(key) or "").strip()
        if val:
            custom[key] = val
    sig["custom"] = custom
    return sig

def is_exact_duplicate(src_sig: dict, dest_sig: dict) -> bool:
    for field in ("title", "username", "password", "url", "notes"):
        src_val = src_sig[field]
        if not src_val:
            continue
        if src_val != dest_sig[field]:
            return False
    src_custom = src_sig["custom"]
    if src_custom:
        dest_custom = dest_sig["custom"]
        for key, val in src_custom.items():
            if dest_custom.get(key) != val:
                return False
    return True

def fuzzy_match(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def compute_field_scores(src_sig: dict, dest_sig: dict) -> dict:
    scores = {}
    for field in ("title", "username", "password", "url", "notes"):
        scores[field] = (
            fuzzy_match(src_sig[field], dest_sig[field]),
            src_sig[field],
            dest_sig[field],
        )
    src_custom = src_sig["custom"]
    dest_custom = dest_sig["custom"]
    all_keys = set(src_custom) | set(dest_custom)
    if all_keys:
        matches = sum(1 for k in all_keys if src_custom.get(k) == dest_custom.get(k))
        custom_score = matches / len(all_keys)
    else:
        custom_score = 1.0
    scores["custom"] = (custom_score, src_custom, dest_custom)
    return scores

def compute_overall_similarity(field_scores: dict) -> float:
    weights = {
        "title": 4, "username": 3, "url": 2,
        "password": 2, "notes": 1, "custom": 2,
    }
    total_weight = 0
    weighted_sum = 0.0
    for field, weight in weights.items():
        score, src_val, dest_val = field_scores[field]
        if field != "custom" and not src_val and not dest_val:
            continue
        total_weight += weight
        weighted_sum += weight * score
    if total_weight == 0:
        return 0.0
    return weighted_sum / total_weight

def find_best_match(src_sig: dict, dest_entries: list, dest_sigs: list,
                    threshold: float = 0.5) -> tuple:
    """Find the best matching dest entry for a given src signature.
    Returns (best_dest_entry, best_dest_sig, best_score, best_field_scores)
    or (None, None, 0, None) if no match above threshold."""
    best_sim = 0.0
    best_idx = -1
    best_field_scores = None

    for i, dest_sig in enumerate(dest_sigs):
        field_scores = compute_field_scores(src_sig, dest_sig)
        score = compute_overall_similarity(field_scores)
        if score > best_sim:
            best_sim = score
            best_idx = i
            best_field_scores = field_scores

    if best_idx >= 0 and best_sim >= threshold:
        return (dest_entries[best_idx], dest_sigs[best_idx],
                best_sim, best_field_scores)
    return (None, None, 0.0, None)

# ═══════════════════════════════════════════════════════════════════════════════
#  Formatação
# ═══════════════════════════════════════════════════════════════════════════════

FIELD_LABELS = {
    "title": "Title", "username": "Username", "password": "Password",
    "url": "URL", "notes": "Notes", "custom": "Custom Fields",
}
FIELD_ICONS = {
    "title": "📄", "username": "👤", "password": "🔑",
    "url": "🔗", "notes": "📝", "custom": "🏷️",
}

def format_value(val, field: str, width: int = 42) -> str:
    if field in SENSITIVE_FIELDS:
        return "•••••••• (oculto)" if val else "(vazio)"
    if not val:
        return "(vazio)"
    if len(val) > width:
        val = val[: width - 3] + "..."
    return val

def format_custom_short(custom_dict: dict, max_items: int = 5) -> str:
    if not custom_dict:
        return "(vazio)"
    items = []
    for k, v in list(custom_dict.items())[:max_items]:
        items.append(f"{k}={v}")
    if len(custom_dict) > max_items:
        items.append(f"...(+{len(custom_dict) - max_items})")
    return ", ".join(items)

def score_bar(score: float, width: int = 10) -> str:
    filled = round(score * width)
    return "█" * filled + "░" * (width - filled)

def format_single_entry_detail(field_scores: dict, overall: float,
                                group_path: str, idx: int = 0,
                                total: int = 0, label: str = "") -> str:
    lines = []
    lines.append("─" * 78)
    tag = f"  {label}" if label else ""
    num = f"#{idx}" if idx else ""
    progress = f"  ({idx}/{total})" if idx and total else ""
    lines.append(f"  {num}{tag} Similaridade: {overall:.0%}{progress}  |  /{group_path}")
    lines.append("")
    lines.append(f"  {'Campo':<14} {'Score':<14} {'Fonte A':<30} {'Fonte B':<30}")
    lines.append(f"  {'─'*13:<14} {'─'*13:<14} {'─'*29:<30} {'─'*29:<30}")

    for field in ("title", "username", "password", "url", "notes", "custom"):
        score, src_val, dest_val = field_scores[field]
        icon = FIELD_ICONS.get(field, "•")
        lbl = FIELD_LABELS.get(field, field)
        bar = score_bar(score)
        pct = f"{score:.0%}"

        if field == "custom":
            src_str = format_custom_short(src_val if src_val else {})
            dest_str = format_custom_short(dest_val if dest_val else {})
        else:
            src_str = format_value(src_val, field)
            dest_str = format_value(dest_val, field)

        lines.append(f"  {icon} {lbl:<11} {bar} {pct:<3}  {src_str:<30} {dest_str:<30}")

    lines.append("")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════════════
#  Grupos
# ═══════════════════════════════════════════════════════════════════════════════

def get_entry_group_path(entry) -> str:
    parts = []
    g = entry.group
    while g is not None and not g.is_root_group:
        parts.append(g.name)
        g = g.group
    parts.reverse()
    return "/".join(parts)

def resolve_or_create_group(kp, group_path: str):
    if not group_path:
        return kp.root_group
    parts = group_path.split("/")
    current = kp.root_group
    for part in parts:
        child = kp.find_groups(name=part, group=current, first=True)
        if child is None:
            child = kp.add_group(current, part)
        current = child
    return current

# ═══════════════════════════════════════════════════════════════════════════════
#  Utilitários de banco
# ═══════════════════════════════════════════════════════════════════════════════

def open_db(path: Path, label: str, password: str = None, keyfile: Path = None):
    """Open a KeePass database, prompting for password if needed."""
    pw = password or getpass.getpass(f"{label} password for {path.name}: ")
    try:
        kp = PyKeePass(str(path.resolve()), password=pw, keyfile=keyfile)
        print(f"  ✅ Banco aberto: {path.name}")
        return kp
    except CredentialsError:
        print(f"ERROR: Wrong password or key file for {path.name}.", file=sys.stderr)
        sys.exit(1)

def copy_entry(src_entry, dest_kp, group_path: str):
    """Copy a pykeepass entry from src to dest_kp. Returns the new entry."""
    dest_group = resolve_or_create_group(dest_kp, group_path)
    new_entry = dest_kp.add_entry(
        destination_group=dest_group,
        title=src_entry.title,
        username=src_entry.username,
        password=src_entry.password,
        url=src_entry.url,
        notes=src_entry.notes,
    )
    for key in src_entry.custom_properties:
        val = src_entry.get_custom_property(key)
        if val is not None:
            new_entry.set_custom_property(key, val)
    return new_entry

# ═══════════════════════════════════════════════════════════════════════════════
#  Pager
# ═══════════════════════════════════════════════════════════════════════════════

def display_via_pager(text: str, no_pager: bool = False) -> None:
    if no_pager or not sys.stdout.isatty():
        print(text)
        return
    pager = os.environ.get("PAGER", "")
    if not pager:
        for cmd in ("less", "more", "most"):
            if subprocess.run(["which", cmd], capture_output=True).returncode == 0:
                pager = cmd
                break
    if not pager:
        pager = "less -R"
    try:
        p = subprocess.Popen(pager, shell=True, stdin=subprocess.PIPE, text=True)
        p.communicate(input=text)
    except OSError:
        print(text)

# ═══════════════════════════════════════════════════════════════════════════════
#  Parser de argumentos
# ═══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="KeePass operations: merge and diff .kdbx files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--version", action="version", version=f"kbdx-ops {__version__}",
        help="Show version and exit",
    )
    sub = p.add_subparsers(dest="command", required=True, title="Commands")

    # ── merge ──────────────────────────────────────────────────────────
    m = sub.add_parser("merge", help="Merge entries from src into dest, skipping duplicates",
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        epilog="""
Examples:
  kdbx_ops.py merge pessoal.kdbx protonpass.kdbx              # preview
  kdbx_ops.py merge pessoal.kdbx protonpass.kdbx --apply      # salva
  kdbx_ops.py merge pessoal.kdbx protonpass.kdbx --similar --interactive
""")
    m.add_argument("dest_db", type=Path, help="Destination KeePass database")
    m.add_argument("src_db", type=Path, help="Source KeePass database")
    m.add_argument("--dest-password", help="Password for destination DB")
    m.add_argument("--src-password", help="Password for source DB")
    m.add_argument("--dest-keyfile", type=Path, default=None)
    m.add_argument("--src-keyfile", type=Path, default=None)
    m.add_argument("--apply", action="store_true",
                   help="REALMENTE salva as alterações (padrão é preview)")
    m.add_argument("--similar", action="store_true",
                   help="Detecta entradas similares para revisão")
    m.add_argument("--similarity-threshold", type=float, default=0.5, metavar="0-1",
                   help="Similaridade mínima para considerar como similar (padrão: 0.5)")
    m.add_argument("--interactive", "-i", action="store_true",
                   help="Revisa cada similar uma a uma (requer --similar)")
    m.add_argument("--no-pager", action="store_true",
                   help="Imprime relatório sem pager")
    m.add_argument("--auto-skip-similar", action="store_true",
                   help="Pula todas as similares automaticamente")
    m.add_argument("--min-score", type=float, default=0.0, metavar="0-1",
                   help="Filtro: só mostra similares com score >= N")
    m.add_argument("--max-score", type=float, default=1.0, metavar="0-1",
                   help="Filtro: só mostra similares com score <= N")

    # ── diff ───────────────────────────────────────────────────────────
    d = sub.add_parser("diff", help="Show differences between two databases and optionally create a diff file",
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        epilog="""
Examples:
  kdbx_ops.py diff pessoal.kdbx protonpass.kdbx                        # report
  kdbx_ops.py diff pessoal.kdbx protonpass.kdbx -o diff.kdbx           # cria arquivo
  kdbx_ops.py diff pessoal.kdbx protonpass.kdbx -o diff.kdbx --apply   # salva
""")
    d.add_argument("file_a", type=Path, help="First KeePass database")
    d.add_argument("file_b", type=Path, help="Second KeePass database")
    d.add_argument("-o", "--output", type=Path, default=None,
                   help="Output .kdbx with diff entries")
    d.add_argument("--password-a", help="Password for file_a")
    d.add_argument("--password-b", help="Password for file_b")
    d.add_argument("--output-password", help="Password for output file")
    d.add_argument("--keyfile-a", type=Path, default=None)
    d.add_argument("--keyfile-b", type=Path, default=None)
    d.add_argument("--output-keyfile", type=Path, default=None)
    d.add_argument("--apply", action="store_true",
                   help="Cria o arquivo de diff (--output é obrigatório)")
    d.add_argument("--similarity-threshold", type=float, default=0.5, metavar="0-1",
                   help="Threshold para considerar como mesmo par (padrão: 0.5)")
    d.add_argument("--no-pager", action="store_true",
                   help="Imprime relatório sem pager")
    d.add_argument("--min-score", type=float, default=0.0, metavar="0-1",
                   help="Filtro: só mostra divergências com score >= N")
    d.add_argument("--max-score", type=float, default=1.0, metavar="0-1",
                   help="Filtro: só mostra divergências com score <= N")

    # ── completions ────────────────────────────────────────────────────
    c = sub.add_parser("completions", help="Generate shell completion scripts",
                        formatter_class=argparse.RawDescriptionHelpFormatter,
                        epilog="""
Examples:
  kbdx-ops completions bash    # print bash completions
  kbdx-ops completions zsh     # print zsh completions
  kbdx-ops completions bash > /etc/bash_completion.d/kbdx-ops
  kbdx-ops completions zsh > /usr/share/zsh/site-functions/_kbdx-ops
""")
    c.add_argument("shell", choices=["bash", "zsh"],
                    help="Shell to generate completions for")

    # ── dedup ──────────────────────────────────────────────────────────
    dp = sub.add_parser("dedup", help="Find and remove duplicate entries within a database",
                         formatter_class=argparse.RawDescriptionHelpFormatter,
                         epilog="""
Examples:
  kbdx-ops dedup pessoal.kdbx                              # preview
  kbdx-ops dedup pessoal.kdbx --apply                      # remove duplicatas
  kbdx-ops dedup pessoal.kdbx --interactive                # decide uma a uma
  kbdx-ops dedup pessoal.kdbx --similarity-threshold 0.8   # só duplicatas exatas
""")
    dp.add_argument("database", type=Path, help="KeePass database")
    dp.add_argument("--password", help="Database password")
    dp.add_argument("--keyfile", type=Path, default=None)
    dp.add_argument("--apply", action="store_true",
                    help="REALMENTE remove duplicatas (padrão é preview)")
    dp.add_argument("--interactive", "-i", action="store_true",
                    help="Revisar cada grupo de duplicatas")
    dp.add_argument("--similarity-threshold", type=float, default=0.8, metavar="0-1",
                    help="Similaridade para considerar duplicata (padrão: 0.8)")
    dp.add_argument("--min-score", type=float, default=0.0, metavar="0-1",
                    help="Filtro: só mostra grupos com score >= N")
    dp.add_argument("--max-score", type=float, default=1.0, metavar="0-1",
                    help="Filtro: só mostra grupos com score <= N")
    dp.add_argument("--no-pager", action="store_true",
                    help="Imprime relatório sem pager")
    dp.add_argument("--keep", choices=["first", "most-complete"], default="most-complete",
                    help="Critério para manter qual entrada (padrão: most-complete)")

    return p

# ═══════════════════════════════════════════════════════════════════════════════
#  COMANDO: MERGE
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_merge(args: argparse.Namespace) -> None:
    dry_run = not args.apply
    if dry_run:
        print("\n  ⚠  MODO PREVIEW — nada será alterado. Use --apply para salvar.\n")

    dest_kp = open_db(args.dest_db, "Destino", args.dest_password, args.dest_keyfile)
    src_kp = open_db(args.src_db, "Fonte", args.src_password, args.src_keyfile)

    dest_entries = dest_kp.entries
    precompute_dest = [entry_signature(e) for e in dest_entries]

    added = 0
    skipped_exact = 0
    similar_list = []

    for src_entry in src_kp.entries:
        src_sig = entry_signature(src_entry)
        group_path = get_entry_group_path(src_entry)

        is_exact = any(is_exact_duplicate(src_sig, ds) for ds in precompute_dest)
        if is_exact:
            skipped_exact += 1
            continue

        result = find_best_match(src_sig, dest_entries, precompute_dest,
                                  args.similarity_threshold)
        best_entry, best_sig, best_sim, best_fs = result

        if args.similar and best_sim >= args.similarity_threshold:
            if not (args.min_score <= best_sim <= args.max_score):
                continue
            similar_list.append({
                "src_entry": src_entry,
                "src_sig": src_sig,
                "dest_sig": best_sig,
                "field_scores": best_fs,
                "overall": best_sim,
                "group_path": group_path,
            })
            continue

        copy_entry(src_entry, dest_kp, group_path)
        title = src_sig["title"] or "(no title)"
        username = src_sig["username"]
        extra = f" [{username}]" if username else ""
        print(f"  {'⚡ ADICIONARIA' if dry_run else '✅ ADICIONADA'}:  {title}{extra}  ─>  /{group_path}")
        added += 1

    # ── Tratar similares ────────────────────────────────────────────────
    similar_added = 0
    similar_skipped = 0

    if similar_list and args.similar:
        if args.interactive:
            idx = 0
            while idx < len(similar_list):
                item = similar_list[idx]
                se = item["src_entry"]
                fs = item["field_scores"]
                ds = item["dest_sig"]

                print(flush=True)
                print(format_single_entry_detail(fs, item["overall"],
                      item["group_path"], idx + 1, len(similar_list)), flush=True)
                key = prompt_key({
                    "a": "adicionar", "s": "pular", "b": "voltar", "q": "sair",
                })
                act = {"a": "add", "s": "skip", "b": "back", "q": "quit"}.get(key, "skip")

                if act == "add":
                    copy_entry(se, dest_kp, item["group_path"])
                    similar_added += 1
                    idx += 1
                elif act == "skip":
                    print(f"  ⏭  PULADA: {se.title or '(no title)'}")
                    similar_skipped += 1
                    idx += 1
                elif act == "back":
                    if idx > 0:
                        idx -= 1
                        print(f"  ↩  Voltando para #{idx + 1}...")
                    else:
                        print("  ⚠  Já está na primeira.")
                elif act == "quit":
                    print("  Merge abortado.")
                    similar_skipped += len(similar_list) - idx
                    break
        elif args.auto_skip_similar:
            similar_skipped = len(similar_list)
            print(f"  ⏭  Pulando automaticamente {similar_skipped} similar(es).")
        else:
            report_lines = [format_single_entry_detail(
                item["field_scores"], item["overall"], item["group_path"],
                idx + 1, len(similar_list))
                for idx, item in enumerate(similar_list)]
            report = "\n".join(report_lines)
            print()
            print("📋  ENTRADAS SIMILARES:")
            display_via_pager(report, args.no_pager)
            print()
            print(f"  📊  {len(similar_list)} similar(es).")
            print()
            act = prompt_key({
                "s": "pular todas", "a": "adicionar todas",
                "i": "revisar uma a uma", "q": "sair",
            })

            if act == "a":
                for item in similar_list:
                    copy_entry(item["src_entry"], dest_kp, item["group_path"])
                    similar_added += 1
            elif act == "i":
                idx = 0
                while idx < len(similar_list):
                    item = similar_list[idx]
                    se = item["src_entry"]
                    fs = item["field_scores"]
                    print(flush=True)
                    print(format_single_entry_detail(fs, item["overall"],
                          item["group_path"], idx + 1, len(similar_list)), flush=True)
                    key = prompt_key({
                        "a": "adicionar", "s": "pular", "b": "voltar", "q": "sair",
                    })
                    act2 = {"a": "add", "s": "skip", "b": "back", "q": "quit"}.get(key, "skip")

                    if act2 == "add":
                        copy_entry(se, dest_kp, item["group_path"])
                        similar_added += 1
                        idx += 1
                    elif act2 == "skip":
                        print(f"  ⏭  PULADA: {se.title or '(no title)'}")
                        similar_skipped += 1
                        idx += 1
                    elif act2 == "back":
                        if idx > 0:
                            idx -= 1
                            print(f"  ↩  Voltando para #{idx + 1}...")
                        else:
                            print("  ⚠  Já está na primeira.")
                    elif act2 == "quit":
                        print("  Merge abortado.")
                        similar_skipped += len(similar_list) - idx
                        break
            elif act == "q":
                print("  Merge abortado.")
                similar_skipped = len(similar_list)
            else:
                similar_skipped = len(similar_list)

        added += similar_added

    # ── Sumário ─────────────────────────────────────────────────────────
    print()
    print("═" * 60)
    print(f"  Destino:  {args.dest_db.name}")
    print(f"  Fonte:    {args.src_db.name}")
    print(f"  Entradas fonte: {len(src_kp.entries)}")
    print(f"  Adicionadas:    {added}")
    print(f"  Puladas exatas: {skipped_exact}")
    if args.similar:
        print(f"  Similares:      {len(similar_list)}")
        print(f"    ├ adicionadas: {similar_added}")
        print(f"    └ puladas:     {similar_skipped}")
    print(f"  Modo: {'PREVIEW' if dry_run else 'APLICANDO'}")
    print("═" * 60)

    if not dry_run and added > 0:
        dest_kp.save()
        print("  ✅ Salvo com sucesso.")
    elif dry_run and added > 0:
        print(f"  ⚠  Preview. Use --apply para salvar {added} adição(ões).")
    else:
        print("  Nada a fazer.")

# ═══════════════════════════════════════════════════════════════════════════════
#  COMANDO: DIFF
# ═══════════════════════════════════════════════════════════════════════════════

def cmd_diff(args: argparse.Namespace) -> None:
    """Show differences between two databases and optionally create diff file."""

    kp_a = open_db(args.file_a, "Arquivo A", args.password_a, args.keyfile_a)
    kp_b = open_db(args.file_b, "Arquivo B", args.password_b, args.keyfile_b)

    sigs_a = [entry_signature(e) for e in kp_a.entries]
    sigs_b = [entry_signature(e) for e in kp_b.entries]

    # Categorias
    only_in_a = []       # (entry, sig, group) - entries in A with no match in B
    only_in_b = []       # (entry, sig, group) - entries in B with no match in A
    modified = []        # (entry_a, sig_a, entry_b, sig_b, group, score, field_scores)

    matched_b = set()    # indices de B que já foram pareados

    # ── Para cada entrada em A, busca melhor correspondência em B ─────
    for i, entry_a in enumerate(kp_a.entries):
        sig_a = sigs_a[i]
        group_a = get_entry_group_path(entry_a)

        result = find_best_match(sig_a, kp_b.entries, sigs_b,
                                  args.similarity_threshold)
        best_entry, best_sig, best_sim, best_fs = result

        if best_sim >= args.similarity_threshold:
            if not (args.min_score <= best_sim <= args.max_score):
                only_in_a.append((entry_a, sig_a, group_a))
                continue

            # Acha o índice em B
            b_idx = next(j for j, e in enumerate(kp_b.entries)
                         if e.uuid == best_entry.uuid)
            matched_b.add(b_idx)

            if is_exact_duplicate(sig_a, best_sig):
                # Exatamente iguais → ignorar
                pass
            else:
                # Mesmo par mas diferente → modificado
                modified.append((
                    entry_a, sig_a, best_entry, best_sig,
                    group_a, best_sim, best_fs,
                ))
        else:
            if args.min_score <= 0.0 <= args.max_score:
                only_in_a.append((entry_a, sig_a, group_a))

    # ── Entradas em B sem correspondência em A ────────────────────────
    for j, entry_b in enumerate(kp_b.entries):
        if j not in matched_b:
            sig_b = sigs_b[j]
            group_b = get_entry_group_path(entry_b)
            only_in_b.append((entry_b, sig_b, group_b))

    # ── Exibir relatório ───────────────────────────────────────────────
    report_lines = []
    report_lines.append("╔════════════════════════════════════════════════════════════════════════╗")
    report_lines.append("║                   DIFF entre bancos KeePass                          ║")
    report_lines.append("╠════════════════════════════════════════════════════════════════════════╣")
    report_lines.append(f"║  A: {args.file_a.name:<52} ║")
    report_lines.append(f"║  B: {args.file_b.name:<52} ║")
    report_lines.append(f"║  Entradas A: {len(kp_a.entries):<5}   B: {len(kp_b.entries):<5}                        ║")
    report_lines.append("╚════════════════════════════════════════════════════════════════════════╝")
    report_lines.append("")

    if only_in_a:
        report_lines.append(f"  🔵  SOMENTE EM A ({len(only_in_a)} entradas):")
        report_lines.append("")
        for entry_a, sig_a, group_a in only_in_a:
            t = sig_a["title"] or "(no title)"
            u = sig_a["username"]
            extra = f" [{u}]" if u else ""
            report_lines.append(f"     • {t}{extra}  ─>  /{group_a}")
        report_lines.append("")

    if only_in_b:
        report_lines.append(f"  🟢  SOMENTE EM B ({len(only_in_b)} entradas):")
        report_lines.append("")
        for entry_b, sig_b, group_b in only_in_b:
            t = sig_b["title"] or "(no title)"
            u = sig_b["username"]
            extra = f" [{u}]" if u else ""
            report_lines.append(f"     • {t}{extra}  ─>  /{group_b}")
        report_lines.append("")

    if modified:
        report_lines.append(f"  🟡  MODIFICADAS ({len(modified)} entradas):")
        report_lines.append("")
        for idx, (entry_a, sig_a, entry_b, sig_b, group,
                  score, fs) in enumerate(modified, 1):
            report_lines.append(format_single_entry_detail(
                fs, score, group, idx, len(modified), "MODIFICADA"))
        report_lines.append("")

    total_diff = len(only_in_a) + len(only_in_b) + len(modified)
    report_lines.append("═" * 60)
    report_lines.append(f"  Resumo:")
    report_lines.append(f"    Total entradas A: {len(kp_a.entries)}")
    report_lines.append(f"    Total entradas B: {len(kp_b.entries)}")
    report_lines.append(f"    Somente em A:     {len(only_in_a)}")
    report_lines.append(f"    Somente em B:     {len(only_in_b)}")
    report_lines.append(f"    Modificadas:      {len(modified)}")
    report_lines.append(f"    Total divergentes: {total_diff}")
    report_lines.append("═" * 60)

    report = "\n".join(report_lines)
    display_via_pager(report, args.no_pager)

    # ── Salvar diff em novo .kdbx ──────────────────────────────────────
    if args.output:
        if not args.apply:
            print(f"\n  ⚠  Preview do diff. Use --apply para criar o arquivo {args.output.name}.")
            return

        out_pass = args.output_password or getpass.getpass(
            f"Password for output {args.output.name}: "
        )

        print(f"\n  📦  Criando arquivo diff: {args.output.name}")

        # Cria novo banco vazio
        out_kp = PyKeePass(str(args.output.resolve()), password=out_pass,
                           keyfile=args.output_keyfile)

        def add_with_group(entry, sig, prefix: str, group_path: str):
            """Add entry under a prefixed group structure."""
            full_path = f"{prefix}/{group_path}" if group_path else prefix
            g = resolve_or_create_group(out_kp, full_path)
            out_kp.add_entry(
                destination_group=g,
                title=entry.title,
                username=entry.username,
                password=entry.password,
                url=entry.url,
                notes=entry.notes,
            )
            # Copy custom properties
            new_e = out_kp.find_entries(title=entry.title, username=entry.username,
                                         group=g, first=True)
            if new_e:
                for key in entry.custom_properties:
                    val = entry.get_custom_property(key)
                    if val is not None:
                        new_e.set_custom_property(key, val)

        count = 0

        for entry_a, sig_a, group_a in only_in_a:
            add_with_group(entry_a, sig_a, "only_in_A", group_a)
            count += 1

        for entry_b, sig_b, group_b in only_in_b:
            add_with_group(entry_b, sig_b, "only_in_B", group_b)
            count += 1

        for idx, (entry_a, sig_a, entry_b, sig_b, group,
                  score, fs) in enumerate(modified):
            add_with_group(entry_a, sig_a, "modified_A", group)
            add_with_group(entry_b, sig_b, "modified_B", group)
            count += 2

        out_kp.save()
        print(f"  ✅ Arquivo criado: {args.output.resolve()} ({count} entradas)")

# ═══════════════════════════════════════════════════════════════════════════════
#  COMANDO: DEDUP
# ═══════════════════════════════════════════════════════════════════════════════

def _entry_completeness(sig: dict) -> int:
    """Score how complete an entry is (more filled fields = higher)."""
    score = 0
    for field in ("title", "username", "password", "url", "notes"):
        if sig[field]:
            score += 1
    if sig["custom"]:
        score += len(sig["custom"])
    return score

def _group_duplicates(entries, sigs, threshold: float) -> list:
    """Group entries into duplicate groups based on similarity.
    Returns list of groups, each group is a list of (entry, sig, idx)."""
    n = len(entries)
    visited = [False] * n
    groups = []

    for i in range(n):
        if visited[i]:
            continue
        group = [(entries[i], sigs[i], i)]
        visited[i] = True

        for j in range(i + 1, n):
            if visited[j]:
                continue
            field_scores = compute_field_scores(sigs[i], sigs[j])
            score = compute_overall_similarity(field_scores)
            if score >= threshold:
                group.append((entries[j], sigs[j], j))
                visited[j] = True

        if len(group) > 1:
            groups.append(group)

    return groups

def cmd_dedup(args: argparse.Namespace) -> None:
    """Find and remove duplicate entries within a database."""
    dry_run = not args.apply
    if dry_run:
        print("\n  ⚠  MODO PREVIEW — nada será removido. Use --apply para remover.\n")

    kp = open_db(args.database, "Database", args.password, args.keyfile)

    entries = kp.entries
    sigs = [entry_signature(e) for e in entries]

    print(f"  Total de entradas: {len(entries)}")

    # Agrupar duplicatas
    groups = _group_duplicates(entries, sigs, args.similarity_threshold)

    # Aplicar filtro de score (usar o score do par mais similar no grupo)
    filtered_groups = []
    for group in groups:
        # Score do grupo = maior similaridade entre qualquer par
        max_score = 0.0
        for a in range(len(group)):
            for b in range(a + 1, len(group)):
                fs = compute_field_scores(group[a][1], group[b][1])
                s = compute_overall_similarity(fs)
                if s > max_score:
                    max_score = s
        if args.min_score <= max_score <= args.max_score:
            filtered_groups.append((max_score, group))

    filtered_groups.sort(key=lambda x: -x[0])  # do mais similar ao menos

    if not filtered_groups:
        print("\n  ✅ Nenhum grupo de duplicatas encontrado.")
        return

    total_duplicates = sum(len(g) for _, g in filtered_groups)
    total_to_remove = total_duplicates - len(filtered_groups)  # keep 1 per group

    print(f"\n  📊  {len(filtered_groups)} grupo(s) de duplicatas encontrados")
    print(f"      {total_duplicates} entrada(s) envolvidas")
    print(f"      {total_to_remove} seriam removida(s) (mantendo 1 por grupo)")
    print()

    removed_count = 0

    if args.interactive:
        for group_idx, (group_score, group) in enumerate(filtered_groups, 1):
            print("═" * 70)
            print(f"  GRUPO #{group_idx}  |  Score: {group_score:.0%}  |  {len(group)} entradas")
            print("═" * 70)

            for idx, (entry, sig, _) in enumerate(group):
                t = sig["title"] or "(no title)"
                u = sig["username"]
                extra = f" [{u}]" if u else ""
                g = get_entry_group_path(entry)
                comp = _entry_completeness(sig)
                print(f"  [{idx}] {t}{extra}")
                print(f"       Grupo: /{g}   Completude: {comp}")
                print(f"       URL: {sig['url'] or '-'}")
                if sig["notes"]:
                    notes = sig["notes"]
                    if len(notes) > 60:
                        notes = notes[:57] + "..."
                    print(f"       Notes: {notes}")
                print()

            # Mostrar scores entre pares
            for a in range(len(group)):
                for b in range(a + 1, len(group)):
                    fs = compute_field_scores(group[a][1], group[b][1])
                    s = compute_overall_similarity(fs)
                    t_a = group[a][1]["title"] or "(no title)"
                    t_b = group[b][1]["title"] or "(no title)"
                    print(f"       {t_a}  ↔  {t_b}  →  {s:.0%}")

            print()

            if args.keep == "most-complete":
                # Escolher a mais completa
                best_idx = max(range(len(group)),
                               key=lambda i: _entry_completeness(group[i][1]))
            else:
                best_idx = 0  # first

            best_entry = group[best_idx][1]
            best_title = best_entry["title"] or "(no title)"
            best_user = best_entry["username"]
            best_extra = f" [{best_user}]" if best_user else ""

            print(f"  Mantida: [{best_idx}] {best_title}{best_extra}")
            print()

            key = prompt_key({
                "k": "manter esta", "o": "escolher outra",
                "s": "pular grupo", "q": "sair",
            })

            if key == "k":
                to_remove = [i for i in range(len(group)) if i != best_idx]
                if not dry_run:
                    for ri in to_remove:
                        entry, sig, _ = group[ri]
                        t = sig["title"] or "(no title)"
                        u = sig["username"]
                        extra = f" [{u}]" if u else ""
                        try:
                            entry.delete()
                            print(f"  🗑  REMOVIDO:  {t}{extra}")
                            removed_count += 1
                        except Exception as e:
                            print(f"  ❌ FALHA ao remover '{t}': {e}", file=sys.stderr)
                else:
                    for ri in to_remove:
                        entry, sig, _ = group[ri]
                        t = sig["title"] or "(no title)"
                        u = sig["username"]
                        extra = f" [{u}]" if u else ""
                        print(f"  🗑  REMOVERIA:  {t}{extra}")
                        removed_count += 1

            elif key == "o":
                print("  Escolha qual manter [0-{}]:".format(len(group) - 1), end=" ", flush=True)
                try:
                    ch = input().strip()
                    chosen = int(ch)
                    if 0 <= chosen < len(group):
                        to_remove = [i for i in range(len(group)) if i != chosen]
                        if not dry_run:
                            for ri in to_remove:
                                entry, sig, _ = group[ri]
                                t = sig["title"] or "(no title)"
                                u = sig["username"]
                                extra = f" [{u}]" if u else ""
                                entry.delete()
                                print(f"  🗑  REMOVIDO:  {t}{extra}")
                                removed_count += 1
                        else:
                            for ri in to_remove:
                                entry, sig, _ = group[ri]
                                t = sig["title"] or "(no title)"
                                u = sig["username"]
                                extra = f" [{u}]" if u else ""
                                print(f"  🗑  REMOVERIA:  {t}{extra}")
                                removed_count += 1
                    else:
                        print("  Índice inválido, pulando grupo.")
                except (ValueError, IndexError):
                    print("  Entrada inválida, pulando grupo.")

            elif key == "q":
                print("  Operação abortada.")
                break
            # else "s": skip

    else:
        # Modo não-interativo: mostrar relatório e perguntar ação em lote
        report_lines = []
        for group_idx, (group_score, group) in enumerate(filtered_groups, 1):
            report_lines.append(f"Grupo #{group_idx} (score: {group_score:.0%}, {len(group)} entradas):")
            for entry, sig, _ in group:
                t = sig["title"] or "(no title)"
                u = sig["username"]
                extra = f" [{u}]" if u else ""
                g = get_entry_group_path(entry)
                comp = _entry_completeness(sig)
                report_lines.append(f"  - {t}{extra}  /{g}  (completude: {comp})")
            report_lines.append("")

        report = "\n".join(report_lines)
        print("📋  GRUPOS DE DUPLICATAS:")
        display_via_pager(report, args.no_pager)

        print()
        print(f"  {len(filtered_groups)} grupo(s), {total_to_remove} entrada(s) a remover.")
        print()
        act = prompt_key({
            "r": "remover duplicatas",
            "i": "revisar grupos",
            "q": "sair",
        })

        if act == "r":
            for _, group in filtered_groups:
                if args.keep == "most-complete":
                    best_idx = max(range(len(group)),
                                   key=lambda i: _entry_completeness(group[i][1]))
                else:
                    best_idx = 0
                to_remove = [i for i in range(len(group)) if i != best_idx]
                for ri in to_remove:
                    entry, sig, _ = group[ri]
                    t = sig["title"] or "(no title)"
                    u = sig["username"]
                    extra = f" [{u}]" if u else ""
                    if not dry_run:
                        entry.delete()
                        print(f"  🗑  REMOVIDO:  {t}{extra}")
                    else:
                        print(f"  🗑  REMOVERIA:  {t}{extra}")
                    removed_count += 1
        elif act == "i":
            # Re-executa em modo interativo (simplificado)
            for group_idx, (group_score, group) in enumerate(filtered_groups, 1):
                print()
                print(f"  GRUPO #{group_idx} (score: {group_score:.0%})")
                for idx, (entry, sig, _) in enumerate(group):
                    t = sig["title"] or "(no title)"
                    u = sig["username"]
                    extra = f" [{u}]" if u else ""
                    print(f"  [{idx}] {t}{extra}")

                if args.keep == "most-complete":
                    best_idx = max(range(len(group)),
                                   key=lambda i: _entry_completeness(group[i][1]))
                else:
                    best_idx = 0

                print(f"  Manter: [{best_idx}]")
                key = prompt_key({"k": "manter", "o": "escolher", "s": "pular", "q": "sair"})

                if key == "k":
                    to_remove = [i for i in range(len(group)) if i != best_idx]
                    for ri in to_remove:
                        entry, sig, _ = group[ri]
                        t = sig["title"] or "(no title)"
                        u = sig["username"]
                        extra = f" [{u}]" if u else ""
                        if not dry_run:
                            entry.delete()
                            print(f"  🗑  REMOVIDO:  {t}{extra}")
                        else:
                            print(f"  🗑  REMOVERIA:  {t}{extra}")
                        removed_count += 1
                elif key == "o":
                    print("  Escolha: ", end="", flush=True)
                    try:
                        chosen = int(input().strip())
                        if 0 <= chosen < len(group):
                            to_remove = [i for i in range(len(group)) if i != chosen]
                            for ri in to_remove:
                                entry, sig, _ = group[ri]
                                t = sig["title"] or "(no title)"
                                u = sig["username"]
                                extra = f" [{u}]" if u else ""
                                if not dry_run:
                                    entry.delete()
                                    print(f"  🗑  REMOVIDO:  {t}{extra}")
                                else:
                                    print(f"  🗑  REMOVERIA:  {t}{extra}")
                                removed_count += 1
                    except ValueError:
                        print("  Inválido.")
                elif key == "q":
                    break
        # else "q": sai

    # ── Sumário ───────────────────────────────────────────────────────────
    print()
    print("═" * 60)
    print(f"  Database:     {args.database.name}")
    print(f"  Grupos encontrados: {len(filtered_groups)}")
    print(f"  Removidas:    {removed_count}")
    print(f"  Modo:         {'PREVIEW (nada removido)' if dry_run else 'APLICANDO'}")
    print("═" * 60)

    if not dry_run and removed_count > 0:
        kp.save()
        print(f"  ✅ Banco salvo com sucesso ({removed_count} entrada(s) removidas).")
    elif dry_run and removed_count > 0:
        print(f"  ⚠  Preview. Use --apply para remover {removed_count} entrada(s).")
    else:
        print("  Nada a fazer.")

def validate_common(args) -> None:
    """Validate shared argument constraints."""
    if hasattr(args, 'similarity_threshold'):
        if args.similarity_threshold < 0 or args.similarity_threshold > 1:
            print("ERROR: --similarity-threshold deve estar entre 0 e 1.", file=sys.stderr)
            sys.exit(1)
    if hasattr(args, 'min_score'):
        if args.min_score < 0 or args.min_score > 1:
            print("ERROR: --min-score deve estar entre 0 e 1.", file=sys.stderr)
            sys.exit(1)
    if hasattr(args, 'max_score'):
        if args.max_score < 0 or args.max_score > 1:
            print("ERROR: --max-score deve estar entre 0 e 1.", file=sys.stderr)
            sys.exit(1)
    if hasattr(args, 'min_score') and hasattr(args, 'max_score'):
        if args.min_score > args.max_score:
            print("ERROR: --min-score não pode ser maior que --max-score.", file=sys.stderr)
            sys.exit(1)

def _find_zsh_completion_dir(user_home: str) -> str:
    """Find a writable directory for zsh completions, checking common fpath locations."""
    # 1. Check ~/.zfunc/ (commonly added to fpath by users)
    zfunc_dir = os.path.join(user_home, ".zfunc")
    if os.path.isdir(zfunc_dir) and os.access(zfunc_dir, os.W_OK):
        return zfunc_dir
    # 2. Check ~/.local/share/zsh/site-functions/ (XDG)
    local_zsh = os.path.join(user_home, ".local", "share", "zsh", "site-functions")
    os.makedirs(local_zsh, exist_ok=True)
    if os.access(local_zsh, os.W_OK):
        return local_zsh
    # 3. Fallback: create ~/.zfunc/
    os.makedirs(zfunc_dir, exist_ok=True)
    return zfunc_dir


def cmd_completions(args: argparse.Namespace) -> None:
    """Detect binary location and install shell completions."""
    import shutil

    # Descobrir onde o binário está
    bin_path = shutil.which("kbdx-ops")
    if not bin_path:
        # Talvez esteja rodando via python kbdx-ops.py
        bin_path = os.path.abspath(sys.argv[0])

    bin_dir = os.path.dirname(os.path.realpath(bin_path))

    # Determinar diretórios de instalação
    user_home = os.path.expanduser("~")
    local_bin_dirs = [
        os.path.join(user_home, ".local", "bin"),
        os.path.join(user_home, ".cargo", "bin"),
        os.path.join(user_home, "bin"),
    ]

    if any(bin_dir.startswith(d) for d in local_bin_dirs):
        # Instalação local do usuário
        if args.shell == "bash":
            dest_dir = os.path.join(user_home, ".local", "share", "bash-completion", "completions")
            dest_file = os.path.join(dest_dir, "kbdx-ops")
        else:
            dest_dir = _find_zsh_completion_dir(user_home)
            dest_file = os.path.join(dest_dir, "_kbdx-ops")
        install_type = "local"
    elif bin_dir.startswith("/usr") or bin_dir.startswith("/opt"):
        # Instalação global do sistema
        if args.shell == "bash":
            dest_dir = "/etc/bash_completion.d"
            dest_file = os.path.join(dest_dir, "kbdx-ops")
        else:
            dest_dir = "/usr/share/zsh/site-functions"
            dest_file = os.path.join(dest_dir, "_kbdx-ops")
        install_type = "global"
    else:
        # Fallback: local
        if args.shell == "bash":
            dest_dir = os.path.join(user_home, ".local", "share", "bash-completion", "completions")
            dest_file = os.path.join(dest_dir, "kbdx-ops")
        else:
            dest_dir = _find_zsh_completion_dir(user_home)
            dest_file = os.path.join(dest_dir, "_kbdx-ops")
        install_type = "local (fallback)"

    # Criar diretório se não existir
    os.makedirs(dest_dir, exist_ok=True)

    # Escrever o arquivo de completions
    script = _BASH_COMPLETION if args.shell == "bash" else _ZSH_COMPLETION
    with open(dest_file, "w") as f:
        f.write(script)
    os.chmod(dest_file, 0o644)

    print(f"  ✅ Completions {args.shell} instalados: {dest_file}")
    print(f"     Binário em: {bin_path}  ({install_type})")
    print()

    if args.shell == "bash":
        print("  Para ativar na sessão atual:")
        print(f"    source {dest_file}")
        print("  Ou reinicie o terminal.")
    else:
        print("  Para ativar, adicione ao ~/.zshrc:")
        print('    autoload -Uz compinit && compinit')
        print(f"  Ou reinicie o terminal.")

def main():
    parser = build_parser()
    args = parser.parse_args()
    validate_common(args)

    if args.command == "merge":
        if args.interactive and not args.similar:
            print("ERROR: --interactive requer --similar.", file=sys.stderr)
            sys.exit(1)
        if args.auto_skip_similar and not args.similar:
            print("ERROR: --auto-skip-similar requer --similar.", file=sys.stderr)
            sys.exit(1)
        if not args.dest_db.exists():
            print(f"ERROR: Banco destino não encontrado: {args.dest_db}", file=sys.stderr)
            sys.exit(1)
        if not args.src_db.exists():
            print(f"ERROR: Banco fonte não encontrado: {args.src_db}", file=sys.stderr)
            sys.exit(1)
        if args.dest_db == args.src_db:
            print("ERROR: Destino e fonte devem ser arquivos diferentes.", file=sys.stderr)
            sys.exit(1)
        cmd_merge(args)

    elif args.command == "diff":
        if not args.file_a.exists():
            print(f"ERROR: Arquivo não encontrado: {args.file_a}", file=sys.stderr)
            sys.exit(1)
        if not args.file_b.exists():
            print(f"ERROR: Arquivo não encontrado: {args.file_b}", file=sys.stderr)
            sys.exit(1)
        if args.file_a == args.file_b:
            print("ERROR: Os dois arquivos devem ser diferentes.", file=sys.stderr)
            sys.exit(1)
        if args.apply and not args.output:
            print("ERROR: --apply requer --output.", file=sys.stderr)
            sys.exit(1)
        if args.output and args.output.exists() and args.apply:
            resp = input(f"  ⚠  {args.output.name} já existe. Sobrescrever? [s/N] ").strip().lower()
            if resp not in ("s", "sim", "y", "yes"):
                print("  Operação cancelada.")
                sys.exit(0)
        cmd_diff(args)

    elif args.command == "completions":
        cmd_completions(args)

    elif args.command == "dedup":
        if not args.database.exists():
            print(f"ERROR: Banco não encontrado: {args.database}", file=sys.stderr)
            sys.exit(1)
        cmd_dedup(args)

if __name__ == "__main__":
    main()
