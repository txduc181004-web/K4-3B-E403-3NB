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

1. NotebookLM / AI research assistant
   - Flow: người dùng tải tài liệu, hỏi câu hỏi, hệ thống trả lời kèm nguồn và trích dẫn rõ ràng.
   - Điều đáng học: luôn gắn câu trả lời với nguồn/đoạn văn, giúp người dùng kiểm chứng nhanh; cách hiển thị topic/summary rõ hơn khi tài liệu dài.
   - Điều đáng né: không phù hợp với chatlog rời rạc, vì dữ liệu không có cấu trúc và không luôn mang nguồn rõ ràng; nếu AI cố gắng gộp mọi câu hỏi vào “bài học” thì dễ sinh ra “triệu chứng giả” hoặc topic quá rộng.
   - Khác với giải pháp của chúng ta: chúng ta không cần trả lời học viên từng câu hỏi, mà cần nhận diện “điểm đau chung” của lớp từ các câu hỏi lặp lại, rồi ưu tiên nội dung giảng lại.

2. ChatGPT / Claude study mode / AI tutor
   - Flow: trả lời theo ngữ cảnh học tập, giải thích từng khái niệm và gợi ý follow-up.
   - Điều đáng học: AI có thể làm rõ khái niệm theo mức độ học viên và cải thiện trải nghiệm khi học viên đang “mất mạch” trong lúc học.
   - Điều đáng né: dễ tạo ra câu trả lời dày đặc nhưng không phản ánh “vấn đề nào đang lặp lại trong lớp”, nên không hỗ trợ giảng viên quyết định ưu tiên giảng dạy.
   - Khác với giải pháp của chúng ta: chúng ta tập trung vào mô hình “phát hiện chủ đề khó của cả lớp” chứ không chỉ giải bất kỳ một câu hỏi nào.

3. Khanmigo / AI tutor học tập theo lớp
   - Flow: hỗ trợ học viên trong quá trình học, thường kèm theo theo dõi tiến độ và gợi ý khi học viên mắc lỗi.
   - Điều đáng học: nên chia rõ “câu hỏi hiện tại” với “topic học đang gặp vấn đề”, và ưu tiên hiển thị sự chắc chắn/căn cứ của AI.
   - Điều đáng né: không nên biến AI thành “người chốt mọi quyết định” cho giảng viên; hệ thống cần để người dùng kiểm soát final judgement.
   - Khác với giải pháp của chúng ta: hướng của chúng ta là support giảng viên dạng triage và priorítization, không phải cá nhân hoá từng học viên.

Kết luận: các sản phẩm hiện có tốt ở việc giải thích hoặc tổng hợp kiến thức, nhưng thiếu một tầng “sự kiện lớp học” theo thời gian và chủ đề, nên không giải quyết được bài toán: “giảng viên cần biết lớp đang gặp khó ở chủ đề nào và cần ưu tiên giải thích ở đâu.”

## §4. Thiết kế

- Lát cắt MỘT CÂU (1 user · 1 việc · 1 quyết định AI · 1 kết quả):
  - Với giảng viên/TA của một lớp, AI xem các câu hỏi và tin nhắn trong chatlog, nhóm các câu hỏi theo chủ đề và cho thấy chủ đề nào đang gây khó khăn nhất, để giảng viên quyết định nội dung cần ôn lại mà không bỏ sót vấn đề lặp lại.

- Non-goals (≥3 thứ KHÔNG build):
  1. Không trả lời từng câu hỏi của học viên thay cho TA hoặc giảng viên.
  2. Không chấm điểm/đánh giá học viên cá nhân theo tiến độ hoặc mức độ hiểu bài.
  3. Không tự động quyết định nội dung giảng dạy cuối cùng; AI chỉ gợi ý, người dùng giữ quyền quyết định.
  4. Không dự đoán hành vi học viên ngoài dữ liệu chatlog và slide nội dung đã có.
  5. Không dùng dữ liệu cá nhân hoặc cuộc hội thoại ngoài phạm vi lớp học.

- Mức prototype nhắm tới: [ ] Sketch [x] Mock [ ] Working — phần nào mock, phần nào thật:
  - Mock: UI, flow nhập chatlog, bảng chủ đề, ranking, mô tả nguyên nhân/độ tin cậy, thao tác xác nhận/loại bỏ chủ đề.
  - Thật: AI call phân tích chatlog, nhóm câu hỏi theo chủ đề, trích dẫn quote/tài liệu, tính điểm frequency + severity + evidence.

