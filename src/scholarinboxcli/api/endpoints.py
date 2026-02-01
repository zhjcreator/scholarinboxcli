"""API endpoint constants used by the Scholar Inbox client."""

from __future__ import annotations

# Auth/session
SESSION_INFO = "/api/session_info"
LOGIN_WITH_SHA_TEMPLATE = "/api/login/{sha_key}/"

# Feed/search
DIGEST = "/api/"
TRENDING = "/api/trending"
SEARCH = "/api/get_search_results/"
SEMANTIC_SEARCH = "/api/semantic-search"
INTERACTIONS = "/api/interactions"

# Bookmarks
BOOKMARKS = "/api/bookmarks"
BOOKMARK_PAPER = "/api/bookmark_paper/"

# Collections
COLLECTIONS_PRIMARY = "/api/get_all_user_collections"
COLLECTIONS_FALLBACK = "/api/collections"
COLLECTIONS_EXPANDED = "/api/get_expanded_collections"
COLLECTION_CREATE_CANDIDATES = (
    "/api/create_collection/",
    "/api/collections",
    "/api/collection-create/",
)
COLLECTION_RENAME_CANDIDATES = (
    "/api/rename_collection/",
    "/api/collection-rename/",
    "/api/collections/rename",
)
COLLECTION_DELETE_CANDIDATES = (
    "/api/delete_collection/",
    "/api/collection-delete/",
    "/api/collections/delete",
)
COLLECTION_ADD_PAPER_CANDIDATES = (
    "/api/add_paper_to_collection/",
    "/api/collection-add-paper/",
    "/api/add_to_collection/",
)
COLLECTION_REMOVE_PAPER_CANDIDATES = (
    "/api/remove_paper_from_collection/",
    "/api/collection-remove-paper/",
    "/api/remove_from_collection/",
)
COLLECTION_PAPERS = "/api/collection-papers"
COLLECTIONS_SIMILAR = "/api/get_collections_similar_papers/"

# Conferences
CONFERENCE_LIST = "/api/conference_list"
CONFERENCE_EXPLORER = "/api/conference-explorer"
