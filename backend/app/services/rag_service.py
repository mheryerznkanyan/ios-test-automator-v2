"""RAG service - encapsulates vector store lifecycle and querying"""
from typing import Any, Dict, Optional


class RAGService:
    """Encapsulates Chroma vector store; lazily initialized on first use."""

    def __init__(self, settings):
        self._settings = settings
        self._vectorstore = None

    def _get_vectorstore(self):
        if self._vectorstore is None:
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(model_name=self._settings.rag_embed_model)
            self._vectorstore = Chroma(
                collection_name=self._settings.rag_collection,
                embedding_function=embeddings,
                persist_directory=self._settings.rag_persist_dir,
            )
        return self._vectorstore

    def query(self, test_description: str, k: Optional[int] = None) -> Dict[str, Any]:
        """
        Query the RAG system for relevant context based on the test description.
        Returns accessibility IDs, code snippets, and screen information.
        Degrades gracefully if the vector store is unavailable.
        """
        if k is None:
            k = self._settings.rag_top_k

        try:
            vs = self._get_vectorstore()
            docs = vs.similarity_search(test_description, k=k)

            accessibility_ids: set = set()
            screens: set = set()
            code_snippets = []

            for doc in docs:
                meta = doc.metadata

                if "accessibility_ids" in meta and meta["accessibility_ids"]:
                    accessibility_ids.update(meta["accessibility_ids"].split("|"))

                if "screen" in meta and meta["screen"]:
                    screens.add(meta["screen"])

                kind = meta.get("kind", "")
                if kind in ("swiftui_view", "accessibility_map", "screen_card",
                            "swift_class", "swift_struct", "uikit_viewcontroller"):
                    code_snippets.append({
                        "kind": kind,
                        "path": meta.get("path", ""),
                        "screen": meta.get("screen", ""),
                        "content": doc.page_content[:1500],
                    })

            return {
                "accessibility_ids": sorted(accessibility_ids),
                "screens": sorted(screens),
                "code_snippets": code_snippets[:8],
                "total_docs_retrieved": len(docs),
            }
        except Exception as exc:
            return {
                "accessibility_ids": [],
                "screens": [],
                "code_snippets": [],
                "total_docs_retrieved": 0,
                "error": str(exc),
            }
