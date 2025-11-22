import json
import os
import sys
from glob import glob

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.services.kb_chromadb import ChromaKB


def main():
    kb_glob = os.path.join("data", "kb", "*.json")
    files = sorted(glob(kb_glob))
    if not files:
        print(f"Không tìm thấy file KB trong data/kb/*.json")
        sys.exit(1)

    docs = []
    for p in files:
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    docs.extend(data)
                elif isinstance(data, dict):
                    docs.append(data)
        except Exception as e:
            print(f"Bỏ qua {p}: {e}")

    kb = ChromaKB()
    kb.upsert(docs)
    print(f"Đã khởi tạo KB với {len(docs)} mục. Persist tại data/chroma/")


if __name__ == "__main__":
    main()