- Automation: [ ] augment [x] conditional [ ] automate — lý do theo cost-of-error:
  - Đây là trường hợp conditional: AI được phép tự xử lý phần lớn flow phân tích và gộp chủ đề, nhưng phải chuyển sang người dùng khi độ tin cậy thấp, khi có nhiều chủ đề mơ hồ, hoặc khi AI phát hiện không đủ căn cứ.
  - Sai lầm ở mức này có tầm ảnh hưởng cao vì giảng viên có thể ôn sai nội dung hoặc bỏ sót phần khó. Vì vậy AI không được “auto quyết định cuối cùng”; nó chỉ nên làm phần việc có căn cứ mạnh, còn các case mơ hồ sẽ hỏi lại hoặc yêu cầu xác nhận người dùng.

- §4b. Nguyên tắc đã áp dụng (≥4 — HAX/PAIR):

  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | G1 — Làm rõ hệ thống làm được gì | Mỗi lần mở giao diện, đầu tiên hiện một câu mô tả rõ: “AI phân tích chatlog và gợi ý chủ đề lớp đang gặp khó.” |
  | G2 — Làm rõ nó làm tốt đến đâu | Mỗi chủ đề có mức độ tin cậy và nguồn trích dẫn; nếu không chắc, hiển thị tag “low confidence” thay vì ẩn sự mơ hồ. |
  | G10 — Thu hẹp phạm vi khi nghi ngờ | Khi AI không thấy căn cứ rõ ràng, nó không “khẳng định chủ đề” mà trả về “chưa đủ dữ liệu” và yêu cầu người dùng xác nhận. |
  | G9 — Sửa dễ dàng | Người dùng có thể bỏ topic, chỉnh lại nhãn, thêm quote, hoặc gộp hai chủ đề trong một thao tác đơn giản. |
  | G11 — Giải thích vì sao | Mỗi chủ đề dùng số liệu và quote để justify: “5 câu hỏi có cùng từ khóa ‘embedding’, 3 câu nói lên sự nhầm lẫn giữa embedding vs vector DB”. |
  | PAIR — Explainability + Trust | AI phải show quote + confidence + rationale, không chỉ show final topic list. |
  | PAIR — Feedback + Control | Người dùng có thể xác nhận, bỏ qua, sửa label, hoặc yêu cầu AI tái phân nhóm. |
  | PAIR — Errors + Graceful Failure | Khi câu hỏi ngoài phạm vi hoặc không có căn cứ, AI trả lời “không đủ dữ liệu để suy ra chủ đề” thay vì đoán mò. |

## §5. Kiểu lỗi — 4 lớp chỗ khó + kịch bản (≥8)

| Lớp | Tình huống cụ thể | Hành vi mong muốn | Nguyên tắc áp |
|---|---|---|---|
| ① Nguồn sự thật | Một câu hỏi về “embedding” và “vector DB” bị gộp thành cùng một topic dù thực chất học viên đang hỏi 2 khái niệm khác nhau | AI hiển thị phân nhóm theo từ khóa + gợi ý “hai mảng câu hỏi có liên quan nhưng chưa hoàn toàn cùng topic”; giảng viên xác nhận/đổi nhóm | G11, PAIR — Explainability |
| ① Nguồn sự thật | Học viên hỏi “em không hiểu đoạn này ở slide 6” nhưng không có nội dung đủ để kết luận phần nào đang khó | AI không suy diễn chủ đề bằng cảm tính; thay vào đó tạo nhóm “mơ hồ” hoặc yêu cầu xác nhận | G10, PAIR — Graceful Failure |
| ② Mơ hồ / thiếu thông tin | Một câu hỏi có từ khóa “RAG” nhưng không cho biết họ đang bối cảnh ở phần fine-tuning, retrieval, hay evaluation | AI trả về “có khả năng liên quan nhưng chưa đủ căn cứ”, không chốt một topic duy nhất | G10, G2 |
| ② Mơ hồ / thiếu thông tin | Học viên viết câu hỏi ngắn “vẫn chưa hiểu chỗ này” mà không nêu rõ lý do | AI gộp vào nhóm “mơ hồ về nội dung” thay vì gán nhầm vào một topic cụ thể | G1, PAIR — Feedback + Control |
| ③ Ngoài phạm vi / thẩm quyền | Người dùng yêu cầu AI tự quyết định “phần nào nên dạy lại trong buổi sau” mà không có tham khảo Rubric/slide | AI chỉ cung cấp “gợi ý chủ đề khó” và không tự động quyết định giảng tiếp | G1, G10 |
| ③ Ngoài phạm vi / thẩm quyền | Người dùng đòi AI trả lời thay cho học viên từng câu hỏi trực tiếp | Hệ thống từ chối hoặc chuyển hướng: “Tôi chỉ hỗ trợ triage chủ đề, không thay thế phản hồi của giảng viên/TA” | G1, PAIR — Control |
| ④ Đặc thù domain | AI nhầm “vector database” với “database truyền thống” vì từ khóa trùng, dẫn giảng viên dạy sai kiến thức cốt lõi | Hệ thống yêu cầu xem xét thêm quote và tài liệu học; không chốt nếu thiếu căn cứ | G2, G11 |
| ④ Đặc thù domain | Một câu hỏi chứa thuật ngữ kỹ thuật nhưng thực chất là lỗi ngữ nghĩa trong bài giảng không phải kiến thức cốt lõi | AI ưu tiên gộp theo “mức độ khó thật” hơn là “có nhiều từ khóa”; người dùng có thể chỉnh nhãn | G9, G15 |
| ① / ④ hỗn hợp | Topic “fine-tuning” được sinh ra từ 6 câu hỏi, nhưng 4 câu thực ra đang hỏi về “training/validation split” | AI hiển thị 2 nhãn khả dĩ và một số quote dẫn chứng; không tự gộp thành một nhãn duy nhất | G2, G11 |
| ② / ③ hỗn hợp | Các tin nhắn logistics (“buổi nào bắt đầu?”, “link bài giảng đâu?”) bị nhầm thành vấn đề học tập | AI loại trừ các tin không phải câu hỏi học tập trước khi tính điểm topic | G10, PAIR — Errors + Graceful Failure |

