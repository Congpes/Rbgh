### Hướng dẫn nhanh Rasa (tiếng Việt)

Yêu cầu cài đặt:
- `pip install rasa rasa-sdk`

Thư mục này gồm:
- `config.yml` – pipeline NLU và policy
- `domain.yml` – intents, responses, actions
- `data/nlu.yml` – ví dụ huấn luyện intents
- `data/rules.yml` – mapping intent -> action
- `endpoints.yml` – endpoint của action server
- `actions/actions.py` – các action: giờ, ngày, thời tiết, tra cứu KB

Huấn luyện và chạy:
```bash
# 1) Train NLU/Core
rasa train

# 2) Chạy action server
rasa run actions --actions rasa.actions.actions

# 3) Chạy Rasa server REST
rasa run --enable-api --cors "*" -p 5005
```

Tích hợp với ứng dụng:
- Ứng dụng UI đã gọi REST `http://localhost:5005/webhooks/rest/webhook` nếu server đang chạy.
- Nếu server không chạy, UI fallback sang KB nội bộ (ChromaDB).

Mở rộng dữ liệu:
- Thêm ví dụ vào `data/nlu.yml`, rồi `rasa train` lại.
- Bổ sung rule/story nếu cần luồng hội thoại phức tạp.

