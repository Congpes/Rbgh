import os
from typing import List, Dict, Any, Optional


class ChromaKB:
    def __init__(
        self,
        persist_dir: str = os.path.join("data", "chroma"),
        collection_name: str = "kb",
        embedding_model: str = "intfloat/multilingual-e5-small",
    ) -> None:
        # import chậm để tránh yêu cầu khi người dùng chưa cài
        try:
            import chromadb  # type: ignore
            from chromadb.utils import embedding_functions  # type: ignore
        except Exception as e:
            raise ImportError("Cần cài đặt chromadb và sentence-transformers") from e

        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )

    def upsert(self, docs: List[Dict[str, Any]]) -> None:
        ids: List[str] = []
        texts: List[str] = []
        metadatas: List[Dict[str, Any]] = []
        for d in docs:
            ids.append(str(d.get("id") or d.get("_id") or d.get("title") or len(ids)))
            texts.append(str(d.get("text") or d.get("content") or ""))
            meta = {k: v for k, v in d.items() if k not in ("id", "_id", "text", "content")}
            metadatas.append(meta)
        self.collection.upsert(ids=ids, documents=texts, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
        if not query_text.strip():
            return []
        res = self.collection.query(query_texts=[query_text], n_results=top_k)
        results: List[Dict[str, Any]] = []
        docs = (res.get("documents") or [[]])[0]
        metas = (res.get("metadatas") or [[]])[0]
        ids = (res.get("ids") or [[]])[0]
        dists = (res.get("distances") or [[]])[0]
        for i, t in enumerate(docs):
            item = {
                "id": ids[i] if i < len(ids) else str(i),
                "text": t,
                "metadata": metas[i] if i < len(metas) else {},
                "distance": dists[i] if i < len(dists) else None,
            }
            if item["distance"] is not None and min_score > 0:
                # distance càng nhỏ càng giống; quy đổi score đơn giản
                score = 1.0 - float(item["distance"])  # gần 1 là tốt
                if score < min_score:
                    continue
            results.append(item)
        return results