Mỗi lớp có ít nhất 2 case và tổng cộng ≥8 case; những kịch bản làm nhóm sợ nhất là case nhầm topic kỹ thuật cốt lõi và case gộp câu hỏi logistics vào kiến thức học tập.

## §6. Bốn đường đi của trải nghiệm

- Happy path: Người dùng tải chatlog lớp học → AI phân tích 30–200 câu hỏi → hệ thống gộp thành các chủ đề, xếp hạng theo số câu hỏi lặp lại và mức độ khó → giảng viên xem quote minh chứng và xác nhận các chủ đề cần dạy lại.
- Low-confidence (②): Nếu AI thấy chủ đề chỉ có 1–2 câu hỏi hoặc có mâu thuẫn ngữ cảnh, hệ thống hiển thị cảnh báo “độ tin cậy thấp” kèm gợi ý “xem xét thêm quote” thay vì chốt chủ đề.
- Failure/không căn cứ (①): Nếu không có câu hỏi nào đủ rõ để gắn topic, AI không xuất một topic giả; thay vào đó hiển thị “Chưa có dữ liệu đủ để xác định chủ đề đang đau.”
- Correction (user sửa): Người dùng có thể gộp hai chủ đề, đổi nhãn, thêm quote, bỏ topic không hợp lệ, hoặc yêu cầu AI chạy lại trên subset câu hỏi.
- Khi bị đòi ngoài phạm vi (③): Nếu người dùng yêu cầu AI trả lời từng học viên hoặc quyết định nội dung giảng dạy hoàn toàn, hệ thống trả về “Tôi hỗ trợ triage và gợi ý chủ đề; quyết định cuối cùng thuộc về giảng viên/TA”.
- Case đặc thù domain (④): Khi câu hỏi liên quan đến kiến thức kỹ thuật nhạy cảm hoặc dễ nhầm lẫn như embedding, vector DB, RAG, fine-tuning, AI không auto xác định mà phải dựa vào quote/căn cứ trong bài giảng và tài liệu lớp học; nếu thiếu căn cứ, báo “không đủ dữ liệu để chốt”.

## §7. Kiểm thử

- Chiều chất lượng + định nghĩa kiểm chứng được:
  1. Factuality (đúng có căn cứ): mỗi topic được hiển thị phải có ít nhất 1 quote hoặc 1 câu hỏi rõ ràng trong chatlog; không được suy đoán thiếu căn cứ.
  2. Coverage: AI phải cover chủ đề chính của các câu hỏi trong chatlog, không bỏ sót trường hợp lặp lại quan trọng.
  3. Relevance: topic được phát hiện phải nằm trong phạm vi học tập, không nhầm với logistics, admin, hoặc câu hỏi cá nhân.
  4. Quality/clarity: topic được gán nhãn rõ ràng, không đem nhiều khái niệm lẫn nhau.

