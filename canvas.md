# Canvas CP1 — Track : Bản đồ lỗ hổng của lớp cho giảng viên từ signal/chatlog

**Nhóm:** 3NB · **Lớp:** 3B · **Phòng:** E403  
**Đội trưởng:** Trần Xuân Đức · **Mã học viên:** 2A202602768  
**Repo nhóm công khai:** https://github.com/txduc181004-web/K4-3B-E403-3NB

| # | Mục | Nội dung bản nháp |
|---|---|---|
| 1 | **Track + đề** | ** - VLearn Tutor - Bản đồ lỗ hổng của lớp cho giảng viên từ signal/chatlog.** |
| 2 | **Job executor** | Giảng viên / trợ giảng sử dụng hệ thống để theo dõi các dấu hiệu cho thấy học viên đang gặp khó khăn trong quá trình học, từ đó biết chủ đề nào cần được giải thích hoặc hỗ trợ thêm. |
| 3 | **Pain** | âu hỏi của học viên dễ bị bỏ sót hoặc trả lời quá muộn, đặc biệt trong lớp đông. Khi không nhận được phản hồi, học viên có thể phải hỏi lại nhiều lần hoặc tự tìm câu trả lời, khiến lỗ hổng kiến thức kéo dài. |
| 4 | **1–2 bằng chứng đầu** | Trong vlearn-pack/chatlog/tutor_turns.csv: hệ thống VLearn (Postgres qua Superset), gộp hai kỳ: bảng gốc kỳ 21/07–02/08 và view kỳ từ 03/08. Mỗi dòng = một lượt hỏi-đáp (câu hỏi học viên + câu trả lời tutor). Xuất 15/09/2026. 13.494 dòng, 22/07 18:00 → 15/09 17:57 (giờ VN). |
| 5 | **Lát cắt một câu** | **Một giảng viên** xem các câu hỏi trong chatlog của lớp; **AI quyết định** nhóm các câu hỏi lặp lại thành các chủ đề có dấu hiệu hổng kiến thức; **giảng viên nhận** bản đồ các chủ đề cần giảng lại, kèm bằng chứng từ chatlog. |
| 6 | **AI tự làm gì, không tự làm gì + willing users** | **AI tự làm:** Phân nhóm chatlog, phát hiện các chủ đề có tín hiệu khó hiểu và tạo bản đồ lỗ hổng kèm evidence. **AI không tự làm:** Không tự kết luận học viên “không hiểu” hay tự thay đổi nội dung giảng dạy. **Lý do:** Quyết định chuyên môn cuối cùng cần giảng viên xác nhận dựa trên evidence. **Người ngoài nhóm đã đồng ý thử:** Thu - Bình - Kiên. |
| 7 | **Phân công có tên** | **Nam:** Data mining & phân tích chatlog. **Tiến:** Thiết kế AI Agent & logic phát hiện lỗ hổng. **Đức:** Backend/UI & tích hợp prototype |

## Tự soát trước khi nộp

- [x] Điền tên nhóm, phòng, đội trưởng, mã học viên và URL **repo nhóm mới, công khai**.
- [x] Điền tên thật và phần việc của từng thành viên; xác nhận số thành viên hợp lệ với TA nếu nhóm có 5 người (README đề bài ghi 3–4 người).
- [x] Xác nhận trực tiếp ít nhất 3 người ngoài nhóm đồng ý thử prototype; chỉ ghi tên khi họ đã đồng ý.
- [x] Mở lại `T10366` và `T10436` để chắc chúng phù hợp với pain đã chọn; thay bằng mã khác nếu không phù hợp.
- [x] Khảo sát có 23 phiếu nhưng chỉ 17 người báo đã dùng tutor trong 7 ngày qua; kiểm tra người trả lời có ngoài nhóm không trước khi dùng chuẩn khảo sát ≥20 người của rubric. Một phiếu không ghi tên. Không suy ra 12 người kiểm tra lại *vì* thiếu trích dẫn — bảng hỏi chưa hỏi nguyên nhân đó.
- [x] Đội trưởng nộp Canvas và link repo theo form CP1 được công bố tại khai mạc.

**Lưu ý dữ liệu:** Chỉ đưa số tổng hợp và ví dụ ngắn có mã lượt vào repo nhóm. Không sao chép hay commit nguyên `data/` của repo đề bài.