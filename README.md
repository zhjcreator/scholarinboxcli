# scholarinboxcli

CLI for Scholar Inbox (authenticated web API).

## Installation

```bash
pip install scholarinboxcli
```

Or with uv:

```bash
uv pip install scholarinboxcli
```

Or run directly with uvx (no install):

```bash
uvx scholarinboxcli auth login --url "<magic-link-url>"
```

## Auth

```bash
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"
scholarinboxcli auth status
scholarinboxcli auth logout
```

Note: `auth login` extracts `sha_key` from the URL and authenticates via the API.

Config is stored at `~/.config/scholarinboxcli/config.json`. You can override the API base with `SCHOLAR_INBOX_API_BASE`.

## Command reference

Top-level commands:

- `auth` (login/status/logout)
- `digest`
- `trending`
- `search`
- `semantic`
- `interactions`
- `bookmark` (list/add/remove)
- `collection` (list/create/rename/delete/add/remove/papers/similar)
- `conference` (list/explore)

Run `scholarinboxcli --help` or `scholarinboxcli <command> --help` for full options.

## Collections

```bash
# List collections
scholarinboxcli collection list

# Expanded collection names (marks which collections are expanded server-side)
scholarinboxcli collection list --expanded

# Create, rename, delete
scholarinboxcli collection create "My Collection"
scholarinboxcli collection rename 10759 "New Name"
scholarinboxcli collection delete 10759

# Add/remove papers
scholarinboxcli collection add 10759 4559909
scholarinboxcli collection remove 10759 4559909

# Show papers in a collection
scholarinboxcli collection papers 10759

# Similar papers for one or more collections
scholarinboxcli collection similar 10759 12345

# You can also use collection names (case-insensitive). The CLI will
# automatically fetch collection ID mappings from the API when needed.
scholarinboxcli collection papers "AIAgents"
scholarinboxcli collection similar "AIAgents" "Benchmark"
```

Collection name matching is exact → prefix → contains. If multiple matches exist, the CLI reports ambiguity and shows candidate IDs.

## Search

```bash
scholarinboxcli search "transformers" --limit 5
```

## Semantic Search

```bash
scholarinboxcli semantic "graph neural networks" --limit 5
```

## Other commands

```bash
scholarinboxcli digest --date 01-30-2026
scholarinboxcli trending --category ALL --days 7
scholarinboxcli interactions --type all
scholarinboxcli bookmark list
scholarinboxcli conference list
scholarinboxcli conference explore --query "vision"
```

## Output modes

- TTY: Rich tables
- `--json`: pretty JSON
- Piped: pretty JSON (auto)

Examples for agents/scripting:

```bash
# Auto-JSON when piped
scholarinboxcli collection list | jq '.'

# Explicit JSON
scholarinboxcli collection papers "AIAgents" --json

# JSON for automation
scholarinboxcli search "diffusion" --json
```

## Tested (2026-02-01)

The following commands were exercised against the live API (with a valid magic-link login) to confirm behavior:

```bash
scholarinboxcli --help
scholarinboxcli auth status --json
scholarinboxcli digest --date 01-30-2026 --json
scholarinboxcli trending --category ALL --days 7 --json
scholarinboxcli search "transformers" --limit 5 --json
scholarinboxcli semantic "graph neural networks" --limit 5 --json
scholarinboxcli interactions --type all --json
scholarinboxcli bookmark list --json
scholarinboxcli bookmark add 3302478 --json
scholarinboxcli bookmark remove 3302478 --json
scholarinboxcli collection list --json
scholarinboxcli collection list --expanded --json
scholarinboxcli collection papers "AIAgents" --json
scholarinboxcli collection similar "AIAgents" --json
scholarinboxcli conference list --json
scholarinboxcli conference explore --query "vision" --json
```

## Notes

- Some collection mutations (create/rename/delete/add/remove) rely on best-effort endpoints that may change on the service side. If a mutation fails, try again or use the web UI to validate the current behavior.
- Similar papers for collections uses the server endpoint used by the web UI. Results typically appear under `digest_df` in JSON responses.
