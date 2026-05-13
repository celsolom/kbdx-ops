# kbdx-ops — KeePass file operations

**kbdx-ops** is a command-line tool to **merge** and **diff** KeePass (.kdbx) databases. It detects exact duplicates, finds similar entries using fuzzy field matching, and can produce standalone diff files.

```
$ kbdx-ops --version
kbdx-ops 1.0
```

## Features

- **Merge** — Copy new entries from a source database into a destination, skipping exact duplicates
- **Similar detection** — Find near-duplicate entries with per-field similarity scores (title, username, password, URL, notes, custom fields)
- **Diff** — Compare two databases and show entries that exist only in one, or differ between them
- **Diff output** — Create a new .kdbx containing only the divergent entries
- **Filters** — `--min-score` / `--max-score` to focus on specific similarity ranges
- **Interactive review** — Single-key input (`a`/`s`/`b`/`q`) with per-entry detail and optional pager
- **Shell completions** — Tab completion for bash and zsh
- **Safe by default** — Preview mode unless `--apply` is given

## Quick start

```bash
# Merge — preview only
kbdx-ops merge pessoal.kdbx protonpass.kdbx --similar

# Merge — review similar entries one by one
kbdx-ops merge pessoal.kdbx protonpass.kdbx --similar --interactive

# Merge — apply changes
kbdx-ops merge pessoal.kdbx protonpass.kdbx --apply

# Diff — show differences between two databases
kbdx-ops diff pessoal.kdbx backup.kdbx

# Diff — create a new .kdbx with only the differing entries
kbdx-ops diff pessoal.kdbx backup.kdbx -o diff.kdbx --apply

# Dedup — preview duplicates
kbdx-ops dedup pessoal.kdbx

# Dedup — remove duplicates
kbdx-ops dedup pessoal.kdbx --apply
```

## Install

### Pre-built binary

Download `kbdx-ops` from the [releases page](https://github.com/celsolom/kbdx-ops/releases) and place it in your PATH:

```bash
chmod +x kbdx-ops
mv kbdx-ops ~/.local/bin/
```

### From source

```bash
git clone https://github.com/celsolom/kbdx-ops.git
cd kbdx-ops
./build.sh
```

The binary will be in `dist/kbdx-ops`.

## Shell completions

```bash
# Bash
kbdx-ops completions bash

# Zsh
kbdx-ops completions zsh
```

O comando detecta automaticamente onde o binário está instalado:

| Localização do binário | Destino bash | Destino zsh |
|---|---|---|
| `~/.local/bin/` | `~/.local/share/bash-completion/completions/kbdx-ops` | `~/.local/share/zsh/site-functions/_kbdx-ops` |
| `/usr/bin/`, `/usr/local/bin/` | `/etc/bash_completion.d/kbdx-ops` | `/usr/share/zsh/site-functions/_kbdx-ops` |

Após instalar, reinicie o terminal ou recarregue:

```bash
# Bash
source ~/.bashrc

# Zsh
autoload -Uz compinit && compinit
```

## Usage

```
kbdx-ops merge <dest_db> <src_db> [options]
kbdx-ops diff <file_a> <file_b> [options]
kbdx-ops dedup <database> [options]
kbdx-ops completions <bash|zsh>
kbdx-ops --version
kbdx-ops --help
```

### Merge command

| Option | Description |
|---|---|
| `--apply` | Actually save changes (default is preview) |
| `--similar` | Detect near-duplicate entries |
| `--similarity-threshold 0.5` | Minimum score to flag as similar |
| `--interactive, -i` | Review each similar entry one by one |
| `--min-score 0.3` | Only show similars with score >= N |
| `--max-score 0.8` | Only show similars with score <= N |
| `--auto-skip-similar` | Skip all similar entries automatically |
| `--no-pager` | Print report to stdout instead of pager |
| `--dest-password` / `--src-password` | Passwords (omit to prompt) |
| `--dest-keyfile` / `--src-keyfile` | Key files |

### Diff command

| Option | Description |
|---|---|
| `-o, --output FILE` | Output .kdbx with diff entries |
| `--apply` | Actually create the output file |
| `--similarity-threshold 0.5` | Threshold for pairing entries |
| `--min-score` / `--max-score` | Filter diff entries by score |
| `--no-pager` | Print report without pager |
| `--password-a` / `--password-b` | Passwords for input files |
| `--output-password` | Password for output file |
| `--keyfile-a` / `--keyfile-b` / `--output-keyfile` | Key files |

### Dedup command

| Option | Description |
|---|---|
| `--apply` | Actually remove duplicates (default is preview) |
| `--interactive, -i` | Review each duplicate group one by one |
| `--similarity-threshold 0.8` | Minimum score to consider duplicate |
| `--min-score` / `--max-score` | Filter groups by score |
| `--no-pager` | Print report without pager |
| `--keep {most-complete,first}` | Which entry to keep (default: most-complete) |
| `--password` | Database password (omit to prompt) |
| `--keyfile` | Key file |

## How it works

### Matching logic

1. **Exact duplicate** — All non-empty fields (title, username, password, URL, notes, custom properties) match → skipped
2. **Similar entry** — Fields don't match exactly but the weighted fuzzy score exceeds the threshold → flagged for review
3. **New entry** — No match found → added

### Similarity scoring

| Field | Weight |
|---|---|
| Title | 4 |
| Username | 3 |
| URL | 2 |
| Password | 2 |
| Notes | 1 |
| Custom fields | 2 |

Each field is compared using `difflib.SequenceMatcher` (case-insensitive). The overall score is a weighted average (0–1).

### Diff categories

- 🔵 **Only in A** — entries present in the first database with no match in the second
- 🟢 **Only in B** — entries present in the second database with no match in the first
- 🟡 **Modified** — entries that exist in both but have different content

## License

Apache 2.0 — see [LICENSE](LICENSE).
