import json
import logging
from ..r2r.documents import (
    handle_create_document,
    handle_add_document_to_collection
)
from ..r2r.collections import (
    handle_create_collection,
    handle_list_user_collections
)
from ..r2r.search import (
    handle_search_with_names as handle_search,
    handle_rag_with_names as handle_rag
)

log = logging.getLogger(__name__)

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "create_collection",
            "description": "Creates a new collection to store documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the collection."
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description of the collection."
                    }
                },
                "required": ["name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_document",
            "description": "Creates a new document with the given content and adds it to a collection. The collection must be specified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_text": {
                        "type": "string",
                        "description": "The text content to be uploaded."
                    },
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to add the document to. This is required."
                    }
                },
                "required": ["raw_text", "collection_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_user_collections",
            "description": "Lists all available collections.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Performs a search across documents to find relevant chunks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you are searching for."
                    },
                    "max_chunks": {
                        "type": "integer",
                        "default": 5
                    },
                    "collection_id": {
                        "type": "string",
                        "description": "Optional collection ID to restrict the search."
                    },
                    "semantic": {
                        "type": "boolean",
                        "description": "Whether to use semantic search (default: false)."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rag",
            "description": "Answers a question using information from documents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user question or request."
                    },
                    "collection_id": {
                        "type": "string",
                        "description": "Optional collection ID to use for retrieval."
                    },
                    "max_chunks": {
                        "type": "integer",
                        "default": 8
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use for generation (default: gpt-4)."
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Temperature for generation (default: 0.7)."
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_document_to_collection",
            "description": "Adds an existing document to a collection.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "ID of the document to add."
                    },
                    "collection_id": {
                        "type": "string",
                        "description": "ID of the collection to add the document to."
                    }
                },
                "required": ["document_id", "collection_id"]
            }
        }
    }
]

# Map of function names to their handlers
function_handlers = {
    "create_collection": handle_create_collection,
    "create_document": handle_create_document,
    "list_user_collections": handle_list_user_collections,
    "search": handle_search,
    "rag": handle_rag
} 