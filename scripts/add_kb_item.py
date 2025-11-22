import json
import os
import sys
import uuid


def main():
    if len(sys.argv) < 3:
        print("Cách dùng: python scripts/add_kb_item.py <title> <text> [tags,phân,cách,bằng,dấu,phẩy]")
        sys.exit(1)

    title = sys.argv[1]
    text = sys.argv[2]
    tags = []
    if len(sys.argv) >= 4:
        tags = [t.strip() for t in sys.argv[3].split(',') if t.strip()]

    kb_file = os.path.join("data", "kb", "custom_kb.json")
    os.makedirs(os.path.dirname(kb_file), exist_ok=True)

    data = []
    if os.path.isfile(kb_file):
        try:
            with open(kb_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    data = []
        except Exception:
            data = []

    item = {
        "id": uuid.uuid4().hex,
        "title": title,
        "text": text,
        "tags": tags,
    }
    data.append(item)

    with open(kb_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Đã thêm 1 mục vào {kb_file}. Hãy chạy: python scripts/init_kb.py")


if __name__ == "__main__":
    main()


