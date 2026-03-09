"""
rag/store.py

Chroma vector store helpers: build, upsert, and file-system utilities.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Iterable, List

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

EXCLUDE_DIRS = {
    ".git",
    "Pods",
    "Carthage",
    "DerivedData",
    ".build",
    ".swiftpm",
    "Build",
    ".xcodeproj",
    ".xcworkspace",
}

SWIFT_SUFFIX = ".swift"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def normalize_path(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root)).replace("\\", "/")
    except Exception:
        return str(p).replace("\\", "/")


def iter_swift_files(root: Path) -> Iterable[Path]:
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for f in files:
            if f.endswith(SWIFT_SUFFIX):
                yield Path(dirpath) / f


def meta_list_to_str(items, limit: int = 200) -> str:
    if not items:
        return ""
    return "|".join(str(x) for x in items[:limit])


def safe_json(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

def build_vectorstore(persist_dir: str, collection: str, embed_model: str) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=embed_model)
    return Chroma(
        collection_name=collection,
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )


def upsert_documents(vs: Chroma, docs: List[Document]) -> None:
    """Upsert documents using deterministic IDs for stable re-ingestion."""
    ids = [sha1(d.page_content + safe_json(d.metadata)) for d in docs]
    vs.add_documents(documents=docs, ids=ids)
    vs.persist()
