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

## Collections

```bash
# List collections
scholarinboxcli collection list

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
```

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
```

## Output modes

- TTY: Rich tables
- Piped: compact JSON
- `--json`: pretty JSON
