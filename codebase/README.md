# Prototype AI — Topic Gap Triage

Mục tiêu của prototype này là giúp giảng viên/TA xác định chủ đề học viên đang gặp khó bằng cách phân tích chatlog / câu hỏi học tập và gợi ý `topic` + `confidence` + `action`.

## Thành phần

- `topic_gap_triage.py`: module AI thật, dùng Ollama `qwen2.5:3b`
- `../eval/golden_set_20.json`: golden set 20 case
- `../eval/run_01_results.json`: kết quả chạy thực tế bộ test
- `../eval/model_trace.jsonl`: trace từng lần gọi model, gồm prompt/messages và raw response

## Cách chạy

```bash
python codebase/topic_gap_triage.py
```

## Mục đích CP3

- Có ít nhất 1 lời gọi mô hình AI thật ở nút quyết định trung tâm
- Có logging / trace rõ ràng ở code
- Có đánh giá sơ bộ bằng golden set thực tế
- Golden set dùng User Input Grid gồm 4 chiều: clarity, scope, technical specificity và evidence context; mỗi case có `input_grid_cell`, đồng thời ghi rõ các ô chưa được phủ.
- Kết quả đánh giá có `failure_analysis` cho từng case không đạt.

## Giới hạn

- Đây là prototype mock/conditional, không tự động quyết định nội dung giảng dạy cuối cùng cho giảng viên.
- Nếu AI không chắc, nó yêu cầu review của con người.