- Golden set (≥20 case theo cơ cấu trong guide §2.6, file trong eval/):
  - Tạo file trong `eval/` với 20–30 case: 
    - 8–10 case common/topic thường gặp (RAG, embedding, vector DB, fine-tuning, model evaluation, logistics, assignment confusion)
    - 8–10 case khó / ambiguous / low-confidence
    - 2–4 case hiếm (câu hỏi thay đổi theo ngữ cảnh, câu hỏi ngắn, câu hỏi có nội dung mơ hồ)
    - ≥10 case lấy từ chatlog thật hoặc biến thể từ data mẫu.
  - Dạng case: `input`, `expected_topic`, `confidence`, `reason`, `pass/fail`.
  - Mục tiêu kiểm tra cả 4 lớp chỗ khó.

- Quality bar (chốt từ hạn chốt spec của khoá, giữ nguyên sau đó): "Đạt khi ≥ 80% số trường hợp qua bộ, và không có lỗi 'không căn cứ / chốt topic sai khi thiếu dữ liệu' vượt quá 2 trường hợp; tất cả topic được xuất ra phải có ít nhất 1 quote hoặc nghĩa vụ minh chứng rõ từ chatlog."

- Kết quả các lượt chạy (bảng % — cập nhật đến trước CP6):

  | Lượt chạy | % qua bộ | Ghi chú | File |
  |---|---:|---|---|
  | Run 01 (mốc spec) | TBD | Chưa chạy | `eval/run-01.csv` |
  | Run 02 (sau fix prompt) | TBD | Cập nhật sau khi chỉnh logic | `eval/run-02.csv` |
  | Run 03 (pre-demo) | TBD | Chốt quality bar cuối | `eval/run-03.csv` |

## §8. Phân công & kế hoạch

- Phân công có tên:
  - Spec & product framing: [Tên thành viên 1]
  - Evidence mining & chứng cứ: [Tên thành viên 2]
  - Prompt + eval: [Tên thành viên 3]
  - Prototype / code: [Tên thành viên 4]
  - Demo & validation: [Tên thành viên 5]

- Willing users (≥2 tên) + kế hoạch vòng validation *(bonus, nếu làm)*:
  - Thu — sinh viên đang gặp vấn đề tương tự với câu hỏi lặp lại về kiến thức kỹ thuật.
  - Kiên — sinh viên thường tìm lại nội dung cũ và cần tổng hợp các câu hỏi liên quan.
  - Bình — sinh viên bối cảnh giống với điểm đau “không biết mình đã hiểu đúng hay chưa”.
  - Kế hoạch validation: 1 buổi 10 phút/người, cho từng người dùng thử sản phẩm với task cụ thể “hãy xác định chủ đề nào lớp đang gặp khó nhất”, rồi log hành vi, quote, và mức độ tin cậy mà họ dành cho AI.

- Multi-prototype (nếu làm): trục khác biệt của ≥2 phương án + lý do chọn:
  1. Phương án A — “AI tự nhóm topic tự động”:
     - Ưu điểm: tiết kiệm thời gian, phù hợp khi dữ liệu nhiều.
     - Nhược điểm: dễ chốt topic sai khi dữ liệu không đủ rõ.
  2. Phương án B — “AI gợi ý các chủ đề nhánh + người dùng xác nhận từng topic”:
     - Ưu điểm: an toàn hơn, kiểm soát tốt, ít rủi ro về kiến thức sai.
     - Nhược điểm: mất thời gian nhiều hơn nếu có quá nhiều câu hỏi.
  - Lý do chọn: chọn phương án B ở mức mock/conditional vì cost-of-error của việc “giảng viên ôn sai chủ đề” cao hơn nhiều so với thời gian xác nhận thêm 1–2 topic.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao (trỏ về feedback/case nào) |
|---|---|---|
| 18/9 — CP1 | Khóa JTBD: giảng viên/TA cần phát hiện chủ đề học viên gặp khó qua chatlog | Dựa trên 7/10 phản hồi khảo sát và các quote như “Em vẫn chưa hiểu sự khác nhau giữa RAG và fine-tuning.” |
| 18/9 — sau review spec | Chốt scope: AI phân tích topic lặp lại, không trả lời từng câu hỏi của học viên | Tránh vượt phạm vi và giảm nguy cơ “AI tự quyết định nội dung giảng dạy” |
| 18/9 — trước CP4 | Chốt thiết kế conditional, xác nhận phải có source + confidence | Theo pattern lỗi đầu tiên: AI dễ gộp topic nhầm khi thiếu căn cứ |
| 18/9 — trước CP5 | Thêm golden set theo 4 lớp chỗ khó và quality bar ≥ 80% | Đảm bảo đánh giá bằng dữ liệu thực, không phải cảm tính |
| Pre-demo | Cập nhật thông tin về feedback người dùng và hành vi sửa topic | Giữ ranh giới giữa “gợi ý” và “quyết định cuối cùng” |
```
