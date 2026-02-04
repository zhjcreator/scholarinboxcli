# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2026-02-04

### Added

- Added collection-aware paper formatting for bookmark and collection views.
- Added tests for bookmark collection lookup and collection paper formatting.
- Added dev tooling dependencies for pytest and ruff.

### Changed

- Bookmarks now resolve the "Bookmarks" collection and load papers via `/api/get_collections`.
- Collection paper retrieval prefers `/api/get_collections` with fallback to legacy endpoints.
- Cleaned up minor lint issues and restored `_resolve_collection_id` export for tests.

## [0.1.1] - 2026-02-01

### Added

- Added `LICENSE` (MIT) file.
- Added CI workflow (`.github/workflows/ci.yml`) for help smoke-check + pytest.
- Added offline smoke tests for CLI commands with mocked client behavior.
- Added logic-focused collection resolution unit tests (exact/prefix/contains/ambiguity/fallbacks).
- Added mocked API client tests for bookmark payload/fallback behavior and conference explorer calls.
- Added Keep a Changelog style `CHANGELOG.md`.

### Changed

- Refactored CLI into focused command modules (`auth`, `papers`, `bookmarks`, `collections`, `conferences`).
- Moved collection name/ID resolution into a dedicated service module.
- Centralized API endpoint constants in `api/endpoints.py`.
- Reduced command boilerplate via shared `with_client()` helper for client lifecycle and error handling.

## [0.1.0] - 2026-02-01

### Added

- Initial `scholarinboxcli` command-line interface with Typer + Rich and JSON output.
- Auth commands: `auth login`, `auth status`, `auth logout`.
- Research workflow commands: `digest`, `trending`, `search`, `semantic`, `interactions`.
- Bookmark commands: `bookmark list`, `bookmark add`, `bookmark remove`.
- Collection commands: `collection list/create/rename/delete/add/remove/papers/similar`.
- Conference commands: `conference list`, `conference explore`.
- Collection name resolution by ID or name, including fallback ID map lookup.
- README quickstart, command examples, tested-command matrix, and release instructions.
- GitHub Actions trusted-publishing workflow for tag-based PyPI release.
- Project tagline and CLI help examples for humans and agents.

### Changed

- Standardized JSON output to pretty-printed format for both `--json` and piped output.
- Simplified `conference explore` to list-style behavior by removing ineffective query/sort options.

### Fixed

- Bookmark add/remove payloads aligned with the web API endpoint behavior.
- Collection name-to-ID resolution improved for cases where list endpoints omit IDs.

### Removed

- Tracked Python bytecode artifacts (`.pyc`) removed from repository history and ignored via `.gitignore`.

[Unreleased]: https://github.com/mrshu/scholarinboxcli/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/mrshu/scholarinboxcli/releases/tag/v0.1.2
[0.1.1]: https://github.com/mrshu/scholarinboxcli/releases/tag/v0.1.1
[0.1.0]: https://github.com/mrshu/scholarinboxcli/releases/tag/v0.1.0
