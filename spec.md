# Template AI Spec *(spec.md — commit trước hạn chốt spec: 21:00 18/9, tại CP4 · quality bar chốt từ thời điểm nộp)*

> Cấu trúc phủ đúng "SPEC 8 phần" của chương trình: Bằng chứng (§1-§2) · Lát cắt (§4) · Canvas (đính kèm CP1) · Augment/Automate (§4) · 4 đường đi của trải nghiệm (§6) · Kiểu lỗi (§5) · Kiểm thử (§7) · Phân công (§8). Hướng dẫn viết từng mục: `02-guide.md`.

```markdown
**# AI SPEC — Bản đồ lỗ hổng của lớp cho giảng viên · Nhóm [XX] · Zone [X]**

Hướng: [x] A — VLearn  [ ] B — Trợ lý Học viên  [ ] C — Làn mở

Loại: [ ] Tối ưu tính năng có sẵn  [x] Tính năng mới

**## §1. User & Job**

- Job executor + workflow (đính kèm worksheet JTBD / ảnh sơ đồ): Giảng viên/TA của lớp → xem các câu hỏi và tín hiệu khó hiểu trong chatlog → xác định chủ đề học viên đang gặp khó khăn → quyết định nội dung cần giải thích/ôn lại.

- Core JTBD (không tên sản phẩm/AI trong câu): Khi chuẩn bị hoặc điều chỉnh nội dung giảng dạy, giảng viên muốn biết lớp đang gặp khó khăn ở chủ đề nào để ưu tiên giải thích hoặc ôn tập đúng chỗ.

- Problem statement (KHÔNG chữ AI):Giảng viên phải tự đọc và tổng hợp nhiều câu hỏi rời rạc của học viên để nhận ra các chủ đề đang gây khó khăn, khiến việc xác định ưu tiên giảng lại tốn thời gian và có thể bỏ sót những vấn đề lặp lại.

- Evidence (chuẩn A và/hoặc B — log đầy đủ trong repo):

- Số liệu mining / kết quả khảo sát (n = 10, 70% xác nhận): 7/10 học viên cho biết họ từng gặp khó khăn khi xác định phần kiến thức mình chưa hiểu và phải tìm lại nhiều câu hỏi hoặc nội dung liên quan. Trong đó Thu, Kiên và Bình đều đề cập nhu cầu tổng hợp các câu hỏi lặp lại để biết chủ đề nào cần được giải thích thêm.

- ≥5 quote/ví dụ nguyên văn + nguồn:

```
\- “Em vẫn chưa hiểu sự khác nhau giữa RAG và fine-tuning.” — Thu, `CHAT-014`

\- “Em đọc lại slide nhưng vẫn không biết tại sao phải dùng embedding.” — Bình, `CHAT-027`

\- “Có ai giải thích lại giúp em đoạn retrieval được không?” — Kiên, `CHAT-035`

\- “Em làm theo ví dụ nhưng kết quả không giống trong bài giảng.” — Thu, `CHAT-041`

\- “Em không chắc là mình hiểu đúng cách hoạt động của vector database.” — Bình, `CHAT-056`
```

**## §2. Impact & quyết định chọn**

- Bảng impact ≥3 ứng viên (bao nhiêu người · tần suất · tốn gì mỗi lần · khả thi):

- **Thu — học viên:** 3/10 người có vấn đề tương tự; khoảng 2–3 lần/tuần; mất 10–15 phút mỗi lần để tìm lại nội dung và câu hỏi cũ; khả thi cao.

- **Kiên — học viên:** 3/10 người có vấn đề tương tự; khoảng 1–2 lần/tuần; mất 10–15 phút mỗi lần để xác định phần kiến thức chưa chắc; khả thi cao.

- **Bình — học viên:** 2/10 người có vấn đề tương tự; khoảng 2 lần/tuần; mất khoảng 10 phút mỗi lần để đối chiếu slide, chatlog và bài giảng; khả thi cao.

- **Minh — học viên:** 1/10 người có vấn đề tương tự; khoảng 1 lần/tuần; mất 5 phút mỗi lần để tìm lại câu hỏi cũ; khả thi cao.

- **Lan — học viên:** 1/10 người có vấn đề tương tự; khoảng 1 lần/tuần; mất 5–10 phút mỗi lần để tìm tài liệu; khả thi trung bình.

- Ứng viên ĐÃ LOẠI + vì sao:

- **Minh:** Chỉ 1/10 người gặp vấn đề và tần suất thấp, chủ yếu là nhu cầu tìm lại thông tin cá nhân.

- **Lan:** Chỉ 1/10 người gặp vấn đề, tần suất thấp và vấn đề thiên về tìm tài liệu hơn là xác định lỗ hổng kiến thức.

- Ứng viên CHỌN + vì sao (bằng số): **Thu, Kiên và Bình:** Có tổng cộng 8/10 lượt học viên được khảo sát ghi nhận nhu cầu liên quan đến việc xác định hoặc tổng hợp phần kiến thức chưa hiểu; ba ứng viên có tần suất gặp vấn đề từ 1–3 lần/tuần và mất khoảng 10–15 phút mỗi lần. Đây là nhóm vấn đề có thể tổng hợp từ chatlog thành bản đồ các chủ đề cần giảng viên ưu tiên giải thích hoặc ôn lại.


## §3. Giải pháp tương tự đã nghiên cứu
- [Sản phẩm 1]: flow / đáng học / đáng né / mình khác gì
- [Sản phẩm 2]: ...

## §4. Thiết kế
- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
- Non-goals (≥3 thứ KHÔNG build):
- Mức prototype nhắm tới: [ ] Sketch [ ] Mock [ ] Working — phần nào mock, phần nào thật:
- Automation: [ ] augment [ ] conditional [ ] automate — lý do theo cost-of-error:
- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR, xem guide):
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8) [bảng theo guide §2.5]

## §6. Bốn đường đi của trải nghiệm
- Happy path: · Low-confidence (②): · Failure/không căn cứ (①): · Correction (user sửa):
- Khi bị đòi ngoài phạm vi (③): · Case đặc thù domain (④):

## §7. Kiểm thử
- Chiều chất lượng + định nghĩa kiểm chứng được:
- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ ___% qua bộ, và ___"
- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

## §8. Phân công & kế hoạch
- Phân công có tên: spec / evidence / prompt / code / demo
- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
```
