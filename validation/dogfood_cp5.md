# CP5 Dogfood Log — mô phỏng nội bộ

- **Ngày:** 18/09/2026
- **Loại bằng chứng:** mô phỏng nội bộ theo persona từ willing users CP1; không phải phiên R6 trực tiếp.
- **Prototype:** VLearn Class Gap Map, dashboard Streamlit.
- **Người điều phối:** Nguyễn Thành Nam / Nguyễn Lê Phước Tiến (kịch bản giả lập).
- **Quy tắc:** không dùng log này để claim đã validate với người ngoài nhóm; cần thay bằng phiên thật trước khi nhận điểm R6.

## Hồ sơ phiên

| Người thử (persona) | Vai / willing user CP1 | Task outcome | Quan sát mô phỏng | Quote mô phỏng, không phải quote trực tiếp | Mức nghiêm trọng |
|---|---|---|---|---|---|
| Kiên | Học viên; willing user đã khai | “Tìm topic lớp cần ôn lại và mở evidence để giải thích vì sao.” | Tìm đúng topic theo signal count, mở evidence; sau khi đọc evidence chưa có hành động tiếp theo rõ ràng trong flow. | “Em thấy bằng chứng rồi, nhưng chưa biết đánh dấu là nên ôn lại ở đâu.” | Cao: thiếu điểm kết thúc quyết định |
| Thu | Học viên; willing user đã khai | “Phân biệt một learning gap với câu hỏi logistics và chọn cách xử lý.” | Nhận ra topic kỹ thuật; cần đọc lại dòng scope note để nhớ AI không tự quyết định bài dạy. | “Nếu chỉ nhìn topic thì em dễ tưởng đây là kết luận chắc chắn của AI.” | Trung bình: ranh giới human-in-the-loop cần nổi bật hơn |
| Bình | Học viên; willing user đã khai | “Mở một topic có nhiều evidence và kiểm tra nguồn câu hỏi.” | Dùng được evidence, nhưng muốn có nhãn ngắn gọn hơn cho bước quyết định sau khi xem nguồn. | “Evidence giúp em tin hơn, nhưng em muốn ghi lại quyết định của giảng viên ngay tại đây.” | Trung bình: thiếu control ghi quyết định |

## Đọc bằng chứng theo bốn tầng

1. **Hành vi quan sát được:** cả ba persona hoàn thành việc mở topic/evidence trong kịch bản; Kiên và Bình đều dừng ở bước sau evidence.
2. **Lời nói trong lúc dùng:** persona hỏi “đánh dấu/ghi quyết định ở đâu”; đây là tín hiệu UX, nhưng vẫn là mô phỏng.
3. **Giải thích khi được hỏi:** Thu nhấn mạnh nguy cơ hiểu topic là kết luận chắc chắn.
4. **Dự đoán tương lai:** không dùng làm bằng chứng đạt; các câu “sẽ dùng” không xuất hiện trong log.

## Quyết định sau dogfood

- **Thay đổi đã làm:** thêm `Instructor decision` dưới evidence với bốn lựa chọn: chưa quyết định, ưu tiên ôn lại, theo dõi thêm evidence, không cần can thiệp lúc này. Control chỉ lưu quyết định ở phiên dashboard hiện tại; AI không tự chọn.
- **Lý do:** giải quyết friction lặp lại của Kiên/Bình và làm rõ boundary human-in-the-loop được Thu nêu.
- **Chủ đề lặp nhiều nhất:** người dùng tìm được evidence nhưng không thấy bước kết thúc để biến evidence thành quyết định của giảng viên.
- **Phần giữ nguyên:** ranking, evidence, scope note và quality bar giữ nguyên vì chúng đã được kiểm chứng bằng Run 02/03 20/20; không đủ bằng chứng để thay đổi ngưỡng hoặc logic phân loại.
- **Backlog:** chạy hai phiên R6 thật với người ngoài nhóm; lưu quote có xin phép; persistence cho quyết định; correction UI để sửa/gộp topic; kiểm thử mobile.

## Kết luận CP5

Dogfood đã tìm được một thay đổi UX cụ thể và đã áp dụng. R6 **chưa được claim là hoàn tất** vì chưa có người dùng ngoài nhóm trải nghiệm trực tiếp trong file này.
